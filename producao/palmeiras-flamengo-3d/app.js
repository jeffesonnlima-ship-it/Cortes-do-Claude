import {THREE,V,R,E,clamp,prog,lerp,shake,path,seedRnd,ctex,redraw,fitText,rr,toon,OL,mesh,glow,plaque,makeChar,pose,setExpr,makeBall,confetti,disposeAll,sky} from './lib.js';
import * as Wd from './world.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const TL=await (await fetch('timeline.json?'+Date.now())).json();const K=TL.keys;
await document.fonts.load('900 40px N');await document.fonts.load('800 40px "JetBrains Mono"');
const Wd_=720,Hd=1280;const canvas=document.getElementById('c');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(1);renderer.setSize(Wd_,Hd,false);renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const ENV=new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(),.04).texture;
const flash=document.getElementById('flash'),hbb=document.getElementById('hbb');
const cam=(fov=40)=>{const c=new THREE.PerspectiveCamera(fov,Wd_/Hd,.1,2000);return c};
let DF=1;const look=(c,p,t,roll=0)=>{p=t.clone().add(p.clone().sub(t).multiplyScalar(DF));c.position.copy(p);c.lookAt(t);if(roll)c.rotateZ(roll)};
const FL=(t,at,dur=.18,max=.75)=>{const d=t-at;return d<0||d>dur?0:max*(1-d/dur)};
let FLASH=0,BLUR=0;

/* =============== shot builders =============== */
const B={};
function stadiumShot(o){const S=Wd.stadiumScene(o);return S}

B.aerial=(sh)=>{const S=stadiumShot({sky:'dusk',crowd:Wd.PAL_CROWD,bounceHz:2,sunPos:V(-40,30,20)});const {scene}=S;
  const pl=Wd.lineup(scene,'PAL','FLA',{scale:.85});const c=cam(42);const ball=makeBall(.3);ball.position.set(0,.3,0);scene.add(ball);
  return {scene,cam:c,update(t,d){S.st.userData.bounce(t);pl.forEach((p,i)=>pose(p,'idle',t*3+i));
    const k=E.io(prog(t,0,d));const a=lerp(-1.4,.35,k);const r=lerp(42,26,k),h=lerp(150,6.5,E.o(k));
    look(c,V(Math.sin(a)*r,h,Math.cos(a)*r),V(0,lerp(0,2.4,k),0).add(shake(t,.08)),lerp(.06,0,k));c.fov=lerp(48,38,k);c.updateProjectionMatrix()}}};

B.exterior=B.exterior2=(sh)=>{const night=sh.id==='exterior2';const scene=new THREE.Scene();
  scene.add(sky(...(night?['#050a24','#162a66','#2a4a8c']:['#2a2d6e','#d2668a','#ffb26a']),night));
  const L=Wd.lights(scene,{sky:night?'#9fb6ff':'#ffd9b0',hemi:1.1,sunI:night?1.2:2.4,sunPos:V(-20,30,40),shadowSize:40});
  const gm=mesh(new THREE.PlaneGeometry(400,400),toon('#6d7280'),V(0,0,0),{recv:1});gm.rotation.x=-Math.PI/2;gm.receiveShadow=true;scene.add(gm);
  // facade
  const fac=new THREE.Group();scene.add(fac);const R0=60;
  const shell=mesh(new THREE.CylinderGeometry(R0,R0,26,96,1,true,-1.1,2.2),toon('#e9eef2',null,{side:THREE.DoubleSide}),V(0,13,-R0+8));fac.add(shell);
  for(let i=0;i<44;i++){const a=-1.08+i*(2.16/43);const fin=OL(mesh(new THREE.BoxGeometry(1.1,24,1.6),toon(i%2?'#0c7a3c':'#0a5f2f'),V(Math.sin(a)*(R0+.6),12.5,Math.cos(a)*(R0+.6)-R0+8),{cast:1}),.03);fin.rotation.y=a;fac.add(fin)}
  const roofRing=mesh(new THREE.TorusGeometry(R0,.8,8,96,2.2),toon('#ffffff'),V(0,26,-R0+8));roofRing.rotation.x=Math.PI/2;roofRing.rotation.z=-Math.PI/2-1.1;fac.add(roofRing);
  const sign=plaque(['NUBANK PARQUE'],26,4.4,{bg:'#0a5f2f',grad:['#0e8a45','#06522a'],border:'#ffffff',ppu:60,d:1.2});sign.position.set(0,17,8.8);fac.add(sign);
  const sg=glow('#c8ffd9',40,night?.35:.15);sg.position.set(0,17,10);fac.add(sg);
  const gate=mesh(new THREE.BoxGeometry(18,8,1),toon('#1d222d'),V(0,4,8.5));fac.add(gate);
  for(let i=0;i<6;i++){const gl=glow('#ffe7b0',6,night?.8:.4);gl.position.set(-15+i*6,9.5,9.5);fac.add(gl)}
  if(night){const pl=new THREE.PointLight('#ffe7b0',200,60,1.5);pl.position.set(0,12,22);scene.add(pl)}
  const fans=[];for(let i=0;i<14;i++){const c=makeChar({team:i%5==0?'FLA':'PAL',skin:['#f2c49b','#d9a173','#b07a50','#8a5a3b'][i%4],curly:i%3==0,scale:.9,scarf:i%2?'#ffffff':null});
    c.g.position.set(R(-22,22),0,R(12,34));c.g.rotation.y=Math.PI+R(-.4,.4);c.sp=R(.8,1.3);c.ph=R(0,6);scene.add(c.g);fans.push(c)}
  const c=cam(40);
  return {scene,cam:c,update(t,d){fans.forEach(f=>{pose(f,'walk',t*6*f.sp+f.ph);f.g.position.z-=0;f.g.userData.z0??=f.g.position.z;f.g.position.z=f.g.userData.z0-t*1.6*f.sp});
    const k=E.io(prog(t,0,d));
    if(!night)look(c,V(lerp(-6,4,k),lerp(1.6,3.5,k),lerp(48,40,k)),V(0,lerp(10,15,k),0).add(shake(t,.05)),lerp(-.05,.03,k));
    else look(c,V(lerp(14,-8,k),lerp(2,16,E.o(k)),lerp(56,44,k)),V(0,lerp(8,16,k),0).add(shake(t,.05)));c.fov=lerp(46,40,k);c.updateProjectionMatrix()}}};

B.trophy=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#06060a');scene.environment=ENV;
  const tr=Wd.trophy(ENV);tr.scale.setScalar(1.3);scene.add(tr);
  const fl=mesh(new THREE.CircleGeometry(30,64),new THREE.MeshStandardMaterial({color:'#111116',roughness:.25,metalness:.6}),null,{recv:1});fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;scene.add(fl);
  const sp=new THREE.SpotLight('#fff3d0',900,60,.38,.6,1.4);sp.position.set(0,22,4);sp.target=tr;sp.castShadow=true;sp.shadow.mapSize.set(1024,1024);scene.add(sp);
  const g1=new THREE.PointLight('#16c25a',160,30,1.4);g1.position.set(-8,5,4);scene.add(g1);const r1=new THREE.PointLight('#ff2030',160,30,1.4);r1.position.set(8,5,4);scene.add(r1);
  scene.add(new THREE.AmbientLight('#ffffff',.15));
  const beam=mesh(new THREE.ConeGeometry(7,24,40,1,true),new THREE.MeshBasicMaterial({color:'#fff6d0',transparent:true,opacity:.06,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending}),V(0,11,0));scene.add(beam);
  const dust=confetti(120,['#fff3c0'],[5,20,5]);dust.material.transparent=true;dust.material.opacity=.5;dust.scale.setScalar(.25);scene.add(dust);
  const c=cam(34);return {scene,cam:c,update(t,d){const k=E.o(prog(t,0,d));const a=lerp(-.9,.25,k);const r=lerp(14,10.5,k);dust.userData.update(t*.3);
    look(c,V(Math.sin(a)*r,lerp(2.2,4.2,k),Math.cos(a)*r),V(0,3.6,0).add(shake(t,.03)));tr.rotation.y=t*.25}}};

B.faceoff=(sh)=>{const S=Wd.bar({lampX:0,lampZ:1});const {scene}=S;
  const a=makeChar({team:'PAL',ex:'angry'});a.g.position.set(-2.3,0,1.5);a.g.rotation.y=Math.PI/2-.25;scene.add(a.g);
  const b=makeChar({team:'FLA',ex:'smug',curly:true,skin:'#b07a50'});b.g.position.set(2.3,0,1.5);b.g.rotation.y=-Math.PI/2+.25;scene.add(b.g);
  Wd.drawTV(S.tvTex,(c,w,h)=>Wd.tvPitch(c,w,h,'PAL × FLA','HOJE · 16H30'));
  const vs=plaque([{t:'VS',c:'#ffd23f',stroke:14}],2.6,1.8,{bg:'#c0392b',grad:['#e74c3c','#a5281b'],border:'#ffffff',ppu:120,d:.5});vs.position.set(0,5.4,1.6);scene.add(vs);
  const ringM=new THREE.MeshBasicMaterial({color:'#ffd23f',transparent:true,side:THREE.DoubleSide});const ringO=mesh(new THREE.RingGeometry(1,1.25,48),ringM,V(0,5.4,1.4));scene.add(ringO);
  const c=cam(38);const tv=0.35;
  return {scene,cam:c,update(t,d){pose(a,'cross',t*3);pose(b,'idle',t*3);a.headG.rotation.z=Math.sin(t*2)*.05;
    const p=E.el(prog(t,tv,tv+.7));vs.scale.setScalar(Math.max(.001,p));vs.rotation.z=(1-p)*.6;const rp=prog(t,tv,tv+.6);ringO.scale.setScalar(1+rp*4);ringM.opacity=(1-rp)*(rp>0?1:0);
    const k=E.io(prog(t,0,d));const ang=lerp(-.55,.55,k);look(c,V(Math.sin(ang)*9.5,lerp(3.4,4.4,k),Math.cos(ang)*9.5+1.5),V(0,3.7,1.5).add(shake(t,.04)),Math.sin(t*1.3)*.02);c.fov=lerp(44,36,k);c.updateProjectionMatrix()}}};

