"""
Whisper STT Service (ZeroMQ Server)
faster-whisper를 사용하여 음성 인식 수행
"""

import zmq
import json
import logging
from pathlib import Path
from typing import Dict, Any
from whisper_wrapper import WhisperTranscriber
from spell_checker import KoreanSpellChecker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class STTService:
    def __init__(self, port: int = 5555):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        # 이전 프로세스가 남긴 소켓 재사용 허용
        self.socket.setsockopt(zmq.LINGER, 0)
        self.transcriber = WhisperTranscriber()
        self.spell_checker = KoreanSpellChecker()

    def _kill_existing_on_port(self):
        """포트를 점유하고 있는 기존 프로세스 종료"""
        import subprocess
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if f'127.0.0.1:{self.port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    logger.warning(f"Killing existing process on port {self.port} (PID: {pid})")
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, timeout=5)
                    import time
                    time.sleep(1)
                    return True
        except Exception as e:
            logger.warning(f"Failed to kill existing process: {e}")
        return False

    def start(self):
        """서비스 시작"""
        try:
            self.socket.bind(f"tcp://127.0.0.1:{self.port}")
        except zmq.error.ZMQError as e:
            if "Address in use" in str(e):
                logger.warning(f"Port {self.port} in use, trying to reclaim...")
                self._kill_existing_on_port()
                # 소켓 재생성 후 재시도
                self.socket.close()
                self.socket = self.context.socket(zmq.REP)
                self.socket.setsockopt(zmq.LINGER, 0)
                self.socket.bind(f"tcp://127.0.0.1:{self.port}")
            else:
                raise
        logger.info(f"STT Service started on port {self.port}")

        while True:
            try:
                # 요청 수신
                message = self.socket.recv_string()
                request = json.loads(message)

                logger.info(f"Received request: {request['action']}")

                # 요청 처리
                response = self.handle_request(request)

                # 응답 전송
                self.socket.send_string(json.dumps(response))

            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                error_response = {
                    "success": False,
                    "error": str(e)
                }
                self.socket.send_string(json.dumps(error_response))

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """요청 처리"""
        action = request.get('action')

        if action == 'transcribe':
            return self.transcribe(request['payload'])
        elif action == 'spell_check':
            return self.spell_check(request['payload'])
        elif action == 'health':
            return {
                "success": True,
                "status": "healthy",
                "spell_check_available": self.spell_checker.available,
            }
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def spell_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """자막 텍스트 한국어 맞춤법 교정 (배치)"""
        try:
            texts = payload.get('texts', [])
            if not isinstance(texts, list):
                return {"success": False, "error": "texts must be a list"}
            corrected = self.spell_checker.check_batch(texts)
            return {
                "success": True,
                "corrected": corrected,
                "available": self.spell_checker.available,
            }
        except Exception as e:
            logger.error(f"Spell check error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def transcribe(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """음성 인식 수행"""
        try:
            audio_path = payload['audio_path']
            language = payload.get('language', 'ko')
            word_timestamps = payload.get('word_timestamps', True)

            logger.info(f"Transcribing: {audio_path}")

            # Whisper로 transcribe
            transcript = self.transcriber.transcribe(
                audio_path=audio_path,
                language=language,
                word_timestamps=word_timestamps
            )

            return {
                "success": True,
                "transcript": transcript
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def stop(self):
        """서비스 종료"""
        self.socket.close()
        self.context.term()
        logger.info("STT Service stopped")


if __name__ == "__main__":
    service = STTService()
    try:
        service.start()
    finally:
        service.stop()
