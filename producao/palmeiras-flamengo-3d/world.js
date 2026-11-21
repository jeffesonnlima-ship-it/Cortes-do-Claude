import {THREE,V,R,ctex,redraw,fitText,rr,toon,OL,mesh,sky,glow,crowdTex,plaque,makeChar,pose,setExpr,clamp,prog,lerp,E,mulberry,pick} from './lib.js';

export const PAL_CROWD=['#0c7a3c','#ffffff','#0a5f2f','#0c7a3c','#e9f5ec'];
export const FLA_CROWD=['#d1121b','#141414','#d1121b','#141414','#ffffff'];
export const MIX_CROWD=['#0c7a3c','#ffffff','#d1121b','#141414'];

/* ---------- lights ---------- */
export function lights(scene,o={}){const hemi=new THREE.HemisphereLight(o.sky||'#bcd3ff',o.ground||'#2c3a22',o.hemi??1.1);scene.add(hemi);
  const d=new THREE.DirectionalLight(o.sun||'#fff2dc',o.sunI??2.2);d.position.copy(o.sunPos||V(30,60,25));d.castShadow=true;d.shadow.mapSize.set(1024,1024);
  const s=o.shadowSize||30;Object.assign(d.shadow.camera,{left:-s,right:s,top:s,bottom:-s,near:1,far:200});d.shadow.bias=-.0005;d.shadow.normalBias=.02;
  if(o.target){d.target.position.copy(o.target);scene.add(d.target);d.position.add(o.target)}scene.add(d);return {hemi,d}}

/* ---------- stadium ---------- */
function ring(a0,b0,a1,b1,h0,h1,seg,mat,rep=40,vrep=1){const pos=[],uv=[],idx=[];
  for(let i=0;i<=seg;i++){const th=i/seg*Math.PI*2,c=Math.cos(th),s=Math.sin(th);pos.push(a0*c,h0,b0*s,a1*c,h1,b1*s);uv.push(i/seg*rep,0,i/seg*rep,vrep)}
  for(let i=0;i<seg;i++){const k=i*2;idx.push(k,k+2,k+1,k+1,k+2,k+3)}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();
  return new THREE.Mesh(g,mat)}
let pitchTex;
function getPitchTex(){if(pitchTex)return pitchTex;return pitchTex=ctex(2048,1328,(g,w,h)=>{const sx=w/105,sy=h/68;
  for(let i=0;i<14;i++){g.fillStyle=i%2?'#2f9a3c':'#37ad45';g.fillRect(i*w/14,0,w/14+1,h)}
  g.globalAlpha=.08;const pr=mulberry(5);for(let i=0;i<4000;i++){g.fillStyle=pr()<.5?'#000':'#fff';g.fillRect(pr()*w,pr()*h,3,3)}g.globalAlpha=1;
  g.strokeStyle='#f4f7f2';g.lineWidth=7;const L=(x,y,ww,hh)=>g.strokeRect(x*sx,y*sy,ww*sx,hh*sy);
  L(1,1,103,66);g.beginPath();g.moveTo(w/2,sy);g.lineTo(w/2,h-sy);g.stroke();g.beginPath();g.arc(w/2,h/2,9.15*sx,0,7);g.stroke();
  L(1,34-20.16,16.5,40.32);L(103-16.5,34-20.16,16.5,40.32);L(1,34-9.16,5.5,18.32);L(103-5.5,34-9.16,5.5,18.32);
  g.fillStyle='#f4f7f2';g.beginPath();g.arc(w/2,h/2,8,0,7);g.fill()})}
const ADS=['CAFÉ DA SERRA','MOTOS VELOZ','RÁDIO GOL AM','PNEUS RODABEM','TINTAS ARCO-ÍRIS','SABÃO BOLHA','GUARANÁ LEGAL','PIPOCA DO ZÉ'];
let adTex;function getAdTex(){if(adTex)return adTex;return adTex=ctex(2048,64,(g,w,h)=>{const n=8;for(let i=0;i<n;i++){g.fillStyle=['#1b2a6b','#c0392b','#f1c40f','#0c7a3c','#ffffff','#8e44ad','#e67e22','#16a085'][i];g.fillRect(i*w/n,0,w/n,h);
  fitText(g,ADS[i],i*w/n+w/n/2,h/2+2,w/n*.86,40,i==2||i==4?'#111':'#fff')}},[6,1])}