B.ledoff=(sh)=>{const S=stadiumShot({sky:'night',crowd:Wd.MIX_CROWD,bounceHz:0});const {scene}=S;
  const led=Wd.ledBoard(30,12);led.position.set(-70,34,0);led.rotation.y=Math.PI/2;scene.add(led);
  const p=makeChar({team:'FLA',ex:'sad',curly:true,skin:'#d9a173',scale:.9});p.g.position.set(-12,0,3);p.g.rotation.y=-Math.PI/2+.4;scene.add(p.g);
  const p2=makeChar({team:'PAL',ex:'smug',scale:.9});p2.g.position.set(-16,0,-4);p2.g.rotation.y=Math.PI/2+.3;scene.add(p2.g);
  const c=cam(40);
  return {scene,cam:c,update(t,d){const gl=t<1.2||(t>2.4&&t<2.7)||(t>4.4&&t<4.6);Wd.ledDraw(led.userData.tex,gl?[]:[{t:'?',s:360}],{noise:gl&&Math.floor(t*20)%3!=0});
    led.userData.glow.material.opacity=gl?.08:.22+Math.sin(t*9)*.04;pose(p,'sad',t);pose(p2,'cross',t);
    const k=E.io(prog(t,0,d));
    if(t<d*.5){const q=E.io(prog(t,0,d*.5));look(c,V(lerp(-2,-6,q),lerp(1.6,2.4,q),lerp(10,8,q)),V(-13,lerp(2,3.5,q),0).add(shake(t,.05)))}
    else{const q=E.io(prog(t,d*.5,d));look(c,V(lerp(-8,-40,q),lerp(4,26,q),lerp(14,4,q)),V(-70,lerp(14,34,q),0).add(shake(t,.08)))}
    c.fov=40;c.updateProjectionMatrix()}}};

function calShot(seq,subs,opts={}){return (sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#140e0a');
  const desk=mesh(new THREE.BoxGeometry(60,1,30),toon('#5a3a20'),V(0,-.5,0),{recv:1});desk.receiveShadow=true;scene.add(desk);
  const base=Wd.calendarBase();base.position.set(0,6.4,0);scene.add(base);
  const pages=seq.map((s,i)=>{const p=Wd.calendarPage(s,subs[i]);p.position.set(0,6.4,.02+(seq.length-i)*.012);base.parent.add(p);return p});
  const sp=new THREE.SpotLight('#ffe9c0',700,50,.5,.6,1.3);sp.position.set(4,18,10);sp.target=base;sp.castShadow=true;scene.add(sp);scene.add(new THREE.AmbientLight('#ffd9b0',.35));
  const ex=opts.extra?opts.extra(scene):null;
  const c=cam(36);const flips=opts.flips;
  return {scene,cam:c,update(t,d){pages.forEach((p,i)=>{if(i===pages.length-1)return;const ft=flips[i];const q=prog(t,ft,ft+.45);p.rotation.x=-E.i(q)*2.6;p.position.y=6.4+E.i(q)*4;p.position.z=.02+(seq.length-i)*.012+E.i(q)*3;p.visible=q<1;p.rotation.z=E.i(q)*(i%2?.6:-.6)});
    if(ex)ex(t);opts.cam(c,t,d)}}}}
B.cal36=calShot(['35','36'],['RODADA','RODADA'],{flips:[.25],extra:(scene)=>{const cards=[];['37','38'].forEach((n,i)=>{const p=plaque([n],2.4,2.4,{bg:'#f7f0e1',fg:'#1b1b22',border:'#c0392b',ppu:100});p.position.set(i?6.5:-6.5,1.3,3);p.rotation.set(-1.2,0,i?-.3:.25);scene.add(p);cards.push(p)});
    const f3=plaque(['FALTAM 3'],5,1.2,{bg:'#c0392b',border:'#fff',ppu:100});f3.position.set(0,.7,5);f3.rotation.x=-1.1;scene.add(f3);return t=>{f3.scale.setScalar(Math.max(.001,E.back(prog(t,.7,1.1))))}},
  cam:(c,t,d)=>{const k=E.o(prog(t,0,d));look(c,V(lerp(-6,1.5,k),lerp(9,6.5,k),lerp(22,15,k)),V(0,lerp(4,3.6,k),0).add(shake(t,.03)),lerp(-.12,0,k))}});
B.cal26=calShot(['2025','2026'],['ANO','ANO'],{flips:[.9],extra:(scene)=>{const pg=[];for(let i=0;i<14;i++){const p=plaque([String(i%2?'2026':'2025')],1.6,1.4,{bg:'#f7f0e1',fg:'#1b1b22',border:false,ppu:60,ol:false,d:.02});p.position.set(R(-8,8),R(4,14),R(-2,4));p.userData.v=V(R(-3,3),R(2,5),R(1,4));p.userData.w=V(R(-4,4),R(-4,4),R(-4,4));scene.add(p);pg.push(p)}
    return t=>{pg.forEach(p=>{const q=prog(t,.9,4);p.visible=q>0;const s=q*3;p.position.addScaledVector(p.userData.v,0);p.position.set(p.userData.v.x*s,6+p.userData.v.y*s-2*s*s*.3,p.userData.v.z*s+2);p.rotation.set(p.userData.w.x*s,p.userData.w.y*s,p.userData.w.z*s)})}},
  cam:(c,t,d)=>{const k=E.io(prog(t,0,d));const a=lerp(.7,-.25,k);look(c,V(Math.sin(a)*16,lerp(12,6.5,k),Math.cos(a)*16),V(0,3.8,0).add(shake(t,.04)),lerp(.15,-.03,k))}});

function boardShot(cfg){return (sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#120c08');
  scene.add(new THREE.AmbientLight('#ffe2b8',.45));const sp=new THREE.SpotLight('#ffe9c0',1000,60,.55,.5,1.3);sp.position.set(-4,14,16);sp.castShadow=true;scene.add(sp);const gl=new THREE.PointLight('#ffd27a',60,30);gl.position.set(6,3,8);scene.add(gl);
  const wall=mesh(new THREE.PlaneGeometry(80,50),toon('#2a1a10'),V(0,0,-1.2),{recv:1});scene.add(wall);
  const bd=Wd.tableBoard();scene.add(bd);sp.target=bd;
  const head=plaque([cfg.head],9,1.5,{bg:'#1f6b3a',grad:['#2a8a4c','#14552d'],border:'#e8c14a',ppu:100});head.position.set(0,5,.4);bd.add(head);
  const rows=cfg.rows.map((r,i)=>{const g=new THREE.Group();g.position.set(0,2.2-i*2.4,.4);bd.add(g);const badge=plaque([String(i+1)],1.1,1.4,{bg:'#e8c14a',fg:'#1b1b22',border:'#16161c',ppu:100});badge.position.x=-4.1;g.add(badge);
    const tp=Wd.teamPlate(r.n,r.c,5.2);tp.position.x=-.6;g.add(tp);const dg=[0,1].map(j=>{const d_=Wd.digit(String(r.p).padStart(2,'0')[j]);d_.position.set(2.75+j*1.1,.7,.1);g.add(d_);return d_});
    return {g,r,dg,badge}});
  const big=cfg.big?plaque([{t:cfg.big,c:'#ffd23f',stroke:10}],4.6,2.4,{bg:'#14182a',border:'#e8c14a',ppu:110,d:.6}):null;if(big){big.position.set(0,-3.6,1.2);bd.add(big)}
  const sub=cfg.sub?plaque([cfg.sub],7.6,1.1,{bg:'#e8c14a',fg:'#1b1b22',border:'#16161c',ppu:100}):null;if(sub){sub.position.set(0,-5.4,1.2);bd.add(sub)}
  const c=cam(36);const rnd=[...Array(40)].map(()=>Math.floor(Math.random()*10));
  return {scene,cam:c,update(t,d){rows.forEach((o,i)=>{const at=cfg.digitAt?cfg.digitAt[i]:(.3+i*.4);o.dg.forEach((dg,j)=>{const q=prog(t,at+j*.08,at+j*.08+.35);dg.rotation.x=(1-E.back(q))*-Math.PI/2;dg.visible=q>0;
        const final=String(cfg.valAt?cfg.valAt(i,t):o.r.p).padStart(2,'0')[j];Wd.setDigit(dg,q<1&&q>0?String(rnd[(Math.floor(t*30)+i*7+j)%40]):final)});
      const sq=E.back(prog(t,(cfg.slideAt||0)+i*.12,(cfg.slideAt||0)+i*.12+.5));o.g.position.x=(1-sq)*-14;
      if(cfg.rowY)o.g.position.y=cfg.rowY(i,t);if(cfg.rowZ)o.g.position.z=.4+cfg.rowZ(i,t)});
    if(big){const q=E.el(prog(t,cfg.bigAt,cfg.bigAt+.8));big.scale.setScalar(Math.max(.001,q));big.rotation.z=(1-q)*.4}
    if(sub){const q=E.back(prog(t,cfg.subAt,cfg.subAt+.5));sub.scale.setScalar(Math.max(.001,q))}
    if(cfg.anim)cfg.anim(rows,t);cfg.cam(c,t,d)}}}}
