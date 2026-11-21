import numpy as np, wave, json, sys, re
d=sys.argv[1]; SR=44100; D=30.0; N=int(SR*D)
TL=json.load(open(d+'/timeline.json'))
def W(i,k):
    l=TL[i]
    if isinstance(k,int): return l['wt'][k]
    for j,w in enumerate(l['words']):
        if re.sub(r'[^a-zà-ú]','',w.lower()).startswith(k): return l['wt'][j]
    raise Exception(k)
M=np.zeros((N,2)); X=np.zeros((N,2)); V=np.zeros(N)
rng=np.random.default_rng(3)
def tt(dur): return np.arange(int(dur*SR))/SR
def put(buf,sig,t0,g=1.0,pan=0.0):
    i=int(t0*SR)
    if i<0: sig=sig[-i:]; i=0
    n=min(len(sig),N-i)
    if n<=0: return
    pan=np.broadcast_to(pan,(len(sig),))[:n]
    buf[i:i+n,0]+=sig[:n]*g*np.sqrt((1-pan)/2); buf[i:i+n,1]+=sig[:n]*g*np.sqrt((1+pan)/2)
def lp(x,cut):
    cut=np.broadcast_to(cut,x.shape); a=1-np.exp(-2*np.pi*cut/SR); y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def kick(dur=0.4,f0=120,f1=42):
    t=tt(dur); f=f1+(f0-f1)*np.exp(-t*28); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*8)+0.25*rng.standard_normal(len(t))*np.exp(-t*300)
def hat(dur=0.05,dec=90):
    t=tt(dur); n=rng.standard_normal(len(t)); return (n-lp(n,7000))*np.exp(-t*dec)
def clap():
    t=tt(0.22); n=rng.standard_normal(len(t)); return (lp(n,3500)-lp(n,800))*np.exp(-t*22)*1.6
def whoosh(dur,c0,c1,p0=-.7,p1=.7):
    t=tt(dur); x=t/dur; n=rng.standard_normal(len(t)); c=c0*(c1/c0)**x
    return (lp(n,c)-lp(n,c*0.25))*np.sin(np.pi*x)**2*2.4, p0+(p1-p0)*x
def pop(f0=900,f1=280,dur=0.12):
    t=tt(dur); f=f1+(f0-f1)*np.exp(-t*60); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def tick(f=2200,dec=160):
    t=tt(0.04); return np.sin(2*np.pi*f*t)*np.exp(-t*dec)
def bell(freqs,step=0.06,dur=1.3,dec=4.0):
    out=np.zeros(int((dur+step*len(freqs))*SR))
    for k,f in enumerate(freqs):
        t=tt(dur); s=(np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2.01*f*t)+0.1*np.sin(2*np.pi*3*f*t))*np.exp(-t*dec)
        i=int(k*step*SR); out[i:i+len(s)]+=s
    return out/len(freqs)*2
def impact(dur=1.4,sub=1.2):
    t=tt(dur); f=32+80*np.exp(-t*10)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.8)*sub+lp(rng.standard_normal(len(t)),2200)*np.exp(-t*9)*0.9
def thud():
    t=tt(0.35); f=70+140*np.exp(-t*40); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)+lp(rng.standard_normal(len(t)),1200)*np.exp(-t*40)*0.8
def riser(dur,f0=180,f1=1400):
    t=tt(dur); x=t/dur; f=f0*(f1/f0)**x
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*0.35+lp(rng.standard_normal(len(t)),400+8000*x**2)*0.9)*x**2
def fall(dur=0.3,f0=1800,f1=300):
    t=tt(dur); x=t/dur; f=f0*(f1/f0)**x; return np.sin(2*np.pi*np.cumsum(f)/SR)*0.5*(1-x*0.3)
def sad():
    t=tt(0.7); f=330*np.exp(-t*0.9); return (np.sin(2*np.pi*np.cumsum(f)/SR)+0.3*np.sin(4*np.pi*np.cumsum(f)/SR))*np.exp(-t*3)*np.minimum(1,t/0.02)
def pluck(f,dur=0.35):
    t=tt(dur); s=np.sign(np.sin(2*np.pi*f*t))*0.5+np.sin(2*np.pi*f*t); return lp(s*np.exp(-t*9),2500)