export function makeGoal(x,dir=1){const g=new THREE.Group();g.position.set(x,0,0);const W=10.4,H=3.5,D=2.6;const white=toon('#ffffff');
  const post=(p,len,rot)=>{const m=OL(mesh(new THREE.CylinderGeometry(.13,.13,len,12),white,p,{cast:1}),.02);if(rot)m.rotation.x=Math.PI/2;g.add(m)};
  post(V(0,H/2,-W/2),H);post(V(0,H/2,W/2),H);post(V(0,H,0),W,1);
  const netM=new THREE.MeshBasicMaterial({color:'#ffffff',wireframe:true,transparent:true,opacity:.55});
  const back=new THREE.Mesh(new THREE.PlaneGeometry(W,H,26,10),netM);back.rotation.y=Math.PI/2;back.position.set(dir*D,H/2,0);g.add(back);
  const top=new THREE.Mesh(new THREE.PlaneGeometry(D,W,6,26),netM);top.rotation.x=Math.PI/2;top.position.set(dir*D/2,H,0);g.add(top);
  for(const s of[-1,1]){const sd=new THREE.Mesh(new THREE.PlaneGeometry(D,H,6,10),netM);sd.position.set(dir*D/2,H/2,s*W/2);g.add(sd)}
  const base=back.geometry.attributes.position.array.slice();
  g.userData={W,H,D,bulge:(z,y,amt)=>{const p=back.geometry.attributes.position;for(let i=0;i<p.count;i++){const lx=base[i*3],ly=base[i*3+1];
    // plane local x maps to world -z (rotated), y to height offset
    const dz=(-lx)-z,dy=(ly+H/2)-y;const f=Math.exp(-(dz*dz+dy*dy)/3)*amt;p.setZ(i,base[i*3+2]+f*dir*-1*-1)}p.needsUpdate=true}};
  return g}

export function stadium(o={}){const g=new THREE.Group();const colors=o.crowd||PAL_CROWD;
  const t0=crowdTex(colors,0),t1=crowdTex(colors,1);
  const standM=new THREE.MeshBasicMaterial({map:t0,side:THREE.DoubleSide,color:o.night?'#dfe3ee':'#f2f2f2'});
  let standM2=null;
  if(o.split){standM2=new THREE.MeshBasicMaterial({map:crowdTex(o.split,0),side:THREE.DoubleSide,color:o.night?'#dfe3ee':'#f2f2f2'})}
  // ground
  const ground=mesh(new THREE.PlaneGeometry(240,190),toon('#24702e'),V(0,-.02,0),{recv:1});ground.rotation.x=-Math.PI/2;g.add(ground);
  const pitch=mesh(new THREE.PlaneGeometry(105,68),new THREE.MeshToonMaterial({map:getPitchTex(),gradientMap:null}),V(0,0,0),{recv:1});pitch.rotation.x=-Math.PI/2;pitch.receiveShadow=true;g.add(pitch);
  // ad boards
  const adM=new THREE.MeshBasicMaterial({map:getAdTex(),toneMapped:false});
  for(const[px,pz,w,ry]of[[0,37,110,0],[0,-37,110,Math.PI],[56,0,74,-Math.PI/2],[-56,0,74,Math.PI/2]]){const b=mesh(new THREE.BoxGeometry(w,1.1,.3),[toon('#111'),toon('#111'),toon('#111'),toon('#111'),adM,toon('#111')],V(px,.55,pz));b.rotation.y=ry;g.add(b)}
  // stands (split into halves for split crowds)
  const seg=120;
  const mk=(m)=>ring(74,54,112,92,2,30,seg,m,24,4);
  if(o.split){// left half (x<0) colors, right half split colors via two meshes with clipping by building half rings
    const half=(m,from)=>{const pos=[],uv=[],idx=[];const n=60;for(let i=0;i<=n;i++){const th=from+i/n*Math.PI,c=Math.cos(th),s=Math.sin(th);pos.push(74*c,2,54*s,112*c,30,92*s);uv.push(i/n*11,0,i/n*11,4)}
      for(let i=0;i<n;i++){const k=i*2;idx.push(k,k+2,k+1,k+1,k+2,k+3)}const ge=new THREE.BufferGeometry();ge.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));ge.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));ge.setIndex(idx);ge.computeVertexNormals();return new THREE.Mesh(ge,m)};
    g.add(half(standM,Math.PI/2));g.add(half(standM2,-Math.PI/2));
  }else g.add(mk(standM));
  const wall=ring(74,54,74,54,0,2.2,seg,toon('#3b4150'),1);g.add(wall);
  const outer=ring(112,92,113,93,30,0,seg,toon('#c9ced8'),1);g.add(outer);
  // roof
  const roofM=new THREE.MeshStandardMaterial({color:'#e8ecf2',roughness:.7,metalness:.1,side:THREE.DoubleSide});
  const roof=ring(113,93,92,72,32,36,seg,roofM,1);g.add(roof);
  const lightsStrip=ring(92.5,72.5,92,72,35.6,36,seg,new THREE.MeshBasicMaterial({color:'#fffbe6',toneMapped:false}),1);if(o.night)g.add(lightsStrip);
  // floodlight glows on roof
  const glows=[];if(o.night){for(let i=0;i<10;i++){const th=i/10*Math.PI*2+.3;const s=glow('#fff6d8',18,.85);s.position.set(Math.cos(th)*93,37,Math.sin(th)*73);g.add(s);glows.push(s)}}
  // city
  if(o.city!==false){const N=70;const bm=new THREE.MeshLambertMaterial({color:o.night?'#1c2550':'#7d8aa8',emissive:o.night?'#1a1a30':'#000'});
    const winTex=ctex(64,128,(gg,w,h)=>{gg.fillStyle=o.night?'#141a38':'#8592ad';gg.fillRect(0,0,w,h);for(let y=6;y<h;y+=14)for(let x=6;x<w;x+=14){gg.fillStyle=R(0,1)<.55?(o.night?'#ffd77a':'#c9d6ea'):(o.night?'#202850':'#6d7a95');gg.fillRect(x,y,7,8)}},[1,3]);
    const wm=new THREE.MeshBasicMaterial({map:winTex,toneMapped:false,color:o.night?'#ffffff':'#e8ecf5'});
    const im=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),wm,N);const m4=new THREE.Matrix4();
    for(let i=0;i<N;i++){const a=i/N*Math.PI*2+R(-.03,.03),rad=R(180,280),hh=R(20,90);m4.compose(V(Math.cos(a)*rad,hh/2,Math.sin(a)*rad),new THREE.Quaternion().setFromEuler(new THREE.Euler(0,-a,0)),V(R(12,26),hh,R(12,26)));im.setMatrixAt(i,m4)}g.add(im)}
  const bounce=(t)=>{const m=standM;m.map=(Math.floor(t*o.bounceHz||0)%2)?t1:t0;if(standM2){standM2.map=(Math.floor(t*(o.bounceHz||0))%2)?crowdTex(o.split,1):crowdTex(o.split,0)}};
  g.userData={bounce,glows};return g}