B.table1=boardShot({head:'BRASILEIRÃO 2026',rows:[{n:'FLAMENGO',p:79,c:'#c0151d'},{n:'PALMEIRAS',p:73,c:'#0c7a3c'}],digitAt:[K.p79-TL.shots[6].t0+.2,K.p73-TL.shots[6].t0+.1],big:'+6',bigAt:K.seis-TL.shots[6].t0,sub:'PONTOS DE DIFERENÇA',subAt:K.seis-TL.shots[6].t0+.5,
  cam:(c,t,d)=>{const s1=1.2,s2=K.seis-TL.shots[6].t0-.2;if(t<s2){const k=E.io(prog(t,0,s2));look(c,V(lerp(-10,6,k),lerp(-3,3,k),lerp(10,18,k)),V(lerp(-3,1,k),lerp(1.5,1,k),0).add(shake(t,.04)),lerp(.1,-.04,k))}
    else{const k=E.o5(prog(t,s2,s2+.6));look(c,V(lerp(6,0,k),lerp(3,-2,k),lerp(18,11,k)),V(0,lerp(1,-3.5,k),0).add(shake(t,.05)))}}});
B.table2=boardShot({head:'BRASILEIRÃO 2026',rows:[{n:'PALMEIRAS',p:0,c:'#0c7a3c'},{n:'FLAMENGO',p:0,c:'#c0151d'}],digitAt:[99,99],
  rowY:(i,t)=>{const sw=E.io(prog(t,K.virou-72.24-.3,K.virou-72.24+.6));const y0=2.2,y1=-.2;return i===0?lerp(y0,y1,sw):lerp(y1,y0,sw)},
  rowZ:(i,t)=>{const sw=prog(t,K.virou-72.24-.3,K.virou-72.24+.6);return i===1?Math.sin(sw*Math.PI)*2.2:-Math.sin(sw*Math.PI)*.6},
  anim:(rows,t)=>{rows.forEach((o,i)=>{o.badge.visible=true;Wd.setDigit;})},
  cam:(c,t,d)=>{const k=E.io(prog(t,0,d));const a=lerp(-.5,.35,k);look(c,V(Math.sin(a)*17,lerp(5,1.5,k),Math.cos(a)*17),V(0,1,0).add(shake(t,.05)),lerp(-.08,.04,k))}});
B.table3=boardShot({head:'SE O PALMEIRAS VENCER',rows:[{n:'FLAMENGO',p:79,c:'#c0151d'},{n:'PALMEIRAS',p:76,c:'#0c7a3c'}],digitAt:[.15,.25],valAt:(i,t)=>i===1&&t<1.1?73:(i===0?79:76),big:'+3',bigAt:1.4,sub:'FALTAM 2 RODADAS',subAt:K.duas-111.64,
  anim:(rows,t)=>{const dg=rows[1].dg[1];const q=prog(t,1.0,1.35);if(q>0&&q<1){dg.rotation.x=Math.sin(q*Math.PI)*-1.4}},
  cam:(c,t,d)=>{const k=E.io(prog(t,0,d));look(c,V(lerp(8,-5,k),lerp(-1,2,k),lerp(13,17,k)),V(lerp(2,0,k),lerp(-.5,-1.5,k),0).add(shake(t,.04)),lerp(.06,-.03,k))}});

function chalkShot(title,lines,camf,teacher){return (sh)=>{const S=Wd.classroom();const {scene}=S;let tc=null;
  if(teacher){tc=makeChar({team:'TEACH',gray:true,glasses:true,ex:'smile'});tc.g.position.set(9.6,0,2);tc.g.rotation.y=-.6;scene.add(tc.g);
    const stick=mesh(new THREE.CylinderGeometry(.05,.05,3.2,6),toon('#c8a060'),V(0,-1.6,0));tc.arms[1].userData.hand.add(stick)}
  const c=cam(38);return {scene,cam:c,update(t,d){const T=title?{t:title,p:prog(t,.05,.55)}:null;chalkDraw(S.boardTex,T,lines(t),t);if(tc){pose(tc,'stick',t);tc.arms[1].rotation.z=1.2+Math.sin(t*2)*.1}camf(c,t,d)}}}}
const chalkDraw=Wd.chalkDraw;
const T0=id=>TL.shots.find(s=>s.id===id).t0;
B.chalkIf=chalkShot('SE...',(t)=>{const o=T0('chalkIf');return [
  {t:'PAL VENCE',y:340,x:70,s:96,p:prog(t,K.palvence-o-.1,K.palvence-o+.5)},{t:'→ BRIGA CONTINUA',y:480,x:110,s:76,c:'#9be7a8',p:prog(t,K.palvence-o+.5,K.palvence-o+1.2)},
  {t:'PAL NÃO VENCE',y:690,x:70,s:96,p:prog(t,K.qualquer-o-.2,K.qualquer-o+.5)},{t:'→ FLA CAMPEÃO',y:830,x:110,s:76,c:'#ff8f8f',p:prog(t,K.vairio-o-.6,K.vairio-o+.2)},
  {t:'(empate ou vitória)',y:960,x:150,s:54,c:'#d8d2bf',p:prog(t,K.vairio-o+.3,K.vairio-o+.9)}]},
  (c,t,d)=>{const k=E.io(prog(t,0,d));look(c,V(lerp(-9,5,k),lerp(11,8,k),lerp(36,27,k)),V(lerp(-.5,.5,k),lerp(10,7.6,k),0).add(shake(t,.03)),lerp(.05,-.03,k))});
B.chalkFla=chalkShot('FESTA HOJE',(t)=>{const o=T0('chalkFla');return [
  {t:'+6 pontos',y:380,x:80,s:104,p:prog(t,K.mais6-o-.1,K.mais6-o+.6)},{t:'empate basta',y:600,x:80,s:104,p:prog(t,K.empatar-o,K.empatar-o+.7)},
  {t:'última final:',y:820,x:80,s:92,p:prog(t,K.ultima-o,K.ultima-o+.6)},{t:'FLA 2025',y:960,x:140,s:92,c:'#ff8f8f',p:prog(t,K.ultima-o+.6,K.ultima-o+1.1),check:prog(t,K.ultima-o+1.2,K.ultima-o+1.7),cx:760}]},
  (c,t,d)=>{const o=T0('chalkFla');const segs=[0,K.mais6-o-.3,K.empatar-o-.3,K.ultima-o-.3,d];let i=segs.findIndex((s,j)=>t>=s&&t<segs[j+1]);if(i<0)i=3;const q=E.io(prog(t,segs[i],segs[i]+.7));
    const tg=[[V(0,8.6,0),V(-14,6,40)],[V(0,10.6,0),V(-5,10.5,25)],[V(0,8.8,0),V(5,8.6,25)],[V(0,6.6,0),V(-3,6.2,25)]];const prev=tg[Math.max(0,i-1)],cur=tg[i];
    look(c,prev[1].clone().lerp(cur[1],i===0?E.io(prog(t,0,segs[1])):q),prev[0].clone().lerp(cur[0],i===0?E.io(prog(t,0,segs[1])):q).add(shake(t,.03)),Math.sin(t*.7)*.02)},true);
B.chalkPal=chalkShot('ADIA A FESTA',(t)=>{const o=T0('chalkPal');return [
  {t:'joga em casa',y:380,x:80,s:104,p:prog(t,K.casa-o,K.casa-o+.6)},{t:'com a torcida',y:600,x:80,s:104,p:prog(t,K.torcida-o,K.torcida-o+.6)},
  {t:'3 × 0',y:830,x:500,align:'center',s:150,c:'#9be7a8',p:prog(t,K.x3-o+.4,K.x3-o+1.0),circle:prog(t,K.x3-o+2.6,K.x3-o+3.3),cx:500,cw:260},{t:'no Maracanã',y:1010,x:500,align:'center',s:84,p:prog(t,K.x3-o+1.0,K.x3-o+1.8)}]},
  (c,t,d)=>{const o=T0('chalkPal');const segs=[0,K.casa-o-.3,K.torcida-o-.3,K.x3-o,d];let i=segs.findIndex((s,j)=>t>=s&&t<segs[j+1]);if(i<0)i=3;const q=E.io(prog(t,segs[i],segs[i]+.7));
    const tg=[[V(0,8.6,0),V(12,6,40)],[V(0,10.6,0),V(5,10.5,25)],[V(0,8.8,0),V(-5,8.6,25)],[V(0,6,0),V(2,5.8,24)]];const prev=tg[Math.max(0,i-1)],cur=tg[i];const qq=i===0?E.io(prog(t,0,segs[1])):q;
    look(c,prev[1].clone().lerp(cur[1],qq),prev[0].clone().lerp(cur[0],qq).add(shake(t,.03)),-Math.sin(t*.7)*.02)},true);

