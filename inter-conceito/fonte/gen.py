import numpy as np, wave
SR=44100; D=10.0; N=int(SR*D)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t0,gain=1.0,pan=0.0):
    i=int(t0*SR); n=min(len(sig),N-i)
    if n<=0: return
    if np.ndim(pan)==0: pan=np.full(len(sig),pan)
    l=np.sqrt((1-pan[:n])/2); r=np.sqrt((1+pan[:n])/2)
    L[i:i+n]+=sig[:n]*gain*l; R[i:i+n]+=sig[:n]*gain*r
def tt(d): return np.arange(int(d*SR))/SR
def lp(x,cut):  # one-pole lowpass, cut can be array
    cut=np.broadcast_to(cut,x.shape); a=1-np.exp(-2*np.pi*cut/SR); y=np.zeros_like(x); s=0.0
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def kick(d=0.35,f0=130,f1=45):
    t=tt(d); f=f1+(f0-f1)*np.exp(-t*30); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)+0.3*rng.standard_normal(len(t))*np.exp(-t*300)
def hat(d=0.05):
    t=tt(d); n=rng.standard_normal(len(t)); n=n-lp(n,6000); return n*np.exp(-t*90)
def clap():
    t=tt(0.2); n=rng.standard_normal(len(t)); n=lp(n,4000)-lp(n,900)
    env=np.exp(-t*25)*(1+0.6*(np.sin(2*np.pi*t*90)>0)*(t<0.03)); return n*env*1.5
def whoosh(d,c0,c1,pan0=-0.8,pan1=0.8):
    t=tt(d); x=t/d; n=rng.standard_normal(len(t))
    cut=c0*(c1/c0)**x; y=lp(n,cut)-lp(n,cut*0.25)
    env=np.sin(np.pi*x)**2; return y*env*2.2, pan0+(pan1-pan0)*x
def pop(f0=900,f1=280,d=0.12):
    t=tt(d); f=f1+(f0-f1)*np.exp(-t*60); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def tick(f=2200):
    t=tt(0.035); return np.sin(2*np.pi*f*t)*np.exp(-t*160)
def chime(freqs,step=0.06,d=1.2):
    out=np.zeros(int((d+step*len(freqs))*SR))
    for k,f in enumerate(freqs):
        t=tt(d); s=(np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*4.5)
        i=int(k*step*SR); out[i:i+len(s)]+=s
    return out/len(freqs)*2
def riser(d=0.5):
    t=tt(d); x=t/d; f=200*(6**x); s=np.sin(2*np.pi*np.cumsum(f)/SR)*0.4
    n=rng.standard_normal(len(t)); n=n-lp(n,300+6000*x)*0+0; n=lp(n,500+9000*x**2)
    return (s+n*0.8)*x**2
def impact():
    t=tt(1.2); f=30+70*np.exp(-t*12); sub=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)
    n=lp(rng.standard_normal(len(t)),2500)*np.exp(-t*10)
    return sub*1.2+n*0.9
def pad(freqs,d,att=0.3,rel=0.6):
    t=tt(d); s=np.zeros(len(t))
    for f in freqs:
        for det in (-0.6,0.6): s+=np.sin(2*np.pi*(f+det)*t)+0.25*np.sin(2*np.pi*2*(f+det)*t)
    env=np.minimum(1,t/att)*np.minimum(1,(d-t)/rel); return s/len(freqs)*env*0.35
# ---- music bed: 120 bpm
beat=0.5
for k in range(13):           # 0 .. 6.0
    tb=k*beat
    add(kick(),tb,0.55)
    add(hat(),tb+beat/2,0.18, 0.3)
    if k%2==1: add(clap(),tb,0.22)
for k in range(4):            # after impact 6.8..8.6
    tb=7.3+k*beat
    if tb<8.6: add(kick(),tb,0.45); add(hat(),tb+beat/2,0.14,-0.3)
C=[261.6,329.6,392.0]; F=[349.2,440.0,523.3]; G=[392.0,493.9,587.3]; A=[220.0,261.6,329.6]
add(pad(C,2.05),0.0,0.5); add(pad(A,2.05),2.0,0.5); add(pad(F,2.3),4.0,0.5)
add(pad(G+[784],1.9),6.8,0.55); add(pad([261.6,392,523.3,659.3],1.6,0.05,1.2),8.4,0.5)
# ---- sfx
add(pop(),0.03,0.9)
w,pn=whoosh(0.55,400,5000); add(w,0.62,0.55,pn)
w,pn=whoosh(0.45,600,7000,0.7,-0.5); add(w,1.45,0.45,pn)
for i in range(4): add(tick(2000+i*250),1.78+i*0.07,0.35,-0.6+i*0.4)
w,pn=whoosh(0.4,2000,300,0,0); add(w,2.0,0.55,pn)
add(chime([1046.5,1318.5,1568.0,2093.0]),2.4,0.5)
w,pn=whoosh(0.5,300,6000,-0.6,0.6); add(w,3.05,0.5,pn)
for t0,pa in ((4.05,0.7),(4.85,0.7),(5.6,0.7)):
    w,pn=whoosh(0.42,800,8000,pa,-pa); add(w,t0,0.45,pn); add(tick(1600),t0+0.38,0.4)
add(riser(0.52),6.28,0.7)
add(impact(),6.8,1.0)
add(pop(1200,500,0.1),6.82,0.5)
w,pn=whoosh(0.35,1500,6000,-0.4,0.4); add(w,7.05,0.3,pn)
add(chime([1568.0,2093.0]),7.3,0.3)
w,pn=whoosh(0.4,4000,500,0.5,-0.5); add(w,7.6,0.4,pn)
add(pop(800,260,0.14),7.95,0.95); add(chime([1318.5,1568.0,2093.0,2637.0],0.05),8.0,0.45)
add(chime([2093.0,2637.0,3136.0,4186.0],0.08,1.4),8.7,0.3)
w,pn=whoosh(0.6,6000,600,0.6,-0.6); add(w,9.35,0.35,pn)
# ---- master
fade=np.ones(N); fo=int(0.35*SR); fade[-fo:]=np.linspace(1,0,fo)
fade[:int(0.005*SR)]=np.linspace(0,1,int(0.005*SR))
st=np.stack([L,R],1)*fade[:,None]
st=np.tanh(st*1.1); st=st/np.max(np.abs(st))*0.89
with wave.open('audio.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