export function stadiumScene(o={}){const scene=new THREE.Scene();
  const skies={dusk:['#2a2d6e','#d2668a','#ffb26a'],night:['#050a24','#13265e','#2a4a8c'],day:['#2f7fd6','#8cc4ff','#e3f2ff'],sunset:['#1f2a6b','#e07a5f','#ffd08a']};
  const sk=skies[o.sky||'night'];scene.add(sky(sk[0],sk[1],sk[2],o.sky==='night'));scene.fog=new THREE.Fog(sk[1],180,600);
  const st=stadium(Object.assign({night:o.sky==='night'},o));scene.add(st);
  const L=lights(scene,{sky:o.sky==='night'?'#9fb6ff':'#ffe9d0',hemi:o.sky==='night'?.9:1.2,sun:o.sky==='night'?'#f4f6ff':'#ffd9a8',sunI:o.sky==='night'?2.4:2.6,sunPos:o.sunPos||V(25,55,30),shadowSize:o.shadowSize||40,target:o.shadowTarget});
  return {scene,st,L}}

/* ---------- teams on pitch ---------- */
export function lineup(scene,teamA,teamB,o={}){const chars=[];for(let i=0;i<11;i++){for(const[tm,s]of[[teamA,-1],[teamB,1]]){const c=makeChar({team:tm,skin:pick(['#f2c49b','#d9a173','#b07a50','#8a5a3b']),curly:R(0,1)<.35,scale:o.scale||.8});
  c.g.position.set((i-5)*1.6,0,s*2.2);c.g.rotation.y=s<0?0:Math.PI;scene.add(c.g);chars.push(c)}}return chars}
const _r=mulberry(9);function rnd2(){return _r()}
export function formation(scene,o={}){const chars=[];const posA=[[-48,0],[-35,-18],[-36,-6],[-36,6],[-35,18],[-20,-12],[-22,0],[-20,12],[-8,-20],[-6,0],[-8,20]];
  for(const[tm,s]of[[o.a||'PAL',1],[o.b||'FLA',-1]]){posA.forEach((p,i)=>{const c=makeChar({team:i==0?(tm==='PAL'?'GK1':'GK2'):tm,skin:pick(['#f2c49b','#d9a173','#b07a50','#8a5a3b']),curly:R(0,1)<.35,scale:o.scale||.8});
    c.g.position.set(p[0]*s*(o.spread||1),0,p[1]);c.g.rotation.y=s>0?Math.PI/2:-Math.PI/2;c.home=c.g.position.clone();c.ph=R(0,6);scene.add(c.g);chars.push(c)})}
  return chars}