B.rivalry=(sh)=>{const S=stadiumShot({sky:'night',crowd:Wd.PAL_CROWD,split:Wd.FLA_CROWD,bounceHz:3});const {scene}=S;
  const a=makeChar({team:'PAL',ex:'angry',num:10});a.g.position.set(-1.4,0,0);a.g.rotation.y=Math.PI/2;scene.add(a.g);
  const b=makeChar({team:'FLA',ex:'smug',curly:true,skin:'#8a5a3b',num:10});b.g.position.set(1.4,0,0);b.g.rotation.y=-Math.PI/2;scene.add(b.g);
  const ball=makeBall(.32);ball.position.set(0,.32,0);scene.add(ball);
  const sign=plaque([{t:'A MAIOR RIVALIDADE',c:'#ffffff'},{t:'DA DÉCADA',c:'#ffd23f'}],6,2.4,{bg:'#0d0f1a',border:'#e8c14a',ppu:90,d:.5});sign.position.set(0,7.5,0);scene.add(sign);
  const cf=confetti(260,['#0c7a3c','#ffffff','#d1121b','#141414'],[22,18,22]);scene.add(cf);
  const c=cam(40);const ma=K.maior-sh.t0;
  return {scene,cam:c,update(t,d){S.st.userData.bounce(t);pose(a,'idle',t*3);pose(b,'idle',t*3+1);cf.userData.update(t);
    const q=E.back(prog(t,ma-.3,ma+.4));sign.scale.setScalar(Math.max(.001,q));sign.position.y=7.5+Math.sin(t*2)*.15;
    const ang=lerp(-1.2,1.6,E.io(prog(t,0,d)));const r=lerp(7,11,E.io(prog(t,0,d)));look(c,V(Math.sin(ang)*r,lerp(1.2,3,prog(t,0,d)),Math.cos(ang)*r),V(0,lerp(3,5,prog(t,ma-.5,ma+.5)),0).add(shake(t,.06)));sign.lookAt(c.position)}}};

/* ---------- goal plays ---------- */
function play(o){return (sh)=>{const S=stadiumShot({sky:o.sky||'night',crowd:o.crowd,split:o.split,bounceHz:0,sunPos:V(20,60,30),shadowSize:30,shadowTarget:V(40,0,0)});const {scene}=S;
  const goal=Wd.makeGoal(52.5,1);scene.add(goal);const goal2=Wd.makeGoal(-52.5,-1);goal2.rotation.y=0;scene.add(goal2);
  const ball=makeBall(.34);scene.add(ball);
  const actors={};for(const[k,v]of Object.entries(o.actors)){const ch=makeChar(Object.assign({scale:.85},v));scene.add(ch.g);actors[k]=ch}
  const extras=[];(o.extras||[]).forEach(v=>{const ch=makeChar(Object.assign({scale:.85},v));ch.g.position.copy(v.p);ch.g.rotation.y=v.ry||0;ch.ph=R(0,6);scene.add(ch.g);extras.push(ch)});
  const cf=confetti(380,o.confColors||['#fff'],[30,22,30],V(40,0,0));cf.visible=false;scene.add(cf);
  const sc=plaque(o.title,9,2.6,{bg:'#0d0f1a',border:'#e8c14a',ppu:90,d:.5});scene.add(sc);
  const led=o.led?Wd.ledBoard(11,6):null;if(led){led.position.set(58,19,-30);led.rotation.y=-Math.PI/2+.5;scene.add(led);led.userData.n=V(Math.sin(led.rotation.y),0,Math.cos(led.rotation.y))}
  const c=cam(40);const ctx={scene,actors,ball,goal,c,cf,sc,led,extras,S};if(o.init)o.init(ctx);
  return {scene,cam:c,update(t,d){S.st.userData.bounce(t);extras.forEach(e=>pose(e,e.pose||'run',t*7+e.ph));o.update(ctx,t,d)}}}}
const bez=(a,b,c,t)=>a.clone().multiplyScalar((1-t)*(1-t)).add(b.clone().multiplyScalar(2*(1-t)*t)).add(c.clone().multiplyScalar(t*t));
function faceTo(ch,x,z){ch.g.rotation.y=Math.atan2(x-ch.g.position.x,z-ch.g.position.z)}

B.final21=play({crowd:Wd.PAL_CROWD,split:Wd.FLA_CROWD,confColors:['#0c7a3c','#ffffff','#ffd23f'],title:[{t:'LIBERTADORES 2021',c:'#ffd23f'},{t:'MONTEVIDÉU · FINAL',c:'#fff'}],led:true,
  actors:{fla:{team:'FLA',curly:true,skin:'#b07a50',num:5},dey:{team:'PAL',num:9,skin:'#d9a173',hairC:'#111'},gk:{team:'GK2',skin:'#f2c49b'},fla2:{team:'FLA',num:3}},
  extras:[{team:'PAL',p:V(20,0,10),ry:Math.PI/2},{team:'FLA',p:V(28,0,-8),ry:-Math.PI/2},{team:'PAL',p:V(14,0,-12),ry:Math.PI/2},{team:'FLA',p:V(34,0,6),ry:-Math.PI/2}],
  update(x,t,d){const o=40.36;const tP=K.prorrog-o,tE=K.erro-o,tG=K.gol21-o,tC=K.camp21-o;const {fla,dey,gk,fla2}=x.actors;const b=x.ball;
    // timeline of play in "play time" (with slow-mo near shot)
    const pt=t;
    // positions
    const steal=tE+.5,shot=tG-.42,arrive=tG+.12;
    gk.g.position.set(51,0,0);faceTo(gk,0,0);
    fla2.g.position.set(lerp(30,38,prog(pt,0,shot)),0,lerp(4,2,prog(pt,0,shot)));faceTo(fla2,dey.g.position.x,dey.g.position.z);pose(fla2,'run',pt*8);
    // fla defender with ball near own box (defending right goal) walking back-pass -> error
    if(pt<steal){fla.g.position.set(lerp(26,30,prog(pt,0,steal)),0,lerp(-6,-2,prog(pt,0,steal)));faceTo(fla,20,0);pose(fla,pt<tE?'walk':'run',pt*7);
      b.position.set(fla.g.position.x-.9+Math.sin(pt*8)*.15,.34,fla.g.position.z+.2);dey.g.position.set(lerp(14,27.5,E.i(prog(pt,tE-1,steal))),0,lerp(4,-1.8,prog(pt,tE-1,steal)));faceTo(dey,b.position.x,b.position.z);pose(dey,'run',pt*10)}
    else if(pt<shot){const q=prog(pt,steal,shot);fla.g.position.set(30,0,-2);fla.g.rotation.x=0;pose(fla,'fall');fla.g.position.y=0;fla.torso.rotation.x=-.9*Math.min(1,q*3);
      dey.g.position.set(lerp(27.5,38,q),0,lerp(-1.8,-3,q));dey.g.rotation.y=Math.PI/2;pose(dey,'run',pt*11);b.position.set(dey.g.position.x+1.1,.34,dey.g.position.z+.1)}
    else{const q=clamp((pt-shot)/(arrive-shot));pose(dey,q<.2?'kick':'fist',0,E.o(clamp(q*5)));dey.g.position.set(38,0,-3);
      if(pt<arrive){b.position.copy(bez(V(39.2,.34,-2.9),V(47,2.4,.8),V(54.6,2.2,2.8),E.o(q)))}else{const r=clamp((pt-arrive)/.6);b.position.set(54.6-r*.6,lerp(2.2,.34,E.bounce(r)),2.8)}
      pose(fla,'sad');fla.torso.rotation.x=-.9;}
    b.rotation.x+=.25;b.rotation.z+=.15;
    // keeper dive
    const dq=E.o(prog(pt,shot+.1,arrive+.1));gk.g.position.set(51-dq*.3,dq*1.2*(1-dq)*3,dq*2.4);gk.g.rotation.z=-dq*1.35;pose(gk,dq>0?'dive':'idle',t*3);
    if(pt>=arrive)x.goal.userData.bulge(2.8,2.2,Math.max(0,1.4*Math.exp(-(pt-arrive)*3)*Math.sin((pt-arrive)*14+1.5)));
    // celebration
    if(t>tC-.2){const cq=t-(tC-.2);dey.g.position.set(38+cq*2.5,0,-3+cq*1.2);dey.g.rotation.y=Math.PI*.15;pose(dey,'celebrate',cq*9);x.cf.visible=true;x.cf.userData.update(cq,1.2);setExpr(dey,'happy')} else setExpr(dey,pt>shot?'wide':'neutral');
    setExpr(fla,pt>steal?'wide':'neutral');
    // title + LED
    x.sc.position.set(36,6,-1);x.sc.scale.setScalar(Math.max(.001,E.back(prog(t,.2,.7))*(1-prog(t,1.7,1.9))));
    if(x.led)Wd.ledDraw(x.led.userData.tex,t<arrive+.2?[{t:'PAL 1 × 1 FLA',s:110},{t:'PRORROGAÇÃO',s:70}]:[{t:'PAL 2 × 1 FLA',s:110},{t:'GOL!',s:90,c:'#7dff9a'}]);
    FLASH=FL(t,arrive+.05,.2,.4);
    // CAMERA
    const c=x.c;let fov=40;
    if(t<tP){const k=E.io(prog(t,0,tP));look(c,V(lerp(70,44,k),lerp(40,9,k),lerp(-30,22,k)),V(lerp(40,30,k),lerp(4,2,k),lerp(0,-2,k)).add(shake(t,.08)))}
    else if(t<tE-.05){const k=E.io(prog(t,tP,tE));look(c,x.led.position.clone().addScaledVector(x.led.userData.n,lerp(26,20,k)).add(V(lerp(-4,2,k),lerp(-6,-3,k),0)),x.led.position.clone().add(shake(t,.1)));fov=40}
    else if(t<shot-.2){const k=prog(t,tE,shot-.2);const p=b.position;look(c,V(p.x-6+k*2,3.2,p.z+12-k*2),V(p.x+2,1.2,p.z).add(shake(t,.1)),-.03);fov=38}
    else if(t<tC-.2){const k=E.o(prog(t,shot-.2,tC-.2));look(c,V(lerp(33,40,k),lerp(2.4,2.2,k),lerp(-7.5,-6,k)),V(lerp(50,54,k),1.6,lerp(0,2.4,k)).add(shake(t,.06)),.04);fov=lerp(36,30,k)}
    else{const k=E.o(prog(t,tC-.2,d));const p=dey.g.position;const a=lerp(.4,-.6,k);look(c,V(p.x+Math.sin(a)*7,lerp(1.2,3.5,k),p.z+Math.cos(a)*7),V(p.x,2.4,p.z).add(shake(t,.12)),Math.sin(t*3)*.03);fov=38}
    c.fov=fov;c.updateProjectionMatrix()}});

