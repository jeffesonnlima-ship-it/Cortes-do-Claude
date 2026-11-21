import numpy as np, wave, json, sys, re
d=sys.argv[1]; SR=44100; D=60.0; N=int(SR*D)
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
# ================= MUSIC =================
# Part 1 (0-13.2): tense, minor, sparse, 100bpm
b=0.6
for k in range(22):
    tb=k*b
    if tb>12.9: break
    put(M,kick(0.4,90,40),tb,0.32 if k%2==0 else 0.0)
    put(M,hat(0.04,120),tb+b/2,0.10,0.3)
    if tb>=6.8: put(M,hat(0.03,140),tb+b/4,0.06,-0.3)
for i,(ch,t0) in enumerate([([57,60,64],0),([53,57,60],3.6),([57,60,64],6.8),([52,55,59],9.8)]):
    put(M,padc([nt(m) for m in ch],3.4 if i<3 else 3.1,0.6,1.0,0.15),t0,0.55)
    put(M,bassn(nt(ch[0]-24),3.0),t0,0.35)
put(M,riser(1.0,120,600),11.9,0.25)
# Part 2 (14.45 - 58.3): bright major groove 100bpm
prog=[[60,64,67],[67,71,74],[69,72,76],[65,69,72]]  # C G Am F
t0=14.45; bar=b*4; k=0
while t0+k*b<58.4:
    tb=t0+k*b; beat=k%4; barI=(k//4)%4; ch=prog[barI]
    inI=43.4<=tb<47.0
    put(M,kick(),tb,0.55 if not inI else 0.3)
    if beat in (1,3): put(M,clap(),tb,0.22)
    put(M,hat(),tb+b/2,0.14,0.35); put(M,hat(0.03,200),tb+b/4,0.05,-0.35); put(M,hat(0.03,200),tb+3*b/4,0.05,-0.35)
    if beat==0:
        put(M,padc([nt(m) for m in ch],bar+0.2,0.25,0.5,0.3),tb,0.42)
        put(M,bassn(nt(ch[0]-24),b*1.8),tb,0.45); put(M,bassn(nt(ch[0]-24),b*1.2),tb+b*2.5,0.35)
    # arpeggio plucks (8ths)
    for e in range(2):
        m=ch[(beat*2+e)%3]+12
        put(M,pluck(nt(m)),tb+e*b/2,0.09,0.4 if e else -0.4)
    k+=1
put(M,padc([nt(m) for m in [60,64,67,72,76]],2.6,0.05,1.8,0.3),57.6,0.55)
put(M,bassn(nt(36),2.2),57.6,0.5)
# ================= VOICE =================
import wave as wv
for i,l in TL.items():
    w=wv.open(f'{d}/vo44/{i}.wav'); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    s=int(l['start']*SR); V[s:s+len(a)]+=a[:N-s]
# duck envelope from voice activity
act=np.zeros(N)
for l in TL.values(): act[int((l['start']-0.12)*SR):int((l['end']+0.15)*SR)]=1
k=int(0.12*SR); ker=np.ones(k)/k; duck=np.convolve(act,ker,'same')
mg=1-0.62*duck
M*=mg[:,None]
# ================= SFX =================
def wh(t0,dur,c0,c1,g=0.5,p0=-.7,p1=.7):
    w,pn=whoosh(dur,c0,c1,p0,p1); put(X,w,t0,g,pn)
# A
put(X,pop(),0.05,0.8); wh(0.4,0.5,500,4000,0.25)
ev=W('s1','vendo'); put(X,pop(1100,500,0.1),ev-0.1,0.45); wh(ev+0.1,0.3,3000,8000,0.3,0.3,-0.3)
wh(3.45,0.45,300,6000,0.6,0,0); put(X,riser(0.4,200,900),3.45,0.25)
# B
tp=W('s2','posta')-0.05; put(X,tick(1800,120),tp,0.6); put(X,pop(700,350,0.1),tp+0.15,0.4)
put(X,sad(),W('s2','nada')-0.05,0.38)
wh(6.55,0.4,800,7000,0.6,0.8,-0.8)
# C
for w_ in ['perfil','poucas','concorrente']: wh(W('s3',w_)-0.2,0.4,400,3000,0.35,0,0); put(X,thud(),W('s3',w_)+0.12,0.25)
wh(W('s3','concorrente')+0.2,1.6,300,2500,0.25,-0.5,0.8)
# D lever
put(X,fall(0.3,1600,300),13.55,0.3); put(X,thud(),13.85,1.0); put(X,impact(0.6,0.6),13.85,0.5)
put(X,riser(0.5,300,2400),13.9,0.45); wh(13.95,0.45,1500,9000,0.5,0,0)
put(X,impact(1.6,1.3),14.4,0.95); put(X,bell([1046.5,1318.5,1568,2093]),14.45,0.4)
for i in range(9): put(X,tick(2400+i*120,200),14.75+i*0.05,0.18,-0.6+i*0.15)
wh(15.45,0.5,2000,6000,0.18,-0.4,0.4)
# sweeps
for s in [17.1,23.2,36.8,52.3]: wh(s-0.36,0.72,400,7000,0.6,-0.9,0.9); put(X,thud(),s,0.25)
# E
for w_ in ['marketing','identidade','estratégia']: put(X,pop(1000,420,0.1),W('s5',w_)-0.05,0.45)
put(X,riser(0.6,300,1200),W('s5','crescerem')-0.05,0.25)
# F
c=W('s6','cores')
for i in range(5): put(X,pop(1200+i*90,600,0.08),c+i*0.06,0.3)
wh(W('s6','logo')-0.2,0.4,600,5000,0.35); wh(W('s6','tipografia')-0.2,0.4,600,5000,0.35)
lm=W('s6','lembrada'); put(X,thud(),lm+0.05,0.7); put(X,bell([1568,2093,2637]),lm+0.08,0.35)
wh(30.2,0.4,600,7000,0.6,0,0)
# G
put(X,riser(5.0,200,700),30.9,0.08)
put(X,pop(),31.0,0.35); put(X,pop(1100,450),W('s7','público'),0.4); put(X,pop(900,350),W('s7','objetivos')-0.15,0.4)
put(X,thud(),W('s7','objetivos')+0.35,0.6); put(X,tick(3000,90),W('s7','objetivos')+0.35,0.3)
put(X,bell([1318.5,1760]),W('s7','objetivos')+0.9,0.25)
# H
for i in range(9): put(X,pop(1300+(i%3)*150,600,0.07),37.4+i*0.12,0.22,-0.5+(i%3)*0.5)
for w_,pn in [('atrai',-0.6),('engaja',0.6),('transforma',-0.6)]: put(X,pop(1000,400,0.1),W('s8',w_)-0.05,0.4,pn)
eg=W('s8','engaja')
for i in range(12): put(X,tick(2600+(i*170)%900,120),eg-0.2+i*0.12+0.3,0.1,((i*7)%10)/5-1)
cl=W('s8','clientes'); put(X,bell([1567.98,2093.0],0.1,1.0,5),cl,0.55); wh(cl-0.15,0.3,2000,6000,0.25)
# I
put(X,impact(0.8,0.8),43.4,0.5)
for j in (0,2,4): put(X,impact(0.7,1.0),W('s9',j)+0.05,0.75); put(X,clap(),W('s9',j)+0.05,0.4)
put(X,riser(0.6,300,1500),W('s9',4)+0.3,0.3)
# J
wh(46.8,0.5,6000,500,0.5,0.6,-0.6)
for i in range(14): put(X,tick(1900,220),48.0+i*0.15,0.12)
pe=W('s10','perto')
for i in range(7): put(X,tick(2400+i*100,160),pe-0.2+i*0.1+0.05,0.25)
put(X,bell([1318.5,1568,1975.5]),W('s10','medir'),0.35)
# K
put(X,pop(800,260,0.15),52.45,0.8); put(X,bell([1046.5,1318.5,1568,2093]),52.5,0.4)
dm=W('s11','direct'); put(X,pop(1000,450,0.1),dm-0.5,0.4); put(X,tick(1800,120),dm,0.6)
cr=W('s11','crescer'); put(X,riser(0.8,400,2000),cr-0.5,0.2)
for i in range(16): put(X,tick(3000+(i*230)%1500,150),cr-0.3+i*0.09,0.1,((i*5)%10)/5-1)
# ================= MIX =================
mix=M*0.8+X*0.75+np.stack([V,V],1)*1.55
fo=int(0.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=np.tanh(mix*1.05); mix=mix/np.max(np.abs(mix))*0.9
with wave.open(d+'/audio.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix*32767).astype('<i2').tobytes())
print('ok')
