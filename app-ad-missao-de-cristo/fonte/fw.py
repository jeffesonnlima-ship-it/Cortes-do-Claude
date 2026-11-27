import sys,json
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
import soundfile as sf
a,_=sf.read(sys.argv[1],dtype='float32')
segs,_=m.transcribe(a,language='pt',word_timestamps=True,beam_size=5)
W=[]
for s in segs:
    for w in s.words: W.append((round(w.start,2),round(w.end,2),w.word.strip()))
json.dump(W,open(sys.argv[2],'w'),ensure_ascii=False)
print(' '.join(f"{w}@{a}" for a,b,w in W))