B.final25=play({crowd:Wd.FLA_CROWD,split:Wd.PAL_CROWD,confColors:['#d1121b','#141414','#ffd23f'],title:[{t:'LIBERTADORES 2025',c:'#ffd23f'},{t:'LIMA · FINAL',c:'#fff'}],led:true,
  actors:{kick:{team:'FLA',num:10,skin:'#f2c49b',hairC:'#6b4a2a'},head:{team:'FLA',num:13,skin:'#8a5a3b',hair:'none'},def:{team:'PAL',num:4},gk:{team:'GK1'},cap:{team:'FLA',num:8,curly:true,skin:'#b07a50'}},
  extras:[{team:'PAL',p:V(46,0,-3),ry:-Math.PI/2,pose:'idle'},{team:'FLA',p:V(44,0,4),ry:Math.PI/2,pose:'idle'},{team:'PAL',p:V(47,0,5),ry:-Math.PI/2,pose:'idle'},{team:'PAL',p:V(45,0,-6),ry:-Math.PI/2,pose:'idle'}],
  init(x){x.tro=Wd.trophy(ENV);x.tro.scale.setScalar(.55);x.scene.add(x.tro);x.tro.visible=false;
    x.pod=OL(mesh(new THREE.BoxGeometry(10,1,4),toon('#1b2340'),V(30,.5,0),{cast:1}),.04);x.pod.visible=false;x.scene.add(x.pod);
    x.fw=[];for(let i=0;i<6;i++){const g_=glow(['#ff4040','#ffd23f','#ffffff'][i%3],1,1);g_.position.set(20+i*4,25,-25);x.scene.add(g_);x.fw.push(g_)}},
  update(x,t,d){const o=49.92;const tL=K.lima-o,tH=K.cabeca-o,t10=K.umazero-o,tLv=K.levantou-o;const {kick,head,def,gk,cap}=x.actors;const b=x.ball;
    const kickT=tL+.35,hitT=tH+.55,inT=hitT+.5,tIn=hitT+.955;const st=t<hitT-.3?t:(t<hitT+.4?hitT-.3+(t-hitT+.3)*.35:hitT-.055+(t-hitT-.4));
    kick.g.position.set(52.2,0,33.4);faceTo(kick,44,0);pose(kick,st<kickT?'idle':'kick',st*3,E.o(prog(st,kickT,kickT+.3)));
    gk.g.position.set(51.2,0,0);faceTo(gk,40,0);
    // header player runs in and jumps
    const hq=prog(st,kickT,hitT);head.g.position.set(lerp(40,45.6,E.io(hq)),0,lerp(-4,1.4,hq));
    if(st<hitT-.25){faceTo(head,52,1);pose(head,'run',st*10)}else{const jq=prog(st,hitT-.25,hitT+.35);head.g.position.y=Math.sin(jq*Math.PI)*1.5;head.g.rotation.y=Math.PI/2+.3;pose(head,'header',0,E.io(prog(st,hitT-.25,hitT)))}
    def.g.position.set(lerp(43,46.4,hq),0,lerp(-3,-.8,hq));faceTo(def,52,0);pose(def,st<hitT?'run':'sad',st*9);def.g.position.y=st>hitT-.3&&st<hitT+.3?Math.sin(prog(st,hitT-.3,hitT+.3)*Math.PI)*.9:0;
    if(st<kickT)b.position.set(51.9,.34,33.2);
    else if(st<hitT){const q=prog(st,kickT,hitT);b.position.copy(bez(V(51.9,.34,33.2),V(52,9,14),V(46.1,3.65,1.5),q))}
    else if(st<inT){const q=prog(st,hitT,inT);b.position.copy(bez(V(46.1,3.65,1.5),V(50,2.8,2.8),V(54.6,.9,4.2),q))}
    else{const r=clamp((st-inT)/.6);b.position.set(54.6-r*.6,lerp(.9,.34,E.bounce(r)),4.2)}
    b.rotation.x+=.3;b.rotation.y+=.2;
    const dq=E.o(prog(st,hitT+.05,inT+.1));gk.g.position.z=dq*2.8;gk.g.position.y=Math.sin(dq*Math.PI)*.9;gk.g.rotation.z=-dq*1.3;pose(gk,dq>0?'dive':'idle',t*3);
    if(st>=inT)x.goal.userData.bulge(4.2,.9,Math.max(0,1.2*Math.exp(-(st-inT)*3)*Math.sin((st-inT)*14+1.5)));
    setExpr(head,st>inT?'happy':'neutral');if(st>inT+.3&&t<tLv-.3){pose(head,'celebrate',t*9);head.g.position.set(45.6+(t-inT-.3)*1.5,0,1.4);head.g.rotation.y=-Math.PI/2}
    if(x.led)Wd.ledDraw(x.led.userData.tex,t<tIn+.15?[{t:'FLA 0 × 0 PAL',s:110},{t:'2º TEMPO',s:70}]:[{t:'FLA 1 × 0 PAL',s:110},{t:'GOL!',s:90,c:'#ff6b6b'}]);
    FLASH=FL(t,tIn+.05,.2,.4);
    x.sc.position.set(40,6,6);x.sc.scale.setScalar(Math.max(.001,E.back(prog(t,.2,.7))*(1-prog(t,tL-.4,tL-.2))));
    // trophy lift
    const lift=t>=tLv-.3;x.tro.visible=lift;x.pod.visible=lift;cap.g.visible=lift;x.extras.forEach(e=>e.g.visible=!lift);kick.g.visible=gk.g.visible=def.g.visible=!lift||false;
    if(lift){const lq=t-(tLv-.3);cap.g.position.set(30,1,0);cap.g.rotation.y=0;pose(cap,'lift',lq*3);setExpr(cap,'happy');x.tro.position.set(30,1+lerp(3.2,4.7,E.o(prog(lq,0,.8))),.3);x.tro.rotation.y=lq;
      head.g.position.set(27.6,1,0);head.g.rotation.y=.3;pose(head,'celebrate',lq*8);x.cf.visible=true;x.cf.position.set(30,0,0);x.cf.userData.update(lq,1.2);
      x.fw.forEach((f,i)=>{const fq=((lq*1.3+i*.37)%1);f.scale.setScalar(fq*16);f.material.opacity=(1-fq)})}else x.fw.forEach(f=>f.material.opacity=0);
    const c=x.c;let fov=40;
    if(t<tL-.2){const k=E.io(prog(t,0,tL-.2));look(c,V(lerp(-10,22,k),lerp(45,14,k),lerp(-50,30,k)),V(lerp(20,44,k),2,lerp(0,10,k)).add(shake(t,.08)))}
    else if(t<tH){const k=E.io(prog(t,tL-.2,tH));look(c,V(lerp(41,38,k),lerp(3.5,5,k),lerp(25,18,k)),V(52,1.5,33).lerp(b.position,clamp(k*1.3)).add(shake(t,.08)),.03);fov=lerp(40,44,k)}
    else if(t<t10-.1){const k=E.o(prog(t,tH,t10-.1));look(c,V(lerp(31,35,k),lerp(3,2.6,k),lerp(5,4,k)),V(lerp(46,51,k),lerp(3,2,k),lerp(2,3,k)).add(shake(t,.06)),-.03);fov=38}
    else if(t<tLv-.3){const k=E.io(prog(t,t10-.1,tLv-.3));look(c,x.led.position.clone().addScaledVector(x.led.userData.n,lerp(28,21,k)).add(V(0,lerp(-7,-3,k),0)),x.led.position.clone().add(shake(t,.08)));fov=40}
    else{const k=E.o(prog(t,tLv-.3,d));const a=lerp(-.5,.4,k);look(c,V(30+Math.sin(a)*12,lerp(2,6,k),Math.cos(a)*12),V(30,lerp(4,5.5,k),0).add(shake(t,.1)),Math.sin(t*2)*.02);fov=40}
    c.fov=fov;c.updateProjectionMatrix()}});

