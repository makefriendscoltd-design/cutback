"""
Whisper Wrapper using faster-whisper
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


def _register_cuda_dll_dirs() -> None:
    """
    nvidia-* pip 패키지가 설치한 CUDA DLL 폴더를 Windows DLL 검색 경로에 등록한다.

    ctranslate2 는 cuBLAS 를 런타임에 LoadLibrary 로 찾는데, pip 패키지는
    site-packages/nvidia/<lib>/bin 에 DLL 을 넣을 뿐 PATH 에 추가하지 않는다.
    등록하지 않으면 모델 로드는 성공하고 **추론 시점에** 다음으로 실패한다:
        RuntimeError: Library cublas64_12.dll is not found or cannot be loaded
    """
    if not hasattr(os, "add_dll_directory"):
        return  # non-Windows

    try:
        import nvidia
    except ImportError:
        return

    for base in nvidia.__path__:
        nvidia_root = Path(base)
        for bin_dir in nvidia_root.glob("*/bin"):
            if bin_dir.is_dir():
                try:
                    os.add_dll_directory(str(bin_dir))
                    logger.debug(f"Registered CUDA DLL dir: {bin_dir}")
                except OSError as e:
                    logger.warning(f"Failed to register {bin_dir}: {e}")


class WhisperTranscriber:
    def __init__(self, model_size: str = None, device: str = None):
        """
        Args:
            model_size: 모델 크기 (tiny, base, small, medium, large-v3)
            device: 디바이스 (cpu, cuda, auto)

        환경변수로 오버라이드 가능:
            CUTBACK_STT_MODEL  = medium | small | large-v3 ...
            CUTBACK_STT_DEVICE = auto | cuda | cpu

        한국어 정확도 우선:
        - tiny/base 는 한국어 오타가 많음
        - small (244MB) 정도가 CPU에서 속도/정확도 균형
        - medium/large-v3 는 GPU 또는 긴 대기 가능 시 사용

        주의: faster-whisper 는 ctranslate2 를 사용하므로 torch 가 필요 없다.
        PyInstaller 번들에 torch 를 포함하면 libiomp5md.dll 이 ctranslate2 와
        중복되어 Intel OpenMP 이중 초기화 충돌 (STATUS_STACK_BUFFER_OVERRUN,
        0xc0000409 fast-fail) 이 발생한다. CUDA 지원은 ctranslate2 가 자체 제공.
        """
        # 기본값 small:
        #   실측(31.7초 한국어 음성, CPU) medium 26.5s vs small 8.8s 로 3배 빠르고,
        #   한국어 인식 결과는 띄어쓰기/쉼표 수준의 차이뿐이었다.
        #   30분 영상 기준 medium 약 25분 → small 약 8분.
        #   모델 다운로드도 1.5GB → 244MB 로 줄어 첫 실행 대기가 크게 짧아진다.
        model_size = model_size or os.environ.get("CUTBACK_STT_MODEL", "small")
        device = device or os.environ.get("CUTBACK_STT_DEVICE", "auto")

        logger.info(f"Loading Whisper model: {model_size} (device={device})")

        # Auto device selection
        # torch 를 import 하지 않는다 (OpenMP 충돌 원인).
        # ctranslate2 의 device="auto" 는 CUDA 런타임이 없으면 로드 시점에
        # 예외를 던지므로, 직접 cuda 를 시도하고 실패하면 cpu 로 폴백한다.
        # 롱폼(30분+)에서 CPU int8 은 실시간보다 느려 사실상 사용 불가이므로
        # GPU 를 쓸 수 있으면 반드시 쓴다.
        candidates = (
            [("cuda", "float16"), ("cpu", "int8")]
            if device == "auto"
            else [(device, "float16" if device == "cuda" else "int8")]
        )

        _register_cuda_dll_dirs()

        last_error = None
        for dev, compute_type in candidates:
            try:
                model = WhisperModel(
                    model_size,
                    device=dev,
                    compute_type=compute_type,
                )

                # 모델 로드 성공만으로 디바이스를 확정하면 안 된다.
                # CUDA 는 로드까지는 통과해놓고 첫 추론에서 cuBLAS 를 못 찾아
                # 터지는 경우가 있다. 그러면 파이프라인이 빈 자막을 받아
                # "무음 컷은 됐는데 자막이 없는" 결과가 조용히 나간다.
                # 실제로 1초짜리 더미를 돌려보고 통과한 디바이스만 채택한다.
                self._smoke_test(model)

                self.model = model
                self.device = dev
                self.model_size = model_size
                logger.info(
                    f"Whisper model ready "
                    f"(device={dev}, compute_type={compute_type})"
                )
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Whisper unusable on {dev}/{compute_type}: "
                    f"{type(e).__name__}: {e}"
                )

        raise RuntimeError(
            f"Whisper 모델을 사용할 수 있는 디바이스가 없습니다 "
            f"(model={model_size}): {last_error}"
        )

    @staticmethod
    def _smoke_test(model: WhisperModel) -> None:
        """1초 무음으로 실제 추론 경로를 한 번 통과시켜 본다."""
        import numpy as np

        segments, _ = model.transcribe(
            np.zeros(16000, dtype=np.float32),
            language="ko",
            vad_filter=False,
            beam_size=1,
        )
        # generator 이므로 소비해야 실제로 encode 가 돈다
        for _ in segments:
            break

    @staticmethod
    def _load_audio(audio_path: str):
        """
        16kHz mono PCM WAV → float32 numpy 배열.

        faster-whisper 에 경로를 넘기면 내부적으로 PyAV 로 디코딩하는데,
        PyAV 는 번들에 65MB 를 더한다. 파이프라인이 ffmpeg 로 항상
        16kHz mono PCM WAV 를 뽑아주므로 표준 wave 모듈로 충분하다.
        """
        import wave
        import numpy as np

        with wave.open(audio_path, "rb") as wf:
            channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

        if sample_width != 2:
            raise ValueError(
                f"16-bit PCM WAV 만 지원합니다 (sample_width={sample_width})"
            )

        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)

        # Whisper 는 16kHz 를 전제한다. 파이프라인은 항상 16kHz 로 뽑지만
        # 다른 경로로 들어온 WAV 도 조용히 어긋나지 않도록 맞춰준다.
        if sample_rate != 16000:
            target_len = int(round(len(audio) * 16000 / sample_rate))
            audio = np.interp(
                np.linspace(0, len(audio) - 1, target_len, dtype=np.float32),
                np.arange(len(audio), dtype=np.float32),
                audio,
            ).astype(np.float32)
            logger.info(f"Resampled audio {sample_rate}Hz → 16000Hz")

        return audio

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
            "쉼표와 마침표 같은 문장 부호를 사용합니다. "
            "음, 어, 저, 그, 뭐, 약간, 좀 같은 추임새와 말버릇도 모두 그대로 받아 적습니다."
            if language == "ko"
            else None
        )

        segments, info = self.model.transcribe(
            self._load_audio(audio_path),
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