/* ---------- bar ---------- */
let floorTex;
export function bar(o={}){const scene=new THREE.Scene();scene.background=new THREE.Color('#2a1a10');
  const g=new THREE.Group();scene.add(g);
  floorTex=floorTex||ctex(256,256,(c,w,h)=>{for(let y=0;y<8;y++)for(let x=0;x<8;x++){c.fillStyle=(x+y)%2?'#b8402f':'#efe3cc';c.fillRect(x*32,y*32,32,32)}},[10,10]);
  const floor=mesh(new THREE.PlaneGeometry(40,40),toon('#ffffff',floorTex),V(0,0,0),{recv:1});floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;g.add(floor);
  const wallTex=ctex(512,512,(c,w,h)=>{const gr=c.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#e9a85a');gr.addColorStop(1,'#c9783c');c.fillStyle=gr;c.fillRect(0,0,w,h);c.fillStyle='rgba(255,255,255,.06)';for(let i=0;i<w;i+=32)c.fillRect(i,0,4,h);
    c.fillStyle='#2e6b8f';c.fillRect(0,h*.72,w,h*.28);c.fillStyle='#fff';for(let x=0;x<w;x+=32)for(let y=h*.72;y<h;y+=32){c.fillStyle=((x+y)/32)%2?'#3f86b0':'#2e6b8f';c.fillRect(x,y,31,31)}},[3,1]);
  const back=mesh(new THREE.PlaneGeometry(40,14),toon('#ffffff',wallTex),V(0,7,-6),{recv:1});back.receiveShadow=true;g.add(back);
  const side=mesh(new THREE.PlaneGeometry(30,14),toon('#ffffff',wallTex),V(-12,7,6),{recv:1});side.rotation.y=Math.PI/2;g.add(side);
  const side2=side.clone();side2.position.x=12;side2.rotation.y=-Math.PI/2;g.add(side2);
  // bunting
  const cols=['#e74c3c','#f1c40f','#3498db','#2ecc71','#9b59b6','#e67e22'];
  for(let row=0;row<2;row++)for(let i=0;i<22;i++){const x=-11+i*1.05;const y=9.2-row*.2-Math.sin(i/21*Math.PI)*.9;const z=-5.5+row*5;
    const tri=new THREE.Mesh(new THREE.ConeGeometry(.42,.8,3),toon(cols[(i+row)%6]));tri.rotation.x=Math.PI;tri.rotation.y=Math.PI/6;tri.position.set(x,y-.4,z);tri.scale.z=.15;g.add(tri)}
  // TV
  const tvTex=ctex(512,300,(c,w,h)=>{});const tv=new THREE.Group();tv.position.copy(o.tvPos||V(-4.2,6.2,-5.6));
  const tvb=OL(mesh(new THREE.BoxGeometry(4.4,2.7,.35),toon('#111')),.04);tv.add(tvb);const scr=mesh(new THREE.PlaneGeometry(4,2.35),new THREE.MeshBasicMaterial({map:tvTex,toneMapped:false}),V(0,0,.18));tv.add(scr);g.add(tv);
  const tvGlow=glow('#a9d4ff',7,.35);tvGlow.position.copy(tv.position).add(V(0,0,.6));g.add(tvGlow);
  // clock
  const clk=new THREE.Group();clk.position.set(4.5,7.4,-5.8);const face=OL(mesh(new THREE.CylinderGeometry(.9,.9,.15,32),toon('#ffffff')),.05);face.rotation.x=Math.PI/2;clk.add(face);
  const rim=mesh(new THREE.TorusGeometry(.9,.1,8,32),toon('#c0392b'));clk.add(rim);const hh=mesh(new THREE.BoxGeometry(.08,.5,.05),toon('#111'),V(0,.22,.12));clk.add(hh);const mh=mesh(new THREE.BoxGeometry(.06,.7,.05),toon('#111'),V(.25,-.1,.13));mh.rotation.z=2.2;clk.add(mh);g.add(clk);
  // fridge
  const fr=OL(mesh(new THREE.BoxGeometry(2.4,5,1.6),toon('#eeeeee'),V(9,2.5,-4.9),{cast:1}),.04);g.add(fr);
  const frd=mesh(new THREE.PlaneGeometry(2,4.2),new THREE.MeshBasicMaterial({map:ctex(128,256,(c,w,h)=>{c.fillStyle='#bfe6ff';c.fillRect(0,0,w,h);for(let y=10;y<h;y+=48){c.fillStyle='#8aa';c.fillRect(0,y+36,w,4);for(let x=8;x<w;x+=22){c.fillStyle=pick(['#e74c3c','#2ecc71','#f39c12','#9b59b6','#c0392b']);rr(c,x,y,14,34,4);c.fill()}}}),toneMapped:false}),V(9,2.7,-4.08));g.add(frd);
  // counter
  const counter=OL(mesh(new THREE.BoxGeometry(14,2.2,2),toon('#6b3c1e'),V(0,1.1,-3.2),{cast:1,recv:1}),.04);g.add(counter);
  const ctop=mesh(new THREE.BoxGeometry(14.4,.25,2.4),toon('#3f2210'),V(0,2.3,-3.2));g.add(ctop);
  // bottles
  for(let i=0;i<9;i++){const b=OL(mesh(new THREE.CylinderGeometry(.15,.2,.9,10),toon(pick(['#2e7d32','#8d5524','#c0392b','#1565c0'])),V(-1.5+i*.5+(i>4?2:0),6.5-((i%2)*0),-5.8)),.02);g.add(b)}
  const shelf=mesh(new THREE.BoxGeometry(6,.15,.6),toon('#4a2a14'),V(1,6,-5.7));g.add(shelf);
  // lamp
  const lamp=new THREE.Group();lamp.position.set(o.lampX??0,10.5,o.lampZ??1.5);const cone=OL(mesh(new THREE.ConeGeometry(1.1,.9,24,1,true),toon('#2d7a4f',null,{side:THREE.DoubleSide})),.03);lamp.add(cone);
  const bulb=glow('#ffd58a',4.5,.9);bulb.position.y=-.4;lamp.add(bulb);g.add(lamp);
  const pl=new THREE.PointLight('#ffcf8a',60,22,1.6);pl.position.set(o.lampX??0,9.5,o.lampZ??1.5);pl.castShadow=true;pl.shadow.mapSize.set(512,512);scene.add(pl);
  scene.add(new THREE.HemisphereLight('#ffe2b8','#6b3a22',1.3));const d=new THREE.DirectionalLight('#ffe9cc',1.2);d.position.set(5,12,10);scene.add(d);
  // stools
  for(const x of[-4,0,4]){const st=new THREE.Group();st.position.set(x,0,-1.7);st.add(mesh(new THREE.CylinderGeometry(.1,.1,2.2,8),toon('#999'),V(0,1.1,0)));st.add(OL(mesh(new THREE.CylinderGeometry(.6,.6,.25,20),toon('#c0392b'),V(0,2.25,0)),.03));g.add(st)}
  return {scene,g,tvTex,tv,clk}}
