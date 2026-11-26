from pathlib import Path
import json, re, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw

root=Path(__file__).parent
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
results=[]
previous=root/'视频技术检查.json'
cached={r['file']:r for r in json.loads(previous.read_text())} if previous.exists() else {}
for video in sorted(root.glob('E07-M??_raw_candidate_v*.mp4')):
    if video.name in cached and Path(cached[video.name]['contact']).exists():
        results.append(cached[video.name])
        continue
    output=root/'质检抽帧'/video.stem
    output.mkdir(parents=True,exist_ok=True)
    meta=subprocess.run([ffmpeg,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
    match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',meta)
    duration=sum(float(x)*m for x,m in zip(match.groups(),[3600,60,1])) if match else None
    timestamps=[0,1,2,3,4,4.95]
    frames=[]
    for index,t in enumerate(timestamps):
        frame=output/f'{index:02d}_{t:.2f}s.jpg'
        subprocess.run([ffmpeg,'-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2','-y',str(frame)],check=True)
        frames.append(frame)
    first=Image.open(frames[0])
    width,height=first.size
    contact=Image.new('RGB',(1080,680),(24,28,36))
    draw=ImageDraw.Draw(contact)
    for i,(frame,t) in enumerate(zip(frames,timestamps)):
        thumb=Image.open(frame).resize((180,320))
        x=(i%3)*360+90;y=(i//3)*340+18
        contact.paste(thumb,(x,y))
        draw.text((x,y-16),f'{t:.2f}s',fill=(240,240,240))
    contact_path=output/'时序检查.jpg'
    contact.save(contact_path,quality=92)
    results.append({'file':video.name,'duration_seconds':duration,'width':width,'height':height,'has_audio':'Audio:' in meta,'frames':[str(f) for f in frames],'contact':str(contact_path),'metadata':meta})
out=root/'视频技术检查.json'
out.write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in r.items() if k not in ['metadata','frames']} for r in results],ensure_ascii=False))
