# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Cutback STT service.

scripts/build-python-exe.js 가 venv 안 PyInstaller 로 이 spec 을 실행한다.
출력:  python/stt_service/dist/cutback-stt/cutback-stt.exe
"""
import sys
from pathlib import Path

block_cipher = None

# faster-whisper / onnxruntime / torch 가 동적 import 되는 모듈을 모두 수집
hidden_imports = [
    'faster_whisper',
    'faster_whisper.transcribe',
    'faster_whisper.tokenizer',
    'faster_whisper.feature_extractor',
    'faster_whisper.audio',
    'ctranslate2',
    'onnxruntime',
    'zmq',
    'zmq.backend.cython',
    'requests',
    'tokenizers',
]

# ctranslate2 는 cuDNN/cuBLAS DLL 을 런타임에 동적으로 로드하므로
# PyInstaller 의 의존성 스캔이 따라가지 못한다. 명시적으로 수집한다.
# 빠지면 GPU 가 있는 PC 에서도 CUDA 추론이 실패해 CPU 로 폴백된다.
_ct2_dir = Path('venv') / 'Lib' / 'site-packages' / 'ctranslate2'
ct2_binaries = [
    (str(dll), 'ctranslate2') for dll in _ct2_dir.glob('*.dll')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=ct2_binaries,
    datas=[
        # faster_whisper VAD 모델 파일 (silero_vad_v6.onnx) 포함
        (str(Path('venv') / 'Lib' / 'site-packages' / 'faster_whisper' / 'assets'), 'faster_whisper/assets'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # torch 완전 제외:
        #   faster-whisper 는 ctranslate2 를 쓰므로 torch 불필요.
        #   torch/lib/libiomp5md.dll 과 ctranslate2/libiomp5md.dll 이 동시에
        #   로드되면 Intel OpenMP 이중 초기화 → 0xc0000409 (fast-fail) 로 크래시.
        'torch',
        # ⚠️ av(PyAV)는 제외하면 안 된다.
        #   faster_whisper/audio.py 가 *import 시점*에 `import av` 를 하므로
        #   (런타임에 안 쓰더라도) 빼면 `from faster_whisper import WhisperModel`
        #   자체가 ModuleNotFoundError 로 터져 cutback-stt.exe 가 시작조차 못 한다.
        #   실제로 v0.1.6~0.1.9 에서 "음성 인식 실패" 의 원인이었다.
        #   (예전엔 whisper_wrapper._load_audio 가 WAV 를 직접 읽으니 av 가 실행
        #    경로에 없다고 판단해 제외했으나, import 단계에서 필요하다는 걸 놓쳤다.)
        # HuggingFace 고속 전송 가속기 (약 8MB). 모델 다운로드는 일반 HTTP 로도 된다.
        'hf_xet',
        # CUDA 런타임 pip 패키지 (약 730MB).
        #   ctranslate2 가 cuBLAS 를 못 찾아 CUDA 추론이 실패하는데,
        #   번들해봐야 용량만 폭증하므로 CPU 경로만 싣는다.
        'nvidia',
        # 기타 불필요한 거
        'matplotlib',
        'tkinter',
        'IPython',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cutback-stt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,         # UPX 압축은 onnxruntime/torch 와 충돌 가능 → off
    console=True,      # stdout/stderr 가 Electron 으로 파이프되어야 하므로 console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='cutback-stt',
)