export function drawTV(tex,draw){redraw(tex,draw)}
export function tvPitch(c,w,h,score,txt){const gr=c.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#1d3b78');gr.addColorStop(.35,'#2b5bb0');gr.addColorStop(.36,'#2f9a3c');gr.addColorStop(1,'#37ad45');c.fillStyle=gr;c.fillRect(0,0,w,h);
  c.fillStyle='rgba(255,255,255,.7)';for(let i=0;i<60;i++){c.fillRect((i*37)%w,h*.18+((i*13)%30),6,6)}
  if(score){c.fillStyle='rgba(10,10,20,.85)';rr(c,w*.12,h*.06,w*.76,h*.26,14);c.fill();fitText(c,score,w/2,h*.19,w*.7,h*.2,'#fff')}
  if(txt){c.fillStyle='#c0392b';c.fillRect(0,h*.82,w,h*.18);fitText(c,txt,w/2,h*.91,w*.9,h*.12,'#fff')}}

/* ---------- classroom + chalkboard ---------- */
export function classroom(){const scene=new THREE.Scene();scene.background=new THREE.Color('#d8c7a4');
  const wall=mesh(new THREE.PlaneGeometry(60,30),toon('#e3d3b0'),V(0,10,-1),{recv:1});scene.add(wall);
  const floor=mesh(new THREE.PlaneGeometry(60,40),toon('#8a5a33'),V(0,0,10),{recv:1});floor.rotation.x=-Math.PI/2;scene.add(floor);
  const frame=OL(mesh(new THREE.BoxGeometry(10.8,12.8,.5),toon('#6b3c1e'),V(0,8.6,-.6),{cast:1}),.05);scene.add(frame);
  const boardTex=ctex(1000,1200,()=>{});
  const board=mesh(new THREE.PlaneGeometry(10,12),new THREE.MeshLambertMaterial({map:boardTex}),V(0,8.6,-.32));scene.add(board);
  const tray=mesh(new THREE.BoxGeometry(11,.25,.7),toon('#4a2a14'),V(0,2.25,-.2));scene.add(tray);
  const chalk=mesh(new THREE.BoxGeometry(.9,.15,.15),toon('#f5f5f0'),V(-3,2.45,-.1));scene.add(chalk);const er=OL(mesh(new THREE.BoxGeometry(1.2,.35,.5),toon('#2c3e50'),V(3,2.55,-.1)),.03);scene.add(er);
  // desks
  for(const x of[-6,6]){const dk=OL(mesh(new THREE.BoxGeometry(4,2,2),toon('#9c6b3e'),V(x,1,8),{cast:1}),.04);scene.add(dk)}
  scene.add(new THREE.HemisphereLight('#fff4e0','#8a6a44',1.4));const d=new THREE.DirectionalLight('#fff',1.6);d.position.set(-8,16,14);d.castShadow=true;d.shadow.mapSize.set(1024,1024);Object.assign(d.shadow.camera,{left:-15,right:15,top:15,bottom:-15});scene.add(d);
  return {scene,boardTex,board}}
