import json,sys,re,numpy as np,soundfile as sf
d=sys.argv[1]; TL=json.load(open(d+'/timeline.json'))
for k,l in TL.items():
    a,sr=sf.read(f'{d}/vo/{k}.wav'); h=int(sr*0.01)
    e=np.array([np.sqrt(np.mean(a[i:i+h]**2)) for i in range(0,len(a)-h,h)])
    on=e>max(e)*0.06
    # voiced chunks separated by gaps >=0.14s
    ch=[];i=0;n=len(on)
    while i<n:
        if on[i]:
            j=i
            while j<n and (on[j] or (j+14<n and on[j:j+14].any())): j+=1
            ch.append((i*0.01,j*0.01)); i=j
        else: i+=1
    segs=[];cur=[]
    for wi,w in enumerate(l['words']):
        cur.append(wi)
        if re.search(r'[.,…!?:]$',w): segs.append(cur);cur=[]
    if cur: segs.append(cur)
    ok=len(ch)==len(segs)
    print(k,'chunks',len(ch),'segs',len(segs),'OK' if ok else 'fallback')
    if ok:
        for (c0,c1),sg in zip(ch,segs):
            wts=[len(re.sub(r'\W','',l['words'][i]))+1.5 for i in sg]; tot=sum(wts); acc=0
            for i,wv in zip(sg,wts): l['wt'][i]=round(l['start']+c0+(c1-c0)*acc/tot,3); acc+=wv
json.dump(TL,open(d+'/timeline.json','w'),ensure_ascii=False)
open(d+'/timeline.js','w').write('window.TL='+json.dumps(TL,ensure_ascii=False)+';')
for k,v in TL.items(): print(k,[f"{w}:{t}" for w,t in zip(v['words'],v['wt'])])