def padc(freqs,dur,att=0.4,rel=0.8,bright=0.25):
    t=tt(dur); s=np.zeros(len(t))
    for f in freqs:
        for det in (-0.7,0.7): s+=np.sin(2*np.pi*(f+det)*t)+bright*np.sin(2*np.pi*2*(f+det)*t)
    return s/len(freqs)*np.minimum(1,t/att)*np.clip((dur-t)/rel,0,1)*0.3
def bassn(f,dur):
    t=tt(dur); return (np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t))*np.minimum(1,t/0.01)*np.exp(-t*2.5)
nt=lambda m:440*2**((m-69)/12)
def choir(freqs,dur,att=0.8,rel=1.2):
    t=tt(dur); s=np.zeros(len(t))
    for f in freqs:
        for det,ph in ((-1.2,0),(0,1.3),(1.1,2.1)):
            vib=1+0.004*np.sin(2*np.pi*5.2*t+ph)
            ph_=2*np.pi*np.cumsum((f+det)*vib)/SR
            s+=np.sin(ph_)+0.45*np.sin(2*ph_)+0.25*np.sin(3*ph_)+0.12*np.sin(4*ph_)
    s=lp(s,2600)
    return s/len(freqs)/3*np.minimum(1,t/att)*np.clip((dur-t)/rel,0,1)*0.45
def piano(f,dur=2.0):
    t=tt(dur); s=sum(np.sin(2*np.pi*f*k*t)*np.exp(-t*(2+k*1.5))/k for k in range(1,6))
    return s*np.minimum(1,t/0.004)*0.6
def tom(f=90,dur=0.7):
    t=tt(dur); fr=f*(1+0.6*np.exp(-t*25)); return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*5)+lp(rng.standard_normal(len(t)),900)*np.exp(-t*30)*0.6
