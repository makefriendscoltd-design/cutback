from pathlib import Path
import json,hashlib,zipfile
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

r=Path.home()/'Downloads/Buyer-Lecture-Windows-v2'
(r/'README.md').write_text('# Buyer Lecture Windows v2\n\nRead START_HERE.md first. This is a self-contained media handoff, not a native CapCut project.\n',encoding='utf-8')
d={'status':'PARTIAL','mac_portable_preview':'PASS: 15 seconds rendered from bundled dependencies and actual frame inspected','dependency_check':'PASS on packaging Mac','windows_runtime':'NOT RUN: no access to employee Windows PC','next_command':'.\\.venv\\Scripts\\python.exe -X utf8 run.py preview','source_commit':'999f60c','full_original_validation':'qa/mac-original-verification.json'}
(r/'MIGRATION-VERIFICATION.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
files=[p for p in r.rglob('*') if p.is_file() and p.name!='SHA256.json' and '__pycache__' not in p.parts]
assert not any(p.is_symlink() for p in r.rglob('*'))
manifest={p.relative_to(r).as_posix():digest(p) for p in files}
(r/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
z=r.with_suffix('.zip')
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as archive:
 for p in [*files,r/'SHA256.json']:archive.write(p,Path(r.name)/p.relative_to(r))
with zipfile.ZipFile(z) as archive:assert archive.testzip() is None
print(json.dumps({'zip':str(z),'bytes':z.stat().st_size,'files':len(files)+1,'zip_crc':'PASS'}))