export function chalkDraw(tex,title,lines,t,o={}){redraw(tex,(c,w,h)=>{c.fillStyle='#244a3b';c.fillRect(0,0,w,h);
  c.globalAlpha=.08;for(let i=0;i<30;i++){c.fillStyle='#fff';c.beginPath();c.ellipse(Math.sin(i*7.1)*w*.5+w/2,(i*53)%h,160,26,i,0,7);c.fill()}c.globalAlpha=1;
  const reveal=(txt,x,y,size,col,p,align='left',rot=-.015)=>{if(p<=0)return;c.save();c.translate(x,y);c.rotate(rot);c.font=`900 ${size}px N`;c.textAlign=align;c.textBaseline='middle';
    const wd=c.measureText(txt).width;const x0=align==='center'?-wd/2:0;c.beginPath();c.rect(x0-10,-size,(wd+20)*clamp(p),size*2);c.clip();
    c.fillStyle=col;c.shadowColor=col;c.shadowBlur=6;c.globalAlpha=.94;c.fillText(txt,0,0);c.restore();
    if(p<1){c.save();c.translate(x,y);c.rotate(rot);c.fillStyle='#fff';c.fillRect(x0+wd*p-6,-size*.3,18,size*.6);c.restore()}};
  if(title){reveal(title.t,w/2,130,110,'#f4f1e6',title.p,'center',-.02);if(title.p>=1){c.strokeStyle='rgba(244,241,230,.9)';c.lineWidth=8;c.beginPath();c.moveTo(w*.2,200);c.quadraticCurveTo(w/2,186,w*.8,204);c.stroke()}}
  lines.forEach(l=>{reveal(l.t,l.x??120,l.y,l.s||96,l.c||'#f4f1e6',l.p,l.align||'left',l.r??-.015);
    if(l.circle&&l.p>=1){const cp=clamp(l.circle);c.save();c.strokeStyle='#ff8f8f';c.lineWidth=10;c.beginPath();c.ellipse(l.cx||w/2,l.y,l.cw||560,90,-.03,-.5,-.5+cp*Math.PI*2.1);c.stroke();c.restore()}
    if(l.check&&l.p>=1){c.save();c.strokeStyle='#9be7a8';c.lineWidth=16;c.lineCap='round';const cp=clamp(l.check);c.beginPath();const x=l.cx||1380,y=l.y;c.moveTo(x-40,y);c.lineTo(x-40+40*Math.min(1,cp*2),y+40*Math.min(1,cp*2));if(cp>.5)c.lineTo(x+(cp-.5)*2*80,y+40-(cp-.5)*2*110);c.stroke();c.restore()}})})}

/* ---------- table board ---------- */
export function tableBoard(){const g=new THREE.Group();const wood=toon('#6b3c1e');
  const frame=OL(mesh(new THREE.BoxGeometry(11,13,.8),wood,V(0,0,-.4),{cast:1,recv:1}),.06);g.add(frame);
  const inner=mesh(new THREE.BoxGeometry(10,12,.2),toon('#3f2210'),V(0,0,.05));g.add(inner);
  return g}
const digitCache={};function digitTex(d){if(digitCache[d])return digitCache[d];return digitCache[d]=ctex(128,180,(c,w,h)=>{c.fillStyle='#141414';rr(c,4,4,w-8,h-8,14);c.fill();c.strokeStyle='#e8c14a';c.lineWidth=6;c.stroke();
  fitText(c,String(d),w/2,h/2+6,w*.9,150,'#ffd23f');c.fillStyle='#000';c.fillRect(0,h/2-3,w,6)})}
export function digit(d){const g=new THREE.Group();const m=new THREE.Mesh(new THREE.BoxGeometry(1,1.4,.25),[toon('#111'),toon('#111'),toon('#111'),toon('#111'),new THREE.MeshBasicMaterial({map:digitTex(d),toneMapped:false}),toon('#111')]);m.position.y=-.7;g.add(m);OL(m,.02);g.userData.m=m;return g}
export function setDigit(dg,d){dg.userData.m.material[4].map=digitTex(d)}
export function teamPlate(name,color,w=6){return plaque([name],w,1.4,{bg:color,fg:'#fff',border:'#16161c',ppu:110})}