B.scale=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#120d0a');scene.environment=ENV;const bl=Wd.balance(ENV);scene.add(bl);
  const fl=mesh(new THREE.CircleGeometry(40,48),new THREE.MeshStandardMaterial({color:'#2a1a10',roughness:.6}),null,{recv:1});fl.rotation.x=-Math.PI/2;scene.add(fl);
  const sp=new THREE.SpotLight('#ffe9c0',900,60,.6,.5,1.3);sp.position.set(0,24,10);sp.castShadow=true;scene.add(sp);scene.add(new THREE.AmbientLight('#fff',.25));
  const balls=bl.userData.pans.map((p,i)=>{const s=OL(mesh(new THREE.SphereGeometry(1.1,24,18),toon(i?'#d1121b':'#0c7a3c',i?ctex(64,64,(c,w,h)=>{c.fillStyle='#d1121b';c.fillRect(0,0,w,h);c.fillStyle='#141414';for(let y=0;y<h;y+=16)c.fillRect(0,y,w,8)}):null),V(0,-2.5,0)),.04);p.add(s);
    const lb=plaque([i?'2025':'2021'],2.2,1,{bg:'#14182a',ppu:80});lb.position.set(0,-.4,1.3);p.add(lb);return s});
  const res=plaque([{t:'1 × 1',c:'#ffd23f'}],5,2,{bg:'#14182a',ppu:90});res.position.set(0,12.6,0);scene.add(res);
  const c=cam(36);return {scene,cam:c,update(t,d){const a=t<.35?lerp(0,.25,E.o(t/.35)):t<.8?lerp(.25,-.25,E.io(prog(t,.35,.8))):lerp(-.25,0,E.el(prog(t,.8,1.5)));bl.userData.beam.rotation.z=a;bl.userData.pans.forEach(p=>p.rotation.z=-a);
    res.scale.setScalar(Math.max(.001,E.back(prog(t,.85,1.2))));const k=E.io(prog(t,0,d));look(c,V(lerp(8,-4,k),lerp(6,9,k),lerp(20,19,k)),V(0,lerp(6,8.5,k),0).add(shake(t,.04)))}}};

B.may=play({sky:'day',crowd:Wd.FLA_CROWD,confColors:['#0c7a3c','#fff'],title:[{t:'MARACANÃ · MAIO',c:'#ffd23f'},{t:'BRASILEIRÃO 2026',c:'#fff'}],led:true,
  actors:{s1:{team:'PAL',num:7,skin:'#d9a173'},s2:{team:'PAL',num:9,curly:true,skin:'#8a5a3b'},gk:{team:'GK2'},d1:{team:'FLA',num:4}},
  update(x,t,d){const o=64.72;const tR=K.rio-o,tT=K.tres-o;const {s1,s2,gk,d1}=x.actors;const b=x.ball;
    gk.g.position.set(51,0,0);faceTo(gk,0,0);
    // goal sequence: shot at tR+0.6 from (36,-6) low into corner
    const sh_=tR-.1,ar=sh_+.6;s1.g.position.set(lerp(28,36,E.io(prog(t,0,sh_))),0,-6);faceTo(s1,52,0);pose(s1,t<sh_?'run':'kick',t*10,E.o(prog(t,sh_,sh_+.25)));
    d1.g.position.set(lerp(33,37.5,prog(t,0,sh_)),0,-3.5);faceTo(d1,s1.g.position.x,s1.g.position.z);pose(d1,'run',t*9);
    s2.g.position.set(40,0,6);faceTo(s2,52,0);pose(s2,'idle',t*3);
    if(t<sh_)b.position.set(s1.g.position.x+1,.34,-5.9);else if(t<ar){const q=prog(t,sh_,ar);b.position.copy(bez(V(37,.34,-5.9),V(45,1.2,-5),V(54.6,.6,-4.2),q))}else{b.position.set(54.6,.34,-4.2)}
    b.rotation.x+=.3;const dq=E.o(prog(t,sh_+.1,ar+.1));gk.g.position.z=-dq*2.6;gk.g.rotation.z=dq*1.3;pose(gk,dq>0?'dive':'idle');
    if(t>=ar)x.goal.userData.bulge(-4.2,.6,Math.max(0,1.2*Math.exp(-(t-ar)*3)*Math.sin((t-ar)*14+1.5)));
    const n=t<ar?0:t<tT+.25?1:t<tT+.55?2:3;Wd.ledDraw(x.led.userData.tex,[{t:`FLA 0 × ${n} PAL`,s:110},{t:'MARACANÃ',s:66}]);
    FLASH=Math.max(FL(t,ar,.2,.6),FL(t,tT+.25,.15,.6),FL(t,tT+.55,.15,.6),FL(t,tT+.85,.2,.8));
    x.sc.position.set(20,7,0);x.sc.scale.setScalar(Math.max(.001,E.back(prog(t,.1,.5))*(1-prog(t,tR-.5,tR-.3))));
    const c=x.c;let fov=40;
    if(t<tR-.3){const k=E.io(prog(t,0,tR-.3));look(c,V(lerp(-10,10,k),lerp(50,10,k),lerp(55,18,k)),V(20,lerp(3,6.5,k),0).add(shake(t,.08)))}
    else if(t<tT){const k=prog(t,tR-.3,tT);look(c,V(lerp(31,40,E.o(k)),lerp(2.2,2,k),lerp(-13,-11,k)),V(lerp(38,52,E.o(k)),1.3,lerp(-5,-3,k)).add(shake(t,.1)),.03);fov=38}
    else{const k=E.o(prog(t,tT,d));look(c,x.led.position.clone().addScaledVector(x.led.userData.n,lerp(30,20,k)).add(V(lerp(3,0,k),lerp(-8,-3,k),0)),x.led.position.clone().add(shake(t,.1+FLASH*.5)));fov=40}
    c.fov=fov;c.updateProjectionMatrix()}});

B.sadfan=(sh)=>{const S=Wd.bar({lampX:1,lampZ:2});const {scene}=S;const f=makeChar({team:'FLA',ex:'sad',scarf:'#141414',skin:'#d9a173'});f.g.position.set(1,0,1.5);f.g.rotation.y=-.35;scene.add(f.g);
  Wd.drawTV(S.tvTex,(c,w,h)=>Wd.tvPitch(c,w,h,'FLA 0 × 3 PAL','FIM DE JOGO'));
  const c=cam(36);return {scene,cam:c,update(t,d){pose(f,'sad',t);f.headG.rotation.x=.35+Math.sin(t*1.2)*.03;const k=E.io(prog(t,0,d));
    look(c,V(lerp(0,1.5,k),lerp(4.6,3.8,k),lerp(12,7.5,k)),V(1,lerp(3.6,3.3,k),1.5).add(shake(t,.025)),lerp(.06,.0,k))}}};

B.referee=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#0a0c12');
  const len=60;const tun=new THREE.Group();scene.add(tun);const wallM=toon('#5b6475');
  const fl=mesh(new THREE.PlaneGeometry(8,len),toon('#3a404d'),V(0,0,-len/2+6),{recv:1});fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;tun.add(fl);
  for(const s of[-1,1]){const w=mesh(new THREE.PlaneGeometry(len,7),wallM,V(s*4,3.5,-len/2+6),{recv:1});w.rotation.y=-s*Math.PI/2;tun.add(w)}
  const ce=mesh(new THREE.PlaneGeometry(8,len),toon('#2c313c'),V(0,7,-len/2+6));ce.rotation.x=Math.PI/2;tun.add(ce);
  for(let i=0;i<10;i++){const z=6-i*6;const l=mesh(new THREE.BoxGeometry(3,.12,.6),new THREE.MeshBasicMaterial({color:'#eaf6ff',toneMapped:false}),V(0,6.9,z));tun.add(l);const gg=glow('#dff2ff',5,.5);gg.position.set(0,6.4,z);tun.add(gg);
    const pl=new THREE.PointLight('#dff2ff',14,10,1.6);pl.position.set(0,6.2,z);if(i%2==0)tun.add(pl)}
  const exitG=glow('#ffffff',26,1);exitG.position.set(0,3.5,-len+7);tun.add(exitG);scene.add(new THREE.AmbientLight('#8fa2c8',.5));
  const r=makeChar({team:'REF',ref:true,ex:'closed'});r.g.position.set(0,0,-8);scene.add(r.g);
  const np=plaque([{t:'RODRIGO JOSÉ PEREIRA DE LIMA',c:'#fff'},{t:'ÁRBITRO · PE',c:'#ffd23f'}],4,1.05,{bg:'#0d0f1a',border:'#e8c14a',ppu:100,d:.3});scene.add(np);
  const c=cam(38);const tr=K.rodrigo-sh.t0;
  return {scene,cam:c,update(t,d){r.g.position.z=-14+t*2.2;pose(r,t<tr+.6?'walk':'whistle',t*6);setExpr(r,t<tr+.6?'closed':'angry');
    const z=r.g.position.z;look(c,V(lerp(1.6,-1.2,prog(t,0,d)),lerp(2.4,2.8,prog(t,0,d)),z+lerp(8,6,E.io(prog(t,0,d)))),V(0,2.4,z).add(shake(t,.05)),Math.sin(t*1.5)*.02);
    np.position.set(lerp(-6,0,E.back(prog(t,tr,tr+.5))),.8,z+1.2);np.lookAt(c.position);np.visible=t>tr}}};

