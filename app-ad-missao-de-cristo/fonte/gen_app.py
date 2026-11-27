import numpy as np, wave, json, sys, re
d=sys.argv[1]; SR=44100; D=39.0; N=int(SR*D)
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
WD=[(a+0.5,b+0.5,w) for a,b,w in json.load(open(d+'/words.json'))]
def T(pref,after=0):
    for a,b,w in WD:
        if a>=after and re.sub(r'[^a-z0-9à-ú]','',w.lower()).startswith(pref): return a
    raise Exception(pref)
def piano(f,dur=1.6):
    t=tt(dur); s=sum(np.sin(2*np.pi*f*k*t)*np.exp(-t*(2.2+k*1.6))/k for k in range(1,6)); return s*np.minimum(1,t/0.004)*0.6
def shaker():
    t=tt(0.08); n=rng.standard_normal(len(t)); return (n-lp(n,5000))*np.sin(np.pi*t/0.08)**2
# ---------- MUSIC: G D Em C, 104bpm ----------
b=60/104; prog=[[55,59,62],[50,54,57],[52,55,59],[48,52,55]]
put(M,padc([nt(m+12) for m in prog[0]],1.2,0.6,0.4,0.2),0,0.4)
k=0; t0=0.5
while t0+k*b<36.4:
    tb=t0+k*b; beat=k%4; ch=prog[(k//4)%4]
    full=tb>=4.4
    if beat==0:
        put(M,padc([nt(m+12) for m in ch],b*4+0.3,0.3,0.6,0.25),tb,0.42)
        put(M,bassn(nt(ch[0]-12),b*2.2),tb,0.5); put(M,bassn(nt(ch[0]-12),b*1.4),tb+b*2.5,0.38)
    put(M,piano(nt(ch[beat%3]+24)),tb,0.17,-0.25); put(M,piano(nt(ch[(beat+1)%3]+24),1.2),tb+b/2,0.1,0.25)
    if full:
        put(M,kick(0.35,110,45),tb,0.42 if beat in (0,2) else 0.0)
        if beat in (1,3): put(M,clap(),tb,0.16)
        put(M,shaker(),tb+b/2,0.1,0.4); put(M,shaker(),tb+b/4,0.05,-0.4); put(M,shaker(),tb+3*b/4,0.05,-0.4)
    k+=1
put(M,padc([nt(m) for m in [67,71,74,79]],3.0,0.05,2.2,0.3),36.3,0.6); put(M,bassn(nt(43),2.6),36.3,0.55)
# ---------- VOICE ----------
w=wave.open(d+'/vo.wav'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
s0=int(0.5*SR); V[s0:s0+len(a)]+=a[:N-s0]
env=np.abs(V); k2=int(0.15*SR); env=np.convolve(env,np.ones(k2)/k2,'same'); act=np.clip(env/0.02,0,1)
k3=int(0.2*SR); duck=np.convolve(act,np.ones(k3)/k3,'same'); M*=(1-0.6*duck)[:,None]
# ---------- SFX ----------
def wh(t0,dur,c0,c1,g=0.5,p0=-.7,p1=.7):
    w_,pn=whoosh(dur,c0,c1,p0,p1); put(X,w_,t0,g,pn)
put(X,pop(800,260,0.15),0.1,0.7); put(X,bell([1174.7,1568,1975.5],0.07,1.8,2.2),0.15,0.3)
put(X,thud(),T('igreja')+0.05,0.4)
ap=T('aplicativo'); wh(ap-0.4,0.7,300,6000,0.5,0,0)
put(X,bell([1568,1975.5,2349.3,3136],0.05,1.4,2.8),T('cara')-0.1,0.3)
put(X,pop(1000,420,0.1),T('mesmas')-0.1,0.4,-0.5); put(X,pop(1200,500,0.1),T('novidades')-0.1,0.4,0.5)
for key,af in [('bíblia',0),('pedido',0),('dízimos',0),('breve',0)]:
    tk=T(key); wh(tk-0.45,0.55,500,5000,0.28,0,0); put(X,pop(1100,500,0.08),tk,0.35)
put(X,pop(900,350,0.12),T('pix')-0.1,0.45); put(X,pop(900,350,0.12),T('breve')+0.1,0.35)
for sw in [T('painel')-0.3,T('devocional')-0.3,T('quiz')-0.3,T('comunidade')-0.3]:
    put(X,tick(1800,120),sw-0.3,0.5); wh(sw-0.05,0.45,800,6000,0.4,0.7,-0.7)
pg=T('programação'); put(X,pop(900,400,0.1),pg,0.35)
for i in range(7): put(X,tick(2300+i*110,180),pg+0.3+i*0.12,0.2)
put(X,pop(1000,450,0.1),T('devocional')+0.4,0.3); put(X,pop(1000,450,0.1),T('palavra',23)-0.05,0.3)
n30=T('30'); put(X,pop(800,300,0.14),n30-0.1,0.5)
for i in range(1,8): put(X,tick(1500,250),n30+0.3+i/2.2,0.22)
wp=T('whatsapp'); put(X,pop(1000,450,0.1),wp-0.05,0.4); put(X,bell([1318.5,1760],0.1,1.0,4),wp+0.15,0.35)
put(X,pop(900,450,0.1),T('acompanha')+0.2,0.25)
at=T('atualize'); wh(at-0.2,0.7,6000,500,0.45,0.6,-0.6)
a2=T('aplicativo',34); put(X,pop(900,320,0.14),a2-0.25,0.5); put(X,tick(1800,120),a2+0.25,0.6)
put(X,riser(T('deus')-a2-0.45,300,1400),a2+0.35,0.18)
dz=T('deus'); put(X,bell([1568,1975.5,2349.3,3136],0.06,2.2,1.8),dz-0.1,0.5); put(X,impact(1.2,0.7),dz-0.1,0.4)
# ---------- MIX ----------
mix=M*0.75+X*0.6+np.stack([V,V],1)*1.25
fo=int(0.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=np.tanh(mix*1.02); mix=mix/np.max(np.abs(mix))*0.9
with wave.open(d+'/audio.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