/* ---------- calendar ---------- */
export function calendarPage(txt,sub){const tex=ctex(600,560,(c,w,h)=>{c.fillStyle='#f7f0e1';c.fillRect(0,0,w,h);c.fillStyle='#c0392b';c.fillRect(0,0,w,120);fitText(c,sub||'',w/2,60,w*.85,58,'#fff');
  fitText(c,txt,w/2,h*.6,w*.86,txt.length>3?190:270,'#1b1b22');c.fillStyle='#1b1b22';c.fillRect(w*.2,h*.86,w*.6,6)});
  const m=new THREE.Mesh(new THREE.PlaneGeometry(6,5.6),new THREE.MeshLambertMaterial({map:tex,side:THREE.DoubleSide}));m.position.y=-2.8;const pv=new THREE.Group();pv.add(m);return pv}
export function calendarBase(){const g=new THREE.Group();const st=OL(mesh(new THREE.BoxGeometry(6.6,6.4,.5),toon('#5a3a20'),V(0,-3.1,-.4),{cast:1}),.05);st.rotation.x=-.12;g.add(st);
  for(let i=0;i<6;i++){const r=OL(mesh(new THREE.TorusGeometry(.25,.06,8,16),toon('#9a9a9a'),V(-2.4+i*.96,.1,0)),.02);r.rotation.y=Math.PI/2;g.add(r)}return g}

/* ---------- trophy ---------- */
export function trophy(env){const g=new THREE.Group();const gold=new THREE.MeshStandardMaterial({color:'#ffcc44',metalness:1,roughness:.22,envMap:env,envMapIntensity:1.4});
  const pts=[];const prof=[[0,0],[.9,0],[.9,.25],[.5,.35],[.35,.9],[.3,1.4],[.55,1.6],[1.3,2.2],[1.55,3.1],[1.6,3.4],[1.45,3.45]];for(const[x,y]of prof)pts.push(new THREE.Vector2(x,y));
  const cup=mesh(new THREE.LatheGeometry(pts,48),gold,V(0,1.1,0),{cast:1});g.add(cup);OL(cup,.025);
  for(const s of[-1,1]){const h=mesh(new THREE.TorusGeometry(.6,.12,12,24,Math.PI*1.2),gold,V(s*1.55,3.6,0),{cast:1});h.rotation.z=s>0?-Math.PI*.6:Math.PI*1.4;g.add(h)}
  const base=OL(mesh(new THREE.BoxGeometry(2.6,.8,2.6),new THREE.MeshStandardMaterial({color:'#2a2a33',roughness:.4,metalness:.3}),V(0,.4,0),{cast:1}),.03);g.add(base);
  const base2=OL(mesh(new THREE.BoxGeometry(2,.5,2),new THREE.MeshStandardMaterial({color:'#1b1b22',roughness:.4}),V(0,1.05,0),{cast:1}),.03);g.add(base2);
  const pl=mesh(new THREE.PlaneGeometry(1.9,.5),new THREE.MeshStandardMaterial({map:ctex(380,100,(c,w,h)=>{c.fillStyle='#d4a33a';c.fillRect(0,0,w,h);fitText(c,'BRASILEIRÃO 2026',w/2,h/2+3,w*.9,48,'#2a1a05')}),metalness:.6,roughness:.3}),V(0,.4,1.31));g.add(pl);
  return g}

/* ---------- LED scoreboard ---------- */
export function ledBoard(w=24,h=10){const g=new THREE.Group();const tex=ctex(1200,500,()=>{});
  const fr=OL(mesh(new THREE.BoxGeometry(w+1,h+1,1),toon('#1a1a1f'),V(0,0,-.55),{cast:1}),.06);g.add(fr);
  const sc=mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:tex,toneMapped:false}),V(0,0,0));g.add(sc);
  for(const s of[-1,1])g.add(mesh(new THREE.CylinderGeometry(.5,.5,30,10),toon('#333'),V(s*w*.35,-h/2-15,-.6)));
  const gl=glow('#ffb23a',w*1.4,.18);gl.position.z=1;g.add(gl);g.userData={tex,glow:gl};return g}