B.var=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#05070d');scene.add(new THREE.AmbientLight('#5070a0',.5));
  const mons=[];for(let r=0;r<3;r++)for(let i=0;i<4;i++){const tex=ctex(320,180,(c,w,h)=>{Wd.tvPitch(c,w,h,null,null);c.strokeStyle='#ffd23f';c.lineWidth=4;c.beginPath();c.moveTo(w*(.2+i*.15),h*.4);c.lineTo(w*(.2+i*.15),h);c.stroke();c.fillStyle='#ff3b3b';c.beginPath();c.arc(w-18,18,8,0,7);c.fill();fitText(c,'CAM '+(r*4+i+1),40,h-16,70,22,'#fff')});
    const m=new THREE.Group();m.position.set(-6.3+i*4.2,1.8+r*2.6,-.2*Math.abs(i-1.5));m.rotation.y=(1.5-i)*.12;m.add(OL(mesh(new THREE.BoxGeometry(4,2.4,.25),toon('#111')),.03));m.add(mesh(new THREE.PlaneGeometry(3.7,2.1),new THREE.MeshBasicMaterial({map:tex,toneMapped:false}),V(0,0,.14)));scene.add(m);mons.push(m)}
  const desk=OL(mesh(new THREE.BoxGeometry(20,1,4),toon('#1d2230'),V(0,.3,3),{recv:1,cast:1}),.04);scene.add(desk);
  const op=makeChar({team:'REF',ex:'closed',glasses:true});op.g.position.set(0,-1.4,6.5);op.g.rotation.y=Math.PI;scene.add(op.g);
  const varl=plaque([{t:'VAR',c:'#ffd23f'}],3,1.3,{bg:'#c0392b',border:'#fff',ppu:100});varl.position.set(0,9.6,0);scene.add(varl);
  const np=plaque([{t:'CHARLY WENDY STRAUB DERETTI',c:'#fff'},{t:'VAR · SC',c:'#ffd23f'}],4.2,1.1,{bg:'#0d0f1a',border:'#e8c14a',ppu:100,d:.3});scene.add(np);
  const scr=glow('#7fb2ff',26,.25);scr.position.set(0,4,1);scene.add(scr);const c=cam(40);
  return {scene,cam:c,update(t,d){pose(op,'idle',t*2);const k=E.io(prog(t,0,d));look(c,V(lerp(8,-3,k),lerp(5,4.5,k),lerp(13,12,k)),V(lerp(1,-1,k),lerp(5,4.6,k),0).add(shake(t,.04)),lerp(-.05,.03,k));
    np.position.set(lerp(-9,.6,E.back(prog(t,.4,.9))),2.4,4);np.lookAt(c.position)}}};

B.covered=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#06060a');scene.environment=ENV;const tr=Wd.trophy(ENV);tr.scale.setScalar(1.3);scene.add(tr);
  const fl=mesh(new THREE.CircleGeometry(30,64),new THREE.MeshStandardMaterial({color:'#111116',roughness:.25,metalness:.6}),null,{recv:1});fl.rotation.x=-Math.PI/2;scene.add(fl);
  const sp=new THREE.SpotLight('#fff3d0',900,60,.38,.6,1.4);sp.position.set(0,22,4);sp.target=tr;sp.castShadow=true;scene.add(sp);scene.add(new THREE.AmbientLight('#fff',.12));
  const r1=new THREE.PointLight('#ff2030',140,30,1.4);r1.position.set(8,5,4);scene.add(r1);
  const prof=[];for(let i=0;i<=24;i++){const y=7.4-i*.32;const rad=i<3?Math.sin(i/3*Math.PI/2)*1.4:1.4+((i-3)/21)*2.9;prof.push(new THREE.Vector2(rad,y))}
  const clothG=new THREE.LatheGeometry(prof,64);const p=clothG.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i),y=p.getY(i);const a=Math.atan2(z,x);const w=Math.sin(a*9)*.18*(1-y/7.4)+Math.sin(a*4+1)*.1;p.setX(i,x*(1+w*.3));p.setZ(i,z*(1+w*.3))}clothG.computeVertexNormals();
  const cloth=OL(mesh(clothG,toon('#0c7a3c',null,{side:THREE.DoubleSide}),null,{cast:1}),.04);scene.add(cloth);
  const c=cam(34);const tD=K.depois-sh.t0;
  return {scene,cam:c,update(t,d){const q=E.bounce(prog(t,tD-1,tD-.2));cloth.position.y=lerp(14,-.2,q);cloth.scale.set(lerp(.6,1,q),lerp(.8,1,q),lerp(.6,1,q));cloth.rotation.y=t*.1;
    const a=lerp(.8,-.6,E.io(prog(t,0,d)));look(c,V(Math.sin(a)*14,lerp(3,6,prog(t,0,d)),Math.cos(a)*14),V(0,lerp(4.4,3.4,prog(t,0,d)),0).add(shake(t,.03)))}}};

B.coverEyes=(sh)=>{const S=stadiumShot({sky:'night',crowd:Wd.PAL_CROWD,bounceHz:0,shadowTarget:V(0,0,50)});const {scene}=S;
  const f=makeChar({team:'PAL',ex:'sad',sweat:true});f.g.position.set(0,2+28*(57.2-54)/38,57.2);f.g.rotation.y=Math.PI;scene.add(f.g);
  const nb=[];for(let i=0;i<6;i++){const n=makeChar({team:'PAL',ex:i%2?'wide':'sad',skin:['#f2c49b','#d9a173','#b07a50'][i%3],curly:i%2==0,scale:.95});{const zz=57.5+(i%2)*1.6;n.g.position.set(-5+i*2+(i>2?2:0),2+28*(zz-54)/38,zz)};n.g.rotation.y=Math.PI;scene.add(n.g);nb.push(n)}
  const players=[];for(let i=0;i<6;i++){const p=makeChar({team:'FLA',ex:'happy',curly:i%2==0,skin:['#f2c49b','#b07a50','#8a5a3b'][i%3],scale:.85});p.g.position.set(-8+i*3,0,10+R(-2,2));p.ph=R(0,6);scene.add(p.g);players.push(p)}
  const cf=confetti(450,['#d1121b','#141414','#ffd23f'],[25,20,30],V(0,0,30));scene.add(cf);
  const c=cam(38);return {scene,cam:c,update(t,d){pose(f,'eyes',t);nb.forEach((n,i)=>pose(n,i%2?'idle':'sad',t*2+i));players.forEach(p=>pose(p,'jump',t*7+p.ph));cf.userData.update(t,1.1);
    const k=E.io(prog(t,0,d));const target=V(0,lerp(4,7.1,k),lerp(20,57,k));look(c,V(lerp(10,1.2,k),lerp(2,7.8,k),lerp(0,49.5,k)),target.add(shake(t,.05)),lerp(.08,-.02,k));c.fov=lerp(50,36,k);c.updateProjectionMatrix()}}};

B.flaHappy=(sh)=>{const S=Wd.bar({lampX:0,lampZ:2});const {scene}=S;const f=makeChar({team:'FLA',ex:'happy',curly:true,skin:'#b07a50',scarf:'#d1121b'});f.g.position.set(0,0,1.6);scene.add(f.g);
  const f2=makeChar({team:'FLA',ex:'grin',skin:'#f2c49b'});f2.g.position.set(-3.5,0,.2);f2.g.rotation.y=.4;scene.add(f2.g);
  Wd.drawTV(S.tvTex,(c,w,h)=>Wd.tvPitch(c,w,h,'FLA CAMPEÃO?','AO VIVO'));const cf=confetti(260,['#d1121b','#141414','#ffd23f'],[8,10,6],V(0,0,2));scene.add(cf);
  const c=cam(38);return {scene,cam:c,update(t,d){pose(f,'jump',t*7);pose(f2,'celebrate',t*6+1);cf.userData.update(t,.8);const a=lerp(-.5,.5,E.io(prog(t,0,d)));
    look(c,V(Math.sin(a)*9,lerp(2.4,3.6,prog(t,0,d)),Math.cos(a)*9+1.6),V(0,3.6,1.6).add(shake(t,.12,1.6)),Math.sin(t*2.5)*.05)}}};

