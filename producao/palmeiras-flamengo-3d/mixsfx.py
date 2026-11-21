import json, wave, numpy as np
TL=json.load(open('timeline.json'));K=TL['keys'];S={s['id']:s for s in TL['shots']};SR=44100;END=TL['end']
def load(n):
    w=wave.open(f'sfx/{n}.wav');a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768;return a
L={n:load(n) for n in ['whoosh','pop','kick','roar','crowd','tick','paper','boom']}
out=np.zeros(int((END+1)*SR),dtype=np.float32)
def put(n,t,g=1.0,dur=None):
    a=L[n];
    if dur: 
        k=int(dur*SR);a=np.tile(a,int(np.ceil(k/len(a))))[:k].copy();f=int(.4*SR);a[:f]*=np.linspace(0,1,f);a[-f:]*=np.linspace(1,0,f)
    i=int(t*SR);j=min(len(out),i+len(a));out[i:j]+=a[:j-i]*g
sh=TL['shots'];trans=['whip','zoom','whip','cut']
for i,s in enumerate(sh[:-1]):
    tr=trans[i%4]
    if tr in('whip','zoom'): put('whoosh',s['t1']-0.3,0.55 if tr=='whip' else 0.35)
    elif tr=='cut': put('boom',s['t1'],0.25)
# crowd beds
for sid,g in [('aerial',.18),('exterior',.08),('ledoff',.07),('rivalry',.16),('final21',.2),('final25',.2),('may',.18),('exterior2',.08),('coverEyes',.22)]:
    s=S[sid];put('crowd',s['t0'],g,dur=s['t1']-s['t0'])
# kicks + goals
g21=K['gol21'];put('kick',g21-.42,.9);put('roar',g21+.12,.55)
hit=K['cabeca']+.55;put('kick',K['lima']+.35,.8);put('kick',hit,.7);put('roar',hit+.955,.55)
put('kick',K['rio']-.1,.9);put('roar',K['rio']+.5,.45);put('pop',K['tres']+.25,.35);put('pop',K['tres']+.55,.35);put('roar',K['tres']+.85,.3)
put('roar',S['final25']['t0']+(K['levantou']-S['final25']['t0'])-.3,.35)
put('roar',S['coverEyes']['t0']+.2,.25)
# pops / plaques
for t,g in [(S['faceoff']['t0']+.35,.6),(S['cal36']['t0']+.7,.4),(K['seis'],.6),(K['maior']-.3,.4),(S['scale']['t0']+.85,.5),(S['table3']['t0']+1.4,.55),
            (K['n90'],.45),(K['seisp'],.45),(K['cta'],.6),(K['cta']+.6,.45),(K['rodrigo'],.35),(S['var']['t0']+.4,.35),(S['endcard']['t0']+.9,.35)]:
    put('pop',t,g)
put('paper',S['cal36']['t0']+.25,.6);put('paper',S['cal26']['t0']+.9,.6);put('whoosh',K['depois']-1.0,.4);put('boom',K['depois']-.25,.4)
for k in np.arange(S['clock']['t0']+.9,S['clock']['t1'],.5): put('tick',k,.35)
put('boom',S['table2']['t0']+(K['virou']-S['table2']['t0']),.35)
out=np.clip(out,-1,1);w=wave.open('sfx.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes());w.close();print('ok',len(out)/SR)
