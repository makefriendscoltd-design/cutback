$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -3 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 or newer with the py launcher first.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& .\.venv\Scripts\python.exe -X utf8 run.py check
if ($LASTEXITCODE -ne 0) { throw 'Check failed. Resolve the reported dependency before rendering.' }
