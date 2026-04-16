"""
Whisper Wrapper using faster-whisper
"""

import logging
from typing import Dict, Any, List
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    def __init__(self, model_size: str = "small", device: str = "auto"):
        """
        Args:
            model_size: 모델 크기 (tiny, base, small, medium, large-v3)
            device: 디바이스 (cpu, cuda, auto)

        한국어 정확도 우선:
        - tiny/base 는 한국어 오타가 많음
        - small (244MB) 정도가 CPU에서 속도/정확도 균형
        - medium/large-v3 는 GPU 또는 긴 대기 가능 시 사용
        """
        logger.info(f"Loading Whisper model: {model_size}")

        # Auto device selection
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

        logger.info(f"Using device: {device}")

        # 모델 로드 (메모리에 상주)
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type="float16" if device == "cuda" else "int8"
        )

        logger.info("Whisper model loaded successfully")

    def transcribe(
        self,
        audio_path: str,
        language: str = "ko",
        word_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        음성 인식 수행

        Returns:
            {
                "words": [{"text": "안녕", "start": 0.0, "end": 0.5, "confidence": 0.99}, ...],
                "full_text": "안녕하세요",
                "language": "ko",
                "duration": 10.5
            }
        """
        # 한국어 STT 정확도 향상을 위한 튜닝:
        # - beam_size=5: greedy(1)보다 정확도 향상
        # - condition_on_previous_text=False: 한국어 환각/반복 줄임
        # - initial_prompt: 한국어 표기/구두점 힌트
        # - temperature=0.0: 결정적 출력
        # - no_speech_threshold=0.5: 무음 오인식 줄임
        # - vad min_silence_duration_ms=300: VAD 가 단어를 잘라내는 문제 완화
        initial_prompt = (
            "다음은 한국어 영상의 음성을 정확한 맞춤법과 띄어쓰기로 받아 적은 것입니다. "
            "쉼표와 마침표 같은 문장 부호를 사용합니다."
            if language == "ko"
            else None
        )

        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            word_timestamps=word_timestamps,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=False,
            no_speech_threshold=0.5,
            initial_prompt=initial_prompt,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=300,
                speech_pad_ms=200,
            )
        )

        # 결과 수집
        words_list: List[Dict[str, Any]] = []
        full_text_parts: List[str] = []

        for segment in segments:
            if word_timestamps and hasattr(segment, 'words'):
                for word in segment.words:
                    words_list.append({
                        "text": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "confidence": word.probability
                    })

            full_text_parts.append(segment.text.strip())

        # 결과 구성
        result = {
            "words": words_list,
            "full_text": " ".join(full_text_parts),
            "language": info.language,
            "duration": info.duration
        }

        logger.info(f"Transcription completed: {len(words_list)} words, {info.duration:.2f}s")

        return result
