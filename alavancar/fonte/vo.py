import sys, json, soundfile as sf
from kokoro_onnx import Kokoro
d=sys.argv[1]; k=Kokoro(d+'/../tts/kokoro-v1.0.onnx', d+'/../tts/voices-v1.0.bin')
lines=json.load(open(d+'/roteiro.json')); tot=0
for l in lines:
    s,sr=k.create(l['txt'], voice='pf_dora', speed=1.0, lang='pt-br')
    sf.write(f"{d}/vo/{l['id']}.wav", s, sr); l['dur']=round(len(s)/sr,3); tot+=l['dur']
    print(l['id'], l['dur'])
json.dump(lines, open(d+'/vo/durs.json','w'), ensure_ascii=False, indent=1)
print('total', round(tot,2), 'sr', sr)
