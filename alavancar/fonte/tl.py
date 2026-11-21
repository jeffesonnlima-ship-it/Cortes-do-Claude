import json,sys,re
d=sys.argv[1]; L=json.load(open(d+'/vo/durs.json'))
starts={'s1':0.6,'s2':4.0,'s3':7.0,'s4':14.5,'s5':17.3,'s6':23.4,'s7':30.8,'s8':37.0,'s9':43.6,'s10':47.3,'s11':52.6}
cap={'s1':0,'s2':1,'s3':1,'s4':1,'s5':1,'s6':1,'s7':1,'s8':1,'s9':0,'s10':1,'s11':0}
out={}
for l in L:
    st=starts[l['id']]; words=l['txt'].split()
    w=[len(re.sub(r'\W','',x))+1.5+(3.5 if re.search(r'[.,…:!?]$',x) else 0) for x in words]
    a=st+0.08; b=st+l['dur']-0.12; tot=sum(w); acc=0; wt=[]
    for x in w: wt.append(round(a+(b-a)*acc/tot,3)); acc+=x
    out[l['id']]={'start':st,'dur':l['dur'],'end':round(st+l['dur'],3),'words':words,'wt':wt,'cap':cap[l['id']]}
json.dump(out,open(d+'/timeline.json','w'),ensure_ascii=False)
open(d+'/timeline.js','w').write('window.TL='+json.dumps(out,ensure_ascii=False)+';')
for k,v in out.items(): print(k,v['start'],v['end'])
