import json, re, difflib, sys, subprocess
WORDS=sys.argv[1] if len(sys.argv)>1 else '../words.json'
AUDIO_END=float(sys.argv[2]) if len(sys.argv)>2 else 145.63
W=json.load(open(WORDS)); SCRIPT=open('script.txt').read(); stoks=SCRIPT.split()
def norm(x): return re.sub(r'[^\wà-úç0-9]','',x.lower())
wt=[norm(w[2]) for w in W]; st=[norm(w) for w in stoks]
sm=difflib.SequenceMatcher(None,st,wt,autojunk=False); times=[None]*len(stoks)
for b in sm.get_matching_blocks():
    for k in range(b.size): times[b.a+k]=(W[b.b+k][0],W[b.b+k][1])
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag in('replace','delete') and i2>i1:
        if j2>j1: s0,e0=W[j1][0],W[j2-1][1]
        else: s0=times[i1-1][1] if i1>0 and times[i1-1] else 0; e0=s0+0.3*(i2-i1)
        for k in range(i1,i2): times[k]=(s0+(e0-s0)*(k-i1)/(i2-i1), s0+(e0-s0)*(k-i1+1)/(i2-i1))
def find(ph,after=0):
    p=[norm(x) for x in ph.split()]
    for i in range(after,len(st)-len(p)+1):
        if st[i:i+len(p)]==p: return i
    raise Exception('nf '+ph)
def T(ph): return round(times[find(ph)][0],3)
END=round(AUDIO_END+0.6,3)
shots=[('aerial',0.0),('exterior','dentro da casa'),('trophy','Basta um empate.'),('faceoff','Festa rubro-negra'),('ledoff','Fica até o final,'),
('cal36','Faltam três rodadas.'),('table1','O Flamengo chega líder,'),('chalkIf','Pra continuar vivo,'),('rivalry','E isso não é'),('final21','Em 2021,'),
('final25','Em 2025,'),('scale','Uma pra cada lado.'),('cal26','Só que em 2026'),('may','Em maio, no Maracanã,'),('sadfan','Era esse o jogo'),
('table2','Desde então,'),('referee','No apito, hoje,'),('var','No VAR,'),('exterior2','E o palco'),('chalkFla','Quem acha que o Flamengo'),
('chalkPal','Quem acha que o Palmeiras'),('covered','E tem um detalhe.'),('table3','A diferença cai'),('coverEyes','Ou seja:'),('flaHappy','Pra uma torcida,'),
('palSmug','Pra outra,'),('clock','Quatro e meia da tarde. Noventa'),('endcard','E pior que')]
out=[]
for i,(sid,a) in enumerate(shots):
    t0=a if isinstance(a,float) else T(a); out.append({'id':sid,'t0':t0})
for i,s in enumerate(out): s['t1']=out[i+1]['t0'] if i+1<len(out) else END
keys={k:T(v) for k,v in {'prorrog':'Prorrogação,','erro':'erro na saída','gol21':'gol do Deyverson.','camp21':'Palmeiras campeão. Em','lima':'agora em Lima.',
'cabeca':'Gol de cabeça','umazero':'1 a 0,','levantou':'quem levantou','tres':'e fez três a zero.','rio':'foi até o Rio','virou':'virou a tabela.',
'mais6':'Seis pontos de vantagem.','empatar':'Só precisa empatar.','ultima':'E foi o Flamengo que','casa':'Joga em casa,','torcida':'com a torcida.',
'x3':'E o último confronto','depois':'Só fica pra depois.','mesmo':'Mesmo que o Palmeiras','duas':'duas rodadas','p79':'com 79 pontos.','p73':'com 73.',
'seis':'Seis de diferença.','palvence':'o Palmeiras precisa ganhar.','qualquer':'Qualquer outra coisa,','vairio':'vai pro Rio.','rodrigo':'o pernambucano Rodrigo',
'cta':'Comenta aí','palpite':'o palpite é seu.','n90':'Noventa minutos.','seisp':'Seis pontos. E pior','maior':'da maior rivalidade','festa':'Flamengo campeão hoje, ou'}.items()}
json.dump({'shots':out,'keys':keys,'end':END},open('timeline.json','w'),indent=1)
# captions
chunks=[];cur=[]
for i,w in enumerate(stoks):
    if cur and len(' '.join(stoks[k] for k in cur+[i]))>16: chunks.append(cur);cur=[]
    cur.append(i)
    if re.search(r'[.,?!:…]$',w) or len(cur)>=3: chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ec=[s for s in out if s['id']=='endcard'][0]['t0']
ev=[]
for ci,c in enumerate(chunks):
    s=times[c[0]][0]; e=times[chunks[ci+1][0]][0] if ci+1<len(chunks) else END
    e=min(e,times[c[-1]][1]+0.6); txt=' '.join(stoks[k] for k in c)
    pos='\\pos(540,1745)' if s>=ec-0.05 else '\\pos(540,1420)'
    ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{{pos}\\fscx70\\fscy70\\t(0,90,\\fscx106\\fscy106)\\t(90,160,\\fscx100\\fscy100)}}{txt}")
open('caps.ass','w').write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,NunitoCap,82,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,1,0,1,6,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+'\n'.join(ev)+'\n')
print(json.dumps(out)); print(keys)
