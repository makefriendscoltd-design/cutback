#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

p=Path(sys.argv[1])
cmd=['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]
data=json.loads(subprocess.check_output(cmd))
video=next(s for s in data['streams'] if s.get('codec_type')=='video')
out={
 'path':str(p),
 'width':video.get('width'),
 'height':video.get('height'),
 'fps':video.get('avg_frame_rate'),
 'duration':float(data['format']['duration']),
 'codec':video.get('codec_name')
}
print(json.dumps(out,ensure_ascii=False,indent=2))
