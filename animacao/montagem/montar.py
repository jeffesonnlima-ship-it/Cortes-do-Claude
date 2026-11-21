"""Monta o vídeo final: quadros (12 fps) -> 1080x1920 30 fps + legendas + narração + torcida.

Uso: python3 montar.py <pasta_quadros> <narracao.wav> <legendas.tsv|-> <saida.mp4> [duracao]

Passe "-" no lugar das legendas para montar sem legenda.
"""
import os, subprocess, sys, tempfile

quadros, narracao, legendas, saida = sys.argv[1:5]
dur = float(sys.argv[5]) if len(sys.argv) > 5 else 15.5
FONTE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
tmp = tempfile.mkdtemp()

filtros = ["scale=1080:1920:flags=lanczos", "fps=30"]
linhas = [] if legendas == "-" else open(legendas, encoding="utf-8")
for i, linha in enumerate(linhas):
    if not linha.strip():
        continue
    a, b, txt = linha.rstrip("\n").split("\t")
    arq = os.path.join(tmp, f"l{i}.txt")
    open(arq, "w", encoding="utf-8").write(txt)
    filtros.append(
        f"drawtext=fontfile={FONTE}:textfile={arq}:fontsize=86:fontcolor=white:"
        f"borderw=8:bordercolor=black:shadowx=0:shadowy=6:shadowcolor=black@0.5:"
        f"x=(w-text_w)/2:y=h*0.66:enable='between(t,{a},{b})'")
filtros.append(
    f"drawtext=fontfile={FONTE}:text='@cortesdoclaude':fontsize=30:fontcolor=white@0.55:"
    f"x=(w-text_w)/2:y=h*0.93")

# torcida: ruído marrom filtrado, com crescimento no gol (~10 s)
torcida = (f"anoisesrc=color=brown:duration={dur}:amplitude=0.6,lowpass=f=900,highpass=f=120,"
           f"volume='0.10+0.22*between(t,9.9,12.6)':eval=frame,afade=t=in:d=0.6,"
           f"afade=t=out:st={dur-0.8}:d=0.8")
cmd = ["ffmpeg", "-v", "error", "-y",
       "-framerate", "12", "-i", os.path.join(quadros, "f_%04d.png"),
       "-i", narracao,
       "-f", "lavfi", "-i", torcida,
       "-filter_complex",
       f"[0:v]{','.join(filtros)}[v];"
       f"[1:a]aresample=48000,volume=1.6,apad[n];[2:a]aresample=48000[t];"
       f"[n][t]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89,atrim=0:{dur}[a]",
       "-map", "[v]", "-map", "[a]", "-t", str(dur),
       "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]
subprocess.run(cmd, check=True)
print("ok", saida)
