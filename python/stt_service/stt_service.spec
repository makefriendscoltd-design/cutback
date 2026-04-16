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

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 용량 절감: torch dev/test 모듈, matplotlib 등 STT 에서 안 쓰는 거 제외
        'torch.test',
        'torch.testing',
        'torch.utils.tensorboard',
        'torch.distributions',
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
