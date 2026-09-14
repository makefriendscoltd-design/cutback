from pathlib import Path
import shutil,json,hashlib,subprocess,sys
repo=Path(__file__).resolve().parents[2];v1=repo/'verification-renders/buyer-meeting-longform-v1';v2=repo/'verification-renders/buyer-meeting-longform-v2'
out=Path.home()/'Downloads/Buyer-Lecture-Windows-v2';out.mkdir(exist_ok=True)
for folder in ['qa','output','source','assets','renders-graphics','graphics']:(out/folder).mkdir(exist_ok=True)
for p in v2.iterdir():
 if p.is_file() and not p.is_symlink() and p.suffix in {'.py','.json','.ass','.srt','.md'}:shutil.copy2(p,out/p.name)
for name in ['assets','graphics']:
 shutil.copytree(v1/name,out/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.log'))
for p in (v1/'renders-graphics').iterdir():
 if p.suffix in {'.mov','.webm'}:shutil.copy2(p,out/'renders-graphics'/p.name)
shutil.copy2(v1/'cut-base.mp4',out/'cut-base.mp4')
shutil.copy2(Path.home()/'Downloads/원본_온라인 오프라인 바이어 미팅 노하우.mp4',out/'source/original.mp4')
for f in ['cut-audio-audit.json','correction-audio-audit.json']:
 shutil.copy2(v1/'qa'/f,out/'qa'/f)
shutil.copy2(v2/'qa/delivery-contact.jpg',out/'qa/reference-contact.jpg')
shutil.copy2(v2/'DELIVERY-VERIFICATION.json',out/'qa/mac-original-verification.json')
(out/'DELIVERY-VERIFICATION.json').unlink()
(out/'works-upload-receipt.json').unlink()
p=out/'assemble.py';s=p.read_text();s=s.replace('import json,subprocess,sys,html,shutil','import json,subprocess,sys,html,shutil,os');s=s.replace("events=[]","os.chdir(r)\n(r/'qa').mkdir(exist_ok=True)\n(r/'output').mkdir(exist_ok=True)\nevents=[]",1);s=s.replace('str(r/\'renders-graphics\'/f\'{e["id"]}.mov\')','str(Path(\'renders-graphics\')/f\'{e["id"]}.mov\')');s=s.replace('subtitles={r/"captions.ass"}:fontsdir={a}','subtitles=captions.ass:fontsdir=assets');s=s.replace("Path('/Users/apple/Downloads/바이어_온라인_오프라인_미팅_롱폼_편집_v2_문장자막.mp4')","r/'output/buyer-lecture-v2.mp4'");p.write_text(s)
p=out/'verify_delivery.py';s=p.read_text().replace("Path('/Users/apple/Downloads/바이어_온라인_오프라인_미팅_롱폼_편집_v2_문장자막.mp4')","r/'output/buyer-lecture-v2.mp4'").replace('../buyer-meeting-longform-v1/qa/','qa/');p.write_text(s)
for name in ['edit-plan.json','caption-style.json']:
 p=out/name;d=json.loads(p.read_text())
 if name=='edit-plan.json':d['source']='source/original.mp4'
 else:d['font_file']='assets/Pretendard-SemiBold.ttf'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for name in ['run.py','setup.ps1','START_HERE.md','AGENTS.md']:
 shutil.copy2(Path(__file__).parent/name,out/name)
(out/'requirements.txt').write_text('Pillow=='+__import__('PIL').__version__+'\nnumpy>=1.26,<3\n')
print(out)