def boom(): return impact(2.2,1.4)
# ---------- MUSIC ----------
# 0-4.6 dark drone + heartbeat
put(M,padc([nt(38),nt(45),nt(50)],4.9,1.5,0.6,0.1),0,0.7)
for k_,tb in enumerate([0.4,1.6,2.8]): put(M,kick(0.5,70,35),tb,0.45); put(M,kick(0.4,70,35),tb+0.28,0.25)
put(M,bell([1174.7,1760,2349.3],0.12,2.5,1.6),2.65,0.35)
put(M,riser(1.4,150,1800),3.2,0.45)
# 4.6-16.65 D Bm G A, piano arps, building
prog=[[50,54,57],[47,50,54],[43,47,50],[45,49,52]]
b=0.75; t0=4.6; k=0
while t0+k*b<16.6:
    tb=t0+k*b; bar=(k//4)%4; ch=prog[bar]; beat=k%4
    if beat==0:
        put(M,padc([nt(m+12) for m in ch],b*4+0.3,0.5,0.6,0.2),tb,0.45)
        put(M,bassn(nt(ch[0]-12),b*3.5),tb,0.5)
    put(M,piano(nt(ch[(beat)%3]+24),1.6),tb,0.16,-0.3); put(M,piano(nt(ch[(beat+1)%3]+24),1.4),tb+b/2,0.11,0.3)
    if tb>=9.05: put(M,tom(80 if beat%2==0 else 110),tb,0.38); put(M,hat(0.05,70),tb+b/2,0.06)
    if tb>=12.85: put(M,kick(),tb,0.4)
    k+=1
put(M,riser(1.2,200,2200),15.45,0.4)
# 16.65-19.05 title: choir + big
put(M,choir([nt(62),nt(66),nt(69),nt(74)],2.6,0.15,0.8),16.65,0.85)
put(M,bassn(nt(38),2.4),16.65,0.6)
# 19.05-24.75 info: steady pulse in G-A-D
b2=0.6; k=0
for k in range(int((24.75-19.05)/b2)+1):
    tb=19.05+k*b2; beat=k%4; ch=[[43,47,50],[45,49,52],[50,54,57],[47,50,54]][(k//4)%4]
    if tb>24.7: break
    put(M,kick(),tb,0.42 if beat in (0,2) else 0.2); put(M,hat(),tb+b2/2,0.1,0.3)
    if beat==0: put(M,padc([nt(m+12) for m in ch],b2*4+0.2,0.2,0.5,0.25),tb,0.42); put(M,bassn(nt(ch[0]-12),b2*3),tb,0.5)
    put(M,piano(nt(ch[beat%3]+24),1.0),tb,0.1)
# 24.75-30 finale
put(M,choir([nt(62),nt(66),nt(69),nt(74),nt(78)],5.3,0.4,1.8),24.75,0.75)
put(M,padc([nt(50),nt(57),nt(62),nt(66)],5.25,0.3,1.8,0.3),24.75,0.5)
put(M,bassn(nt(38),3.0),24.75,0.55); put(M,bassn(nt(38),2.8),27.2,0.55)
for k in range(4): put(M,tom(70,0.9),24.75+k*0.6,0.3)
# ---------- VOICE ----------
import wave as wv
for i,l in TL.items():
    w=wv.open(f'{d}/vo44/{i}.wav'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    s=int(l['start']*SR); V[s:s+len(a)]+=a[:N-s]
act=np.zeros(N)
for l in TL.values(): act[int((l['start']-0.12)*SR):int((l['end']+0.15)*SR)]=1
kk=int(0.12*SR); duck=np.convolve(act,np.ones(kk)/kk,'same'); M*=(1-0.55*duck)[:,None]
# ---------- SFX ----------
def wh(t0,dur,c0,c1,g=0.5,p0=-.7,p1=.7):
    w,pn=whoosh(dur,c0,c1,p0,p1); put(X,w,t0,g,pn)
def hit(t,g=0.6): put(X,impact(0.9,0.9),t,g); put(X,thud(),t,g*0.6)
for f in [4.6,9.05,16.65,19.05,24.75]: wh(f-0.45,0.6,300,9000,0.5,0,0); put(X,boom(),f,0.7)
put(X,thud(),W('s1','lutas'),0.5)
put(X,bell([1568,2093,2637,3136],0.05,1.8,2.5),W('s1','luz')-0.25,0.35); wh(W('s1','luz')-0.4,0.6,400,6000,0.3,0,0)
hit(W('s2','omega')+0.05,0.6); wh(W('s2','omega')-0.3,0.35,600,7000,0.3)
put(X,bell([1174.7,1568,2349.3],0.08,2.0,2.2),W('s2','voz')-0.1,0.3); put(X,riser(0.6,300,1500),W('s2','voz')-0.55,0.2)
for w_ in ['louvor','palavra','transformação']: hit(W('s3',w_)+0.03,0.5); wh(W('s3',w_)-0.3,0.35,600,7000,0.25)
hit(W('s4','restauradas'),0.5); wh(W('s4','restauradas')+0.1,0.7,1500,6000,0.2,-0.8,0.8)
hit(W('s4','famílias')+0.03,0.6); put(X,bell([1318.5,1760,2217.5],0.08,2.0,2.2),W('s4','famílias')+0.1,0.25)
for w_ in ['bairro','omega','cristo']: hit(W('s5',w_)+0.03,0.75 if w_!='bairro' else 0.5)
for i in range(16): put(X,tick(2600+i*90,200),16.8+i*0.06,0.08)
hit(W('s6',0)+0.03,0.5); hit(W('s6','cinco')+0.03,0.55)
hr=W('s6','dezenove'); hit(hr+0.03,0.5)
for i in range(8): put(X,tick(3200,300),hr+i*0.1,0.2)
put(X,pop(900,300,0.15),W('s6','terreno')-0.05,0.45); put(X,pop(1200,500,0.1),W('s6','ad')-0.1,0.35)
hit(W('s7','venha')+0.03,0.7)
cr=W('s7','cristo'); hit(cr+0.03,0.8); put(X,bell([1174.7,1480,1760,2349.3],0.06,2.6,1.6),cr+0.05,0.4)
# ---------- MIX ----------
mix=M*0.8+X*0.7+np.stack([V,V],1)*1.6
fo=int(0.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=np.tanh(mix*1.05); mix=mix/np.max(np.abs(mix))*0.9
with wave.open(d+'/audio.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