export function ledDraw(tex,lines,o={}){redraw(tex,(c,w,h)=>{c.fillStyle='#050505';c.fillRect(0,0,w,h);
  if(o.noise){for(let i=0;i<5000;i++){c.fillStyle=Math.random()<.5?'#ffb23a':'#3a2a10';c.fillRect(Math.random()*w,Math.random()*h,8,8)}}
  else lines.forEach((l,i)=>{const L=typeof l==='string'?{t:l}:l;c.font=`800 ${L.s||110}px "JetBrains Mono"`;c.textAlign='center';c.textBaseline='middle';c.shadowColor=L.c||'#ffb23a';c.shadowBlur=24;c.fillStyle=L.c||'#ffc83a';
    let s=L.s||110;while(c.measureText(L.t).width>w*.92&&s>20){s-=4;c.font=`800 ${s}px "JetBrains Mono"`}c.fillText(L.t,w/2,h*(i+.5)/lines.length)});
  c.shadowBlur=0;c.fillStyle='rgba(0,0,0,.55)';for(let y=0;y<h;y+=10)c.fillRect(0,y,w,3);for(let x=0;x<w;x+=10)c.fillRect(x,0,3,h)})}

/* ---------- clock ---------- */
export function bigClock(){const g=new THREE.Group();const faceTex=ctex(800,800,(c,w,h)=>{c.fillStyle='#fffdf6';c.beginPath();c.arc(w/2,h/2,w/2,0,7);c.fill();
  for(let i=0;i<60;i++){const a=i/60*Math.PI*2;const r1=w*.46,r0=i%5?w*.43:w*.38;c.strokeStyle='#1b1b22';c.lineWidth=i%5?6:16;c.beginPath();c.moveTo(w/2+Math.sin(a)*r0,h/2-Math.cos(a)*r0);c.lineTo(w/2+Math.sin(a)*r1,h/2-Math.cos(a)*r1);c.stroke()}
  for(let i=1;i<=12;i++){const a=i/12*Math.PI*2;fitText(c,String(i),w/2+Math.sin(a)*w*.3,h/2-Math.cos(a)*w*.3+4,120,74,'#1b1b22')}});
  const body=mesh(new THREE.CylinderGeometry(5,5,.6,64),toon('#c0392b'),null,{cast:1});body.rotation.x=Math.PI/2;g.add(body);const face=mesh(new THREE.CircleGeometry(4.95,64),new THREE.MeshLambertMaterial({map:faceTex}),V(0,0,.31));g.add(face);
  const rim=OL(mesh(new THREE.TorusGeometry(5.1,.45,16,64),toon('#c0392b')),.04);g.add(rim);
  const hour=new THREE.Group(),min=new THREE.Group(),sec=new THREE.Group();[hour,min,sec].forEach((h,i)=>{h.position.z=.5+i*.12;g.add(h)});
  hour.add(OL(mesh(new THREE.BoxGeometry(.4,2.8,.1),toon('#1b1b22'),V(0,1.2,0)),.02));min.add(OL(mesh(new THREE.BoxGeometry(.28,4,.1),toon('#1b1b22'),V(0,1.8,0)),.02));sec.add(mesh(new THREE.BoxGeometry(.1,4.3,.08),toon('#c0392b'),V(0,1.6,0)));
  g.add(OL(mesh(new THREE.CylinderGeometry(.35,.35,.3,20),toon('#c0392b'),V(0,0,.85)),.02).rotateX(Math.PI/2));
  g.userData={hour,min,sec};return g}

/* ---------- balance ---------- */
export function balance(env){const g=new THREE.Group();const gold=new THREE.MeshStandardMaterial({color:'#e8b84a',metalness:.9,roughness:.3,envMap:env});
  g.add(mesh(new THREE.CylinderGeometry(.3,.4,9,16),gold,V(0,4.5,0),{cast:1}));g.add(mesh(new THREE.CylinderGeometry(2.4,2.8,.6,32),gold,V(0,.3,0),{cast:1}));
  const beam=new THREE.Group();beam.position.y=9;g.add(beam);beam.add(mesh(new THREE.BoxGeometry(12,.35,.35),gold,null,{cast:1}));beam.add(mesh(new THREE.SphereGeometry(.6,20,16),gold));
  const pans=[];for(const s of[-1,1]){const pv=new THREE.Group();pv.position.x=s*5.6;beam.add(pv);
    for(const a of[0,2.1,4.2])pv.add(mesh(new THREE.CylinderGeometry(.03,.03,4.6,4),gold,V(Math.cos(a)*1.1,-2.3,Math.sin(a)*1.1)).rotateZ(Math.cos(a)*.24).rotateX(-Math.sin(a)*.24));
    const pan=mesh(new THREE.SphereGeometry(1.8,32,12,0,Math.PI*2,Math.PI*.62,Math.PI*.38),new THREE.MeshStandardMaterial({color:'#e8b84a',metalness:.9,roughness:.3,envMap:env,side:THREE.DoubleSide}),V(0,-3.2,0),{cast:1});pv.add(pan);pans.push(pv)}
  g.userData={beam,pans};return g}
