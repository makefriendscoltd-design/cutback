"""
VAD (Voice Activity Detection) Service
Silero VAD를 사용하여 음성 구간 탐지
"""

import zmq
import json
import logging
import torch
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class VADService:
    def __init__(self, port: int = 5556):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.model = None
        self.utils = None
        self._load_model()

    def _load_model(self):
        """Silero VAD 모델 로드"""
        logger.info("Loading Silero VAD model...")
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=True
        )
        logger.info("Silero VAD model loaded")

    def start(self):
        """서비스 시작"""
        self.socket.bind(f"tcp://127.0.0.1:{self.port}")
        logger.info(f"VAD Service started on port {self.port}")

        while True:
            try:
                message = self.socket.recv_string()
                request = json.loads(message)
                logger.info(f"Received request: {request.get('action')}")

                response = self.handle_request(request)
                self.socket.send_string(json.dumps(response))

            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                self.socket.send_string(json.dumps({
                    "success": False,
                    "error": str(e)
                }))

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get('action')

        if action == 'detect_speech':
            return self.detect_speech(request['payload'])
        elif action == 'health':
            return {"success": True, "status": "healthy"}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def detect_speech(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """음성 구간 탐지"""
        try:
            audio_path = payload['audio_path']
            (get_speech_timestamps, _, read_audio, _, _) = self.utils

            wav = read_audio(audio_path, sampling_rate=16000)
            speech_timestamps = get_speech_timestamps(
                wav,
                self.model,
                sampling_rate=16000,
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=300,
            )

            results = []
            for ts in speech_timestamps:
                start_sec = ts['start'] / 16000
                end_sec = ts['end'] / 16000
                results.append({
                    "timestamp": start_sec,
                    "duration": end_sec - start_sec,
                    "is_speech": True,
                    "confidence": 0.9
                })

            logger.info(f"Detected {len(results)} speech segments")
            return {"success": True, "results": results}

        except Exception as e:
            logger.error(f"VAD error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def stop(self):
        self.socket.close()
        self.context.term()
        logger.info("VAD Service stopped")


if __name__ == "__main__":
    service = VADService()
    try:
        service.start()
    finally:
        service.stop()
