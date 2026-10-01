import wave, numpy as np, json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
with wave.open(str(root/'src/source_16k.wav'),'rb') as w:
    sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
hop=int(sr*.05)
r=np.array([np.sqrt(np.mean(x[i:i+hop]**2)+1e-12) for i in range(0,len(x),hop)])
db=20*np.log10(r+1e-9)
print('percentiles', {p:round(float(np.percentile(db,p)),2) for p in [1,5,10,20,50,90]})
for threshold in [-42,-38,-34,-30,-27,-24]:
    low=db<threshold; runs=[]; start=None
    for i,v in enumerate(low):
        if v and start is None:start=i
        if start is not None and (not v or i==len(low)-1):
            end=i if not v else i+1
            if (end-start)*.05>=.25:runs.append((round(start*.05,2),round(end*.05,2),round((end-start)*.05,2)))
            start=None
    print('threshold',threshold,'runs',runs)
