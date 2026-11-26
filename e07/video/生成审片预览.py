from pathlib import Path
import subprocess,json
import imageio_ffmpeg
root=Path(__file__).parent
versions={'M01':'v01','M02':'v01','M03':'v02','M04':'v01','M05':'v02','M06':'v01'}
paths=[root/f'E07-{name}_raw_candidate_{version}.mp4' for name,version in versions.items()]
missing=[str(p) for p in paths if not p.exists()]
if missing:
    raise SystemExit('仍缺少返工结果：'+', '.join(missing))
listing=root/'审片串联清单.txt'
listing.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in paths))
out=root/'E07_整集串联审片_候选_v02.mp4'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
args=[ffmpeg,'-loglevel','error']
for path in paths:
    args.extend(['-i',str(path)])
filters=[]
for i in range(len(paths)):
    filters.extend([f'[{i}:v]trim=duration=5,setpts=PTS-STARTPTS,fps=24,format=yuv420p[v{i}]',f'[{i}:a]asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration=5[a{i}]'])
filters.append(''.join(f'[v{i}][a{i}]' for i in range(len(paths)))+f'concat=n={len(paths)}:v=1:a=1[v][a]')
args.extend(['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-movflags','+faststart','-y',str(out)])
subprocess.run(args,check=True)
meta=subprocess.run([ffmpeg,'-hide_banner','-i',str(out)],capture_output=True,text=True).stderr
(root/'审片预览技术信息.txt').write_text(meta)
print(out)
print(meta)
