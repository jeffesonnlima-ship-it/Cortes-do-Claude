set -e
cd "$(dirname "$0")"
printf "file 'chunks/c0.mp4'\nfile 'chunks/c1.mp4'\nfile 'chunks/c2.mp4'\nfile 'chunks/c3.mp4'\n" > chunks.txt
ffmpeg -v error -y -f concat -safe 0 -i chunks.txt -c copy base720.mp4
ffmpeg -v error -y -i base720.mp4 -i ../narr.mp3 -i sfx.wav -filter_complex \
"[0:v]scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,subtitles=caps.ass:fontsdir=/root/.fonts[v];\
[1:a]loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=1[n];[2:a]aresample=44100,volume=0.9[s];\
[n][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]" \
-map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 24 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -shortest -movflags +faststart final3d.mp4
ffprobe -v error -show_entries format=duration:stream=width,height -of compact final3d.mp4; ls -la final3d.mp4
