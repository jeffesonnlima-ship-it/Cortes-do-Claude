"""Monta o vídeo completo Vasco 2 x 1 Inter (9:16) com o áudio original da transmissão.

Uso:
    python3 montar_completo.py <video_original.mp4> <pasta_scratch> <saida.mp4>

<pasta_scratch> deve conter: lance_A, quadros (teste do 1º gol), lance_C, lance_D,
lance_E, lance_F (PNGs f_0001.png ...).
"""
import os, subprocess, sys, tempfile

FPS = 12
orig, base, saida = sys.argv[1:4]
tmp = tempfile.mkdtemp()

# (pasta, primeiro quadro, último quadro, trechos de áudio [(ini, fim)] ou None)
BLOCOS = [
    ("lance_A", 1, None, [(11.5, 30.0)]),
    ("quadros", 37, 186, "teste"),          # 1º gol: teste já renderizado, a partir de 3,0 s
    ("lance_C", 1, None, [(99.0, 108.0), (112.6, 118.0)]),
    ("lance_D", 1, None, [(147.6, 166.0), (180.6, 184.4)]),
    ("lance_E", 1, None, [(259.0, 268.3), (271.9, 278.4)]),
    ("lance_F", 1, None, None),             # tela final: apito + torcida sintéticos
]
TESTE_AUDIO = os.path.join(base, "voz", "audio_original_teste.wav")


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


seq = os.path.join(tmp, "seq")
os.makedirs(seq)
n = 0
partes_audio = []
for i, (pasta, q0, q1, audio) in enumerate(BLOCOS):
    d = os.path.join(base, pasta)
    arquivos = sorted(f for f in os.listdir(d) if f.startswith("f_") and f.endswith(".png"))
    nums = [int(f[2:6]) for f in arquivos]
    q1 = q1 or max(nums)
    for q in range(q0, q1 + 1):
        n += 1
        os.symlink(os.path.join(d, f"f_{q:04d}.png"), os.path.join(seq, f"f_{n:04d}.png"))
    dur = (q1 - q0 + 1) / FPS
    wav = os.path.join(tmp, f"a{i}.wav")
    if audio == "teste":
        run(["-ss", "3.0", "-t", f"{dur}", "-i", TESTE_AUDIO, "-af", "aresample=48000",
             "-ac", "2", wav])
    elif audio is None:
        # três apitos (curto, curto, longo) + torcida
        apito = ("sine=f=2900:d={d},volume=0.5[s1];sine=f=3080:d={d},volume=0.5[s2];"
                 "[s1][s2]amix=2,tremolo=f=28:d=0.6")
        filtros = []
        for k, (t0, d_) in enumerate(((0.15, 0.35), (0.75, 0.35), (1.35, 1.1))):
            filtros.append(apito.format(d=d_).replace("[s1]", f"[s1{k}]").replace("[s2]", f"[s2{k}]")
                           + f",afade=t=in:d=0.03,afade=t=out:st={d_-0.08}:d=0.08,adelay={int(t0*1000)}|{int(t0*1000)}[w{k}]")
        torcida = (f"anoisesrc=color=brown:duration={dur}:amplitude=0.7,lowpass=f=900,highpass=f=120,"
                   f"volume=0.35,afade=t=out:st={dur-1.0}:d=1.0[t]")
        fc = ";".join(filtros) + ";" + torcida + ";[w0][w1][w2][t]amix=inputs=4:duration=longest:normalize=0[o]"
        run(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", fc.replace(
            "sine=", "sine=sample_rate=48000:").replace("anoisesrc=", "anoisesrc=sample_rate=48000:"),
             "-map", "[o]", "-t", f"{dur}", "-ac", "2", wav])
    else:
        # trechos do áudio original; emendas com crossfade de 0,3 s
        ins, fc = [], []
        for k, (a, b) in enumerate(audio):
            ins += ["-ss", f"{a}", "-t", f"{b - a}", "-i", orig]
            fc.append(f"[{k}:a]aresample=48000,asetpts=PTS-STARTPTS[p{k}]")
        atual = "p0"
        for k in range(1, len(audio)):
            fc.append(f"[{atual}][p{k}]acrossfade=d=0.3:c1=tri:c2=tri[x{k}]")
            atual = f"x{k}"
        fc.append(f"[{atual}]apad,atrim=0:{dur}[o]")
        run(ins + ["-filter_complex", ";".join(fc), "-map", "[o]", "-ac", "2", wav])
    # micro-fades nas bordas para não estalar no corte
    wav2 = os.path.join(tmp, f"b{i}.wav")
    run(["-i", wav, "-af", f"afade=t=in:d=0.08,afade=t=out:st={dur-0.1:.3f}:d=0.1,atrim=0:{dur}", wav2])
    partes_audio.append(wav2)
    print(f"bloco {pasta}: {q1 - q0 + 1} quadros, {dur:.2f} s")

lista = os.path.join(tmp, "lista.txt")
open(lista, "w").write("".join(f"file '{p}'\n" for p in partes_audio))
audio_total = os.path.join(tmp, "audio_total.wav")
run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", audio_total])
dur_total = n / FPS
print(f"total: {n} quadros, {dur_total:.2f} s")

env = dict(os.environ, TORCIDA="0", NARRACAO_VOL=os.environ.get("NARRACAO_VOL", "2.4"))
aqui = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(aqui, "montar.py"), seq, audio_total, "-", saida, f"{dur_total}"],
               check=True, env=env)