B.palSmug=(sh)=>{const S=Wd.bar({lampX:0,lampZ:2});const {scene}=S;const f=makeChar({team:'PAL',ex:'smug',scarf:'#0c7a3c'});f.g.position.set(0,0,1.6);f.g.rotation.y=-.15;scene.add(f.g);
  Wd.drawTV(S.tvTex,(c,w,h)=>Wd.tvPitch(c,w,h,'PAL × FLA','HOJE · 16H30'));
  const c=cam(36);return {scene,cam:c,update(t,d){pose(f,'cross',t);f.headG.rotation.z=.08+Math.sin(t)*.02;const k=E.io(prog(t,0,d));
    look(c,V(lerp(4,1,k),lerp(2.2,3.2,k),lerp(13,7.2,k)),V(0,lerp(3.4,4.1,k),1.6).add(shake(t,.02)),lerp(-.12,-.04,k))}}};

B.clock=(sh)=>{const scene=new THREE.Scene();scene.background=new THREE.Color('#2a1a10');const wall=mesh(new THREE.PlaneGeometry(80,60),toon('#c9783c'),V(0,0,-1),{recv:1});scene.add(wall);
  const ck=Wd.bigClock();scene.add(ck);const sp=new THREE.SpotLight('#ffe9c0',900,60,.6,.5,1.2);sp.position.set(-6,10,16);sp.castShadow=true;scene.add(sp);scene.add(new THREE.AmbientLight('#ffd9b0',.5));
  const p1=plaque([{t:'90 MIN',c:'#ffd23f'}],5,1.6,{bg:'#14182a',ppu:90});p1.position.set(-3.4,-6.8,1.5);scene.add(p1);const p2=plaque([{t:'6 PONTOS',c:'#ffffff'}],5.6,1.6,{bg:'#c0392b',border:'#fff',ppu:90});p2.position.set(3.2,-6.8,1.5);scene.add(p2);
  const c=cam(36);const t90=K.n90-sh.t0,t6=K.seisp-sh.t0;
  return {scene,cam:c,update(t,d){const sp_=E.o(prog(t,0,.9));const mins=lerp(16*60+5-90,16*60+30,sp_)+t*.05;const U=ck.userData;U.hour.rotation.z=-(mins/720)*Math.PI*2;U.min.rotation.z=-((mins%60)/60)*Math.PI*2;U.sec.rotation.z=-Math.floor(t*2)/2*Math.PI*2/60*6;
    p1.scale.setScalar(Math.max(.001,E.back(prog(t,t90,t90+.4))));p2.scale.setScalar(Math.max(.001,E.back(prog(t,t6,t6+.4))));
    const k=E.io(prog(t,0,d));look(c,V(lerp(-6,2,k),lerp(-2,-1.5,k),lerp(20,24,k)),V(0,lerp(0,-1.8,k),0).add(shake(t,.03)),lerp(.1,-.02,k))}}};

B.endcard=(sh)=>{const scene=new THREE.Scene();const raysTex=ctex(1024,1024,(c,w,h)=>{c.fillStyle='#ffc82e';c.fillRect(0,0,w,h);c.translate(w/2,h/2);for(let i=0;i<24;i++){c.rotate(Math.PI/12);c.fillStyle=i%2?'#ffb300':'#ffd54a';c.beginPath();c.moveTo(0,0);c.lineTo(900,-120);c.lineTo(900,120);c.fill()}});
  const bg=mesh(new THREE.PlaneGeometry(90,90),new THREE.MeshBasicMaterial({map:raysTex,toneMapped:false}),V(0,6,-8));scene.add(bg);
  scene.add(new THREE.HemisphereLight('#fff6e0','#c08a2a',1.6));const d=new THREE.DirectionalLight('#fff',1.4);d.position.set(4,10,12);d.castShadow=true;scene.add(d);
  const floor=mesh(new THREE.BoxGeometry(60,8,10),toon('#1b2340'),V(0,-4,1),{recv:1});floor.receiveShadow=true;scene.add(floor);const rim=mesh(new THREE.BoxGeometry(40,.25,.2),toon('#d1121b'),V(0,.05,6.05));scene.add(rim);
  const sign=new THREE.Group();scene.add(sign);const pl=plaque([{t:'FLA CAMPEÃO HOJE',c:'#fff'},{t:'OU PALMEIRAS ADIA?',c:'#ffd23f'}],8.4,3.2,{bg:'#1b2340',border:'#e8c14a',ppu:90,d:.6});pl.position.y=-3;sign.add(pl);
  for(const s of[-1,1]){const ch=mesh(new THREE.CylinderGeometry(.06,.06,8,6),toon('#555'),V(s*3.2,1,0));sign.add(ch)}sign.position.set(0,13.5,0);
  const a=makeChar({team:'PAL',ex:'smug'});a.g.position.set(-2.7,0,1);a.g.rotation.y=.25;scene.add(a.g);const b=makeChar({team:'FLA',ex:'happy',curly:true,skin:'#b07a50'});b.g.position.set(2.7,0,1);b.g.rotation.y=-.25;scene.add(b.g);
  const tr=Wd.trophy(ENV);tr.scale.setScalar(.6);tr.position.set(0,0,2);scene.add(tr);
  const bub=plaque([{t:'COMENTA AÍ',c:'#c0392b'}],3.6,1.25,{bg:'#ffffff',fg:'#c0392b',border:'#16161c',ppu:100});scene.add(bub);
  const sub=plaque([{t:'INSCREVA-SE',c:'#fff'}],3.4,1,{bg:'#d1121b',border:'#fff',ppu:100});scene.add(sub);
  const c=cam(42);const tc=K.cta-sh.t0;
  return {scene,cam:c,update(t,d){bg.rotation.z=t*.08;const sq=prog(t,0,1.4);sign.position.y=lerp(26,13.5,E.bounce(sq));sign.rotation.z=Math.sin(t*2.2)*.06*Math.exp(-t*.4)+(1-sq)*.2;
    pose(a,'cross',t);pose(b,'point',t);b.arms[1].rotation.z=1.45+Math.sin(t*5)*.15;a.g.position.y=Math.abs(Math.sin(t*2))*.08;tr.rotation.y=t*.6;
    const q1=E.el(prog(t,tc,tc+.8));bub.scale.setScalar(Math.max(.001,q1));bub.position.set(2.5,7.2,2.5);const q2=E.back(prog(t,tc+.6,tc+1.1));sub.scale.setScalar(Math.max(.001,q2));sub.position.set(-2.1,.9,4.5);
    const k=E.o(prog(t,0,1.6));look(c,V(0,lerp(16,4.6,k),lerp(6,22,k)),V(0,lerp(10,4.6,k),0).add(shake(t,.03)))}}};

/* =============== driver =============== */
const SHOTS=TL.shots.map((s,i)=>Object.assign({},s,{i,trans:['whip','zoom','whip','cut'][i%4]}));
let cur=null,built=null;
const DFS={exterior:1.5,trophy:1.45,faceoff:1.45,ledoff:1.3,cal36:1.7,table1:1.6,chalkIf:1,rivalry:1.9,final21:1.1,final25:1.1,scale:1.4,cal26:1.5,may:1.05,sadfan:1.05,table2:1.5,referee:1.6,var:1.5,exterior2:1.4,chalkFla:1,chalkPal:1,covered:1.4,table3:1.5,coverEyes:1.2,flaHappy:1.4,palSmug:1.15,clock:1.6};
function build(sh){if(built){disposeAll(built.scene)}seedRnd(1000+sh.i*77);DF=DFS[sh.id]||1;built=B[sh.id](sh);cur=sh}
window.renderAt=(t)=>{let sh=SHOTS.find(s=>t>=s.t0&&t<s.t1)||SHOTS[SHOTS.length-1];if(cur!==sh)build(sh);
  const lt=t-sh.t0,d=sh.t1-sh.t0;FLASH=0;built.update(lt,d);const c=built.cam;
  // transitions (whip / zoom punch) at boundaries
  BLUR=0;const TD=.16;const nxt=SHOTS[sh.i+1];
  const inn=sh.i>0?SHOTS[sh.i-1].trans:'cut',out=nxt?sh.trans:'cut';
  if(lt<TD&&inn==='whip'){const q=1-lt/TD;c.rotateY(-.55*q*q);BLUR=26*q}
  if(d-lt<TD&&out==='whip'){const q=1-(d-lt)/TD;c.rotateY(.55*q*q);BLUR=26*q}
  if(lt<TD&&inn==='zoom'){const q=1-lt/TD;c.fov*=1-.35*q*q;c.updateProjectionMatrix();BLUR=Math.max(BLUR,8*q)}
  if(d-lt<TD&&out==='zoom'){const q=1-(d-lt)/TD;c.fov*=1+.3*q*q;c.updateProjectionMatrix();BLUR=Math.max(BLUR,8*q)}
  renderer.render(built.scene,c);
  if(BLUR>.5){hbb.setAttribute('stdDeviation',`${BLUR.toFixed(1)} ${(BLUR*.08).toFixed(1)}`);canvas.style.filter='url(#hb)'}else canvas.style.filter='none';
  flash.style.opacity=String(Math.min(.85,FLASH));return sh.id};
window.READY=true;document.title='ok';
