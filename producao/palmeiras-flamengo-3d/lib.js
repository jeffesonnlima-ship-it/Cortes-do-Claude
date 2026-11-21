import * as THREE from 'three';
export {THREE};

/* ---------- math / easing ---------- */
export const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
export const prog=(t,a,b)=>clamp((t-a)/(b-a));
export const lerp=(a,b,t)=>a+(b-a)*t;
export const V=(x,y,z)=>new THREE.Vector3(x,y,z);
export const E={
  io:t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,
  o:t=>1-Math.pow(1-t,3), i:t=>t*t*t,
  o5:t=>1-Math.pow(1-t,5),
  back:t=>{const c1=1.9,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)},
  el:t=>t<=0?0:t>=1?1:Math.pow(2,-9*t)*Math.sin((t*10-.75)*(2*Math.PI/3))+1,
  bounce:t=>{const n1=7.5625,d1=2.75;if(t<1/d1)return n1*t*t;if(t<2/d1)return n1*(t-=1.5/d1)*t+.75;if(t<2.5/d1)return n1*(t-=2.25/d1)*t+.9375;return n1*(t-=2.625/d1)*t+.984375}
};
export function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
export let rnd=Math.random;
export function seedRnd(s){rnd=mulberry(s)}
export const R=(a,b)=>a+(b-a)*rnd();
export function pick(a){return a[Math.floor(rnd()*a.length)]}
export function shake(t,amp=1,f=1){return V((Math.sin(t*1.7*f)+Math.sin(t*3.1*f+1.3)*.5)*amp,(Math.sin(t*2.3*f+.7)+Math.sin(t*4.3*f+2.1)*.4)*amp,(Math.sin(t*1.3*f+2.2))*amp*.5)}
/* catmull path */
export function path(pts,t){const c=new THREE.CatmullRomCurve3(pts,false,'centripetal');return c.getPoint(clamp(t))}

/* ---------- textures ---------- */
export function ctex(w,h,draw,rep){const c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d');draw(g,w,h);
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=8;if(rep){t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(rep[0],rep[1])}
  t.userData={c,g};return t}
export function redraw(t,draw){const {c,g}=t.userData;g.clearRect(0,0,c.width,c.height);draw(g,c.width,c.height);t.needsUpdate=true}
export function fitText(g,text,x,y,maxW,size,color,o={}){g.save();let s=size;g.font=`${o.w||900} ${s}px N`;while(g.measureText(text).width>maxW&&s>8){s-=2;g.font=`${o.w||900} ${s}px N`}
  g.textAlign=o.align||'center';g.textBaseline='middle';
  if(o.shadow){g.shadowColor='rgba(0,0,0,.5)';g.shadowBlur=o.shadow;g.shadowOffsetY=o.shadow/3}
  if(o.stroke){g.lineWidth=o.stroke;g.strokeStyle=o.strokeColor||'#111';g.lineJoin='round';g.strokeText(text,x,y)}
  g.fillStyle=color;g.fillText(text,x,y);g.restore();return s}
export function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath()}

/* ---------- materials ---------- */
const gmData=new Uint8Array([110,110,110,255,185,185,185,255,255,255,255,255]);
export const GM=new THREE.DataTexture(gmData,3,1);GM.minFilter=GM.magFilter=THREE.NearestFilter;GM.needsUpdate=true;
export const toon=(color,map,o={})=>new THREE.MeshToonMaterial(Object.assign({color,map:map||null,gradientMap:GM},o));
const OLC={};
export function outlineMat(th=.035){if(OLC[th])return OLC[th];return OLC[th]=new THREE.ShaderMaterial({uniforms:{th:{value:th}},
  vertexShader:`uniform float th;void main(){vec3 p=position+normal*th;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}`,
  fragmentShader:`void main(){gl_FragColor=vec4(.06,.06,.08,1.);}`,side:THREE.BackSide})}
export function OL(mesh,th=.035){const o=new THREE.Mesh(mesh.geometry,outlineMat(th));o.userData.outline=1;mesh.add(o);return mesh}
export function mesh(geo,mat,pos,o={}){const m=new THREE.Mesh(geo,mat);if(pos)m.position.copy(pos);if(o.shadow!==false){m.castShadow=!!o.cast;m.receiveShadow=!!o.recv}return m}

/* ---------- characters ---------- */
export const TEAMS={
  PAL:{base:'#0c7a3c',stripe:null,shorts:'#f4f4f4',socks:'#0c7a3c',trim:'#ffffff'},
  FLA:{base:'#d1121b',stripe:'#141414',shorts:'#f4f4f4',socks:'#141414',trim:'#141414'},
  REF:{base:'#1d1f2a',stripe:null,shorts:'#1d1f2a',socks:'#1d1f2a',trim:'#e5c04a'},
  GK1:{base:'#f39c12',stripe:null,shorts:'#222',socks:'#f39c12',trim:'#222'},
  GK2:{base:'#7d3cff',stripe:null,shorts:'#222',socks:'#7d3cff',trim:'#222'},
  SUIT:{base:'#2c3446',stripe:null,shorts:'#2c3446',socks:'#222',trim:'#c0392b'},
  TEACH:{base:'#8a6d4a',stripe:null,shorts:'#4b3b2a',socks:'#222',trim:'#eee'},
};
const shirtCache={};
function shirtTex(team,num){const k=team+(num||'');if(shirtCache[k])return shirtCache[k];const T=TEAMS[team];
  return shirtCache[k]=ctex(256,256,(g,w,h)=>{g.fillStyle=T.base;g.fillRect(0,0,w,h);
    if(T.stripe){g.fillStyle=T.stripe;for(let y=0;y<h;y+=42)g.fillRect(0,y,w,21)}
    if(team==='PAL'){g.fillStyle='#fff';g.fillRect(0,0,w,10);g.fillStyle='#0a5f2f';g.fillRect(0,h*.62,w,10)}
    if(team==='REF'){g.fillStyle=T.trim;g.fillRect(0,0,w,12)}
    if(team==='SUIT'){g.fillStyle='#f1f1f1';g.beginPath();g.moveTo(w*.12,0);g.lineTo(w*.25,h*.35);g.lineTo(w*.38,0);g.fill();g.fillStyle=T.trim;g.fillRect(w*.22,h*.05,w*.06,h*.3)}
    if(num){fitText(g,String(num),w*.75,h*.42,90,90,team==='FLA'?'#fff':'#fff',{stroke:8,strokeColor:'#111'})}
  })}
const SKINS=['#f2c49b','#d9a173','#b07a50','#8a5a3b','#f6d3b5'];
export function makeChar(o={}){
  const team=o.team||'PAL',T=TEAMS[team];const g=new THREE.Group();const rig={g};
  const skin=o.skin||'#f2c49b';const skinM=toon(skin);const ink=toon('#16161c');
  const bodyM=toon('#ffffff',shirtTex(team,o.num));
  const torso=new THREE.Group();torso.position.y=1.0;g.add(torso);rig.torso=torso;
  const body=OL(mesh(new THREE.CapsuleGeometry(.56,.72,8,20),bodyM,V(0,.36,0),{cast:1}),.04);torso.add(body);rig.body=body;
  if(o.scarf){const sc=OL(mesh(new THREE.TorusGeometry(.5,.14,10,24),toon(o.scarf),V(0,1.02,0),{cast:1}),.03);sc.rotation.x=Math.PI/2;torso.add(sc);
    const tail=OL(mesh(new THREE.BoxGeometry(.22,.6,.1),toon(o.scarf),V(.28,.7,.5)),.03);tail.rotation.z=.15;torso.add(tail)}
  if(o.ref||team==='REF'){const wh=OL(mesh(new THREE.SphereGeometry(.09,12,10),toon('#cfcfcf'),V(0,.65,.55)),.02);torso.add(wh)}
  const headG=new THREE.Group();headG.position.y=1.92;torso.add(headG);rig.headG=headG;
  const head=OL(mesh(new THREE.SphereGeometry(.82,40,28),skinM,null,{cast:1}),.04);headG.add(head);
  // hair
  const hairC=o.gray?'#d4d4dc':(o.hairC||'#2a1b12');
  if(o.hair!=='none'){
    if(o.curly){for(let i=0;i<14;i++){const a=i/14*Math.PI*2;const r=.62;const s=OL(mesh(new THREE.SphereGeometry(.27,14,10),toon(hairC),V(Math.cos(a)*r,.48+Math.sin(i*1.7)*.05,Math.sin(a)*r*.85-.12)),.03);headG.add(s)}
      const top=OL(mesh(new THREE.SphereGeometry(.7,20,14),toon(hairC),V(0,.42,-.08)),.03);top.scale.set(1,.65,1);headG.add(top)}
    else{const hg=new THREE.SphereGeometry(.86,40,20,0,Math.PI*2,0,Math.PI*.42);const h=OL(mesh(hg,toon(hairC),V(0,.02,-.03)),.035);h.rotation.x=-.32;headG.add(h);
      if(!o.gray){const fr=OL(mesh(new THREE.SphereGeometry(.3,14,10),toon(hairC),V(.3,.6,.55)),.03);fr.scale.set(1.4,.6,.8);headG.add(fr)}}
  }
  // face
  const eyes=[],brows=[];
  for(const s of [-1,1]){const e=mesh(new THREE.SphereGeometry(.11,16,12),ink,V(s*.28,.06,.76));e.scale.set(1,1.3,.5);headG.add(e);eyes.push(e);
    const b=mesh(new THREE.BoxGeometry(.3,.07,.06),ink,V(s*.3,.36,.74));headG.add(b);brows.push(b);}
  if(o.glasses){for(const s of [-1,1]){const r=mesh(new THREE.TorusGeometry(.2,.03,8,24),ink,V(s*.28,.06,.8));headG.add(r)}
    headG.add(mesh(new THREE.BoxGeometry(.18,.03,.03),ink,V(0,.08,.84)))}
  const mouth={};
  mouth.smile=mesh(new THREE.TorusGeometry(.2,.045,8,20,Math.PI),ink,V(0,-.26,.76));mouth.smile.rotation.z=Math.PI;
  mouth.frown=mesh(new THREE.TorusGeometry(.18,.045,8,20,Math.PI),ink,V(0,-.42,.75));
  mouth.line=mesh(new THREE.BoxGeometry(.3,.05,.05),ink,V(0,-.3,.78));
  mouth.open=mesh(new THREE.SphereGeometry(.2,16,12),toon('#7a1d22'),V(0,-.32,.7));mouth.open.scale.set(1.2,1,.45);
  mouth.grin=OL(mesh(new THREE.BoxGeometry(.56,.2,.12),toon('#ffffff'),V(0,-.3,.73)),.02);
  mouth.smirk=mesh(new THREE.TorusGeometry(.17,.045,8,20,Math.PI*.8),ink,V(.06,-.24,.77));mouth.smirk.rotation.z=Math.PI*1.1;
  for(const k in mouth){headG.add(mouth[k]);mouth[k].visible=false}
  if(o.sweat){const d=OL(mesh(new THREE.SphereGeometry(.12,12,10),toon('#8fd6ff'),V(.62,.45,.42)),.02);d.scale.set(.8,1.3,.8);headG.add(d)}
  rig.eyes=eyes;rig.brows=brows;rig.mouth=mouth;
  // eye-cover hands
  rig.faceHands=[];for(const s of [-1,1]){const hnd=OL(mesh(new THREE.SphereGeometry(.26,14,12),skinM,V(s*.28,.06,.84)),.03);hnd.scale.set(1.1,.85,.6);hnd.visible=false;headG.add(hnd);rig.faceHands.push(hnd)}
  // arms
  rig.arms=[];for(const s of [-1,1]){const p=new THREE.Group();p.position.set(s*.6,.75,0);torso.add(p);
    const a=OL(mesh(new THREE.CapsuleGeometry(.13,.5,6,10),bodyM,V(0,-.36,0),{cast:1}),.03);p.add(a);
    const hnd=OL(mesh(new THREE.SphereGeometry(.17,12,10),skinM,V(0,-.78,0),{cast:1}),.03);p.add(hnd);p.userData.hand=hnd;rig.arms.push(p)}
  // legs
  rig.legs=[];for(const s of [-1,1]){const p=new THREE.Group();p.position.set(s*.27,.78,0);g.add(p);
    const l=OL(mesh(new THREE.CapsuleGeometry(.14,.46,6,10),toon(T.shorts),V(0,-.3,0),{cast:1}),.03);p.add(l);
    const sk=mesh(new THREE.CylinderGeometry(.15,.15,.22,12),toon(T.socks),V(0,-.52,0));p.add(sk);
    const sh=OL(mesh(new THREE.SphereGeometry(.2,12,10),ink,V(0,-.7,.1),{cast:1}),.02);sh.scale.set(1,.6,1.5);p.add(sh);rig.legs.push(p)}
  if(o.scale)g.scale.setScalar(o.scale);
  g.userData.rig=rig;setExpr(rig,o.ex||'neutral');return rig;
}
export function setExpr(r,ex){const M=r.mouth;for(const k in M)M[k].visible=false;
  const br=(a,y)=>{r.brows[0].rotation.z=a;r.brows[1].rotation.z=-a;r.brows.forEach(b=>b.position.y=y)};
  r.eyes.forEach(e=>{e.scale.set(1,1.3,.5);e.rotation.z=0});
  if(ex==='neutral'){M.line.visible=true;br(0,.36)}
  if(ex==='happy'){M.open.visible=true;M.open.scale.set(1.5,1.1,.45);r.eyes.forEach(e=>e.scale.set(1.2,.45,.5));br(-.1,.42)}
  if(ex==='smile'){M.smile.visible=true;br(-.05,.4)}
  if(ex==='sad'){M.frown.visible=true;br(-.35,.38)}
  if(ex==='angry'){M.grin.visible=true;br(.4,.3)}
  if(ex==='wide'){M.open.visible=true;r.eyes.forEach(e=>e.scale.set(1.5,1.8,.5));br(-.2,.48)}
  if(ex==='smug'){M.smirk.visible=true;r.eyes.forEach(e=>e.scale.set(1.15,.55,.5));br(.15,.34);r.brows[1].position.y=.42;r.brows[1].rotation.z=-.25}
  if(ex==='closed'){M.line.visible=true;r.eyes.forEach(e=>e.scale.set(1.2,.25,.5));br(0,.38)}
  if(ex==='grin'){M.grin.visible=true;r.eyes.forEach(e=>e.scale.set(1.2,.5,.5));br(-.1,.42)}
  r.ex=ex}
export function pose(r,name,ph=0,amt=1){const [aL,aR]=r.arms,[lL,lR]=r.legs;
  const reset=()=>{for(const a of r.arms)a.rotation.set(0,0,0);for(const l of r.legs)l.rotation.set(0,0,0);r.torso.rotation.set(0,0,0);r.headG.rotation.set(0,0,0);r.torso.position.y=1.0;r.faceHands.forEach(h=>h.visible=false)};
  reset();const S=Math.sin(ph);
  if(name==='idle'){aL.rotation.z=-.18-S*.03;aR.rotation.z=.18+S*.03;r.torso.position.y=1+Math.sin(ph*.5)*.02;r.headG.rotation.z=Math.sin(ph*.35)*.04}
  if(name==='run'||name==='walk'){const k=name==='run'?1:.45;lL.rotation.x=S*.95*k;lR.rotation.x=-S*.95*k;aL.rotation.x=-S*.9*k;aR.rotation.x=S*.9*k;aL.rotation.z=-.15;aR.rotation.z=.15;
    r.torso.rotation.x=.18*k;r.torso.position.y=1+Math.abs(Math.cos(ph))*.12*k}
  if(name==='celebrate'){aL.rotation.z=-2.6-S*.25;aR.rotation.z=2.6+S*.25;r.torso.position.y=1+Math.abs(S)*.35;lL.rotation.x=-Math.abs(S)*.3;lR.rotation.x=-Math.abs(S)*.3;r.headG.rotation.x=-.15}
  if(name==='fist'){aR.rotation.z=2.7;aR.rotation.x=-.2;aL.rotation.z=-.5;aL.rotation.x=-.6;r.headG.rotation.x=-.2}
  if(name==='cross'){aL.rotation.x=-1.25;aR.rotation.x=-1.35;aL.rotation.z=.75;aR.rotation.z=-.75;r.headG.rotation.x=-.05}
  if(name==='eyes'){aL.rotation.x=-2.3;aR.rotation.x=-2.3;aL.rotation.z=.35;aR.rotation.z=-.35;r.faceHands.forEach(h=>h.visible=true);r.headG.rotation.x=.18;r.torso.rotation.x=.12}
  if(name==='point'){aR.rotation.z=1.45;aR.rotation.x=-.5;aL.rotation.z=-.2}
  if(name==='whistle'){aR.rotation.x=-2.2;aR.rotation.z=-.5;aL.rotation.z=-.2}
  if(name==='kick'){const k=amt;lR.rotation.x=lerp(.9,-1.5,k);r.torso.rotation.x=-.2*k;aL.rotation.z=-1.1;aR.rotation.z=.6;aL.rotation.x=-.4}
  if(name==='header'){r.torso.rotation.x=lerp(-.25,.5,amt);r.headG.rotation.x=lerp(-.4,.4,amt);aL.rotation.z=-1.4;aR.rotation.z=1.4;lL.rotation.x=.4;lR.rotation.x=-.6}
  if(name==='sad'){aL.rotation.z=-.05;aR.rotation.z=.05;r.headG.rotation.x=.35;r.torso.rotation.x=.12}
  if(name==='jump'){aL.rotation.z=-2.4-S*.3;aR.rotation.z=2.4+S*.3;r.torso.position.y=1+Math.abs(S)*.6;lL.rotation.x=.5;lR.rotation.x=-.3}
  if(name==='dive'){aL.rotation.z=-2.8;aR.rotation.z=2.8;lL.rotation.z=-.3;lR.rotation.z=.3}
  if(name==='fall'){aL.rotation.z=-1.8;aR.rotation.z=1.2;lR.rotation.x=-1.2;lL.rotation.x=-.4}
  if(name==='lift'){aL.rotation.z=-2.9;aR.rotation.z=2.9;r.headG.rotation.x=-.25}
  if(name==='stick'){aR.rotation.z=1.2;aR.rotation.x=-.9;aL.rotation.z=-.15}
}

/* ---------- ball ---------- */
let ballTex;
export function makeBall(r=.32){if(!ballTex)ballTex=ctex(512,256,(g,w,h)=>{g.fillStyle='#fafafa';g.fillRect(0,0,w,h);g.fillStyle='#1a1a1a';
  const pts=[[.1,.5],[.35,.2],[.35,.8],[.6,.5],[.85,.2],[.85,.8],[.6,.02],[.1,.02],[.1,.98],[.6,.98]];for(const[x,y]of pts){g.beginPath();for(let i=0;i<5;i++){const a=i/5*Math.PI*2-Math.PI/2;g.lineTo(x*w+Math.cos(a)*34,y*h+Math.sin(a)*30)}g.fill()}});
  const b=OL(mesh(new THREE.SphereGeometry(r,24,18),toon('#ffffff',ballTex),null,{cast:1}),.025);return b}

/* ---------- sky ---------- */
export function sky(top,mid,bot,stars=false){const g=new THREE.Group();
  const m=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,uniforms:{a:{value:new THREE.Color(top)},b:{value:new THREE.Color(mid)},c:{value:new THREE.Color(bot)}},
  vertexShader:`varying vec3 vp;void main(){vp=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,
  fragmentShader:`uniform vec3 a,b,c;varying vec3 vp;void main(){float h=vp.y;vec3 col=h>0.12?mix(b,a,smoothstep(.12,.75,h)):mix(c,b,smoothstep(-.1,.12,h));gl_FragColor=vec4(col,1.);}`});
  g.add(new THREE.Mesh(new THREE.SphereGeometry(900,32,16),m));
  if(stars){const p=[];for(let i=0;i<900;i++){const th=R(0,6.28),ph=R(.15,1.4);p.push(Math.cos(th)*Math.cos(ph)*850,Math.sin(ph)*850,Math.sin(th)*Math.cos(ph)*850)}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.add(new THREE.Points(geo,new THREE.PointsMaterial({color:'#ffffff',size:2.2,sizeAttenuation:false,transparent:true,opacity:.8})))}
  return g}
const glowTex=ctex(128,128,(g,w,h)=>{const gr=g.createRadialGradient(64,64,0,64,64,64);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.25,'rgba(255,250,220,.55)');gr.addColorStop(1,'rgba(255,240,200,0)');g.fillStyle=gr;g.fillRect(0,0,w,h)});
export function glow(color='#fff6d8',size=10,op=1){const s=new THREE.Sprite(new THREE.SpriteMaterial({map:glowTex,color,transparent:true,opacity:op,blending:THREE.AdditiveBlending,depthWrite:false}));s.scale.set(size,size,1);return s}

/* ---------- crowd textures ---------- */
const crowdCache={};
export function crowdTex(colors,frame=0,rows=24,cols=32){const k=colors.join()+frame;if(crowdCache[k])return crowdCache[k];const rr_=mulberry(77+frame*0);
  return crowdCache[k]=ctex(1024,1024,(g,w,h)=>{g.fillStyle='#646a7a';g.fillRect(0,0,w,h);const cw=w/cols,rh=h/rows;
    for(let r=0;r<rows;r++){g.fillStyle='rgba(0,0,0,.25)';g.fillRect(0,r*rh+rh*.82,w,rh*.18);
      for(let c=0;c<cols;c++){const rnd2=rr_();const col=colors[Math.floor(rnd2*colors.length)];const sk=SKINS[Math.floor(rr_()*SKINS.length)];const up=frame&&rr_()<.6?-rh*.16:0;const x=c*cw+cw/2+(rr_()-.5)*cw*.3,y=h-(r*rh+rh*.55)+up;
        g.fillStyle=col;rr(g,x-cw*.36,y+rh*.1,cw*.72,rh*.5,cw*.25);g.fill();g.fillStyle=sk;g.beginPath();g.arc(x,y,cw*.27,0,7);g.fill();
        if(frame&&up&&rr_()<.5){g.strokeStyle=sk;g.lineWidth=5;g.beginPath();g.moveTo(x-cw*.3,y+rh*.2);g.lineTo(x-cw*.42,y-rh*.3);g.moveTo(x+cw*.3,y+rh*.2);g.lineTo(x+cw*.42,y-rh*.3);g.stroke()}
        if(rr_()<.08){g.fillStyle=col;g.fillRect(x+cw*.2,y-rh*.6,cw*.5,rh*.35)}}}},[1,1])}

/* ---------- confetti ---------- */
export function confetti(n,colors,area=[40,30,40],center=V(0,0,0)){const geo=new THREE.PlaneGeometry(.22,.34);const m=new THREE.MeshBasicMaterial({side:THREE.DoubleSide,vertexColors:false});
  const im=new THREE.InstancedMesh(geo,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),n);const d=[];const col=new THREE.Color();
  for(let i=0;i<n;i++){d.push({x:R(-1,1)*area[0],y:R(0,1)*area[1],z:R(-1,1)*area[2],s:R(.8,2),r:R(0,6),w:R(1,4),ph:R(0,6)});im.setColorAt(i,col.set(colors[i%colors.length]))}
  im.position.copy(center);const mt=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),sc=V(1,1,1);
  im.userData.update=(t,scale=1)=>{for(let i=0;i<n;i++){const p=d[i];let y=p.y-t*p.s*2.2;y=((y%area[1])+area[1])%area[1];
    e.set(p.r+t*p.w,p.r*2+t*p.w*.7,0);q.setFromEuler(e);sc.setScalar(scale);mt.compose(V(p.x+Math.sin(t*p.w+p.ph)*.6,y,p.z),q,sc);im.setMatrixAt(i,mt)}im.instanceMatrix.needsUpdate=true};
  im.userData.update(0);return im}

/* ---------- text plaques ---------- */
export function plaque(lines,w,h,o={}){const ppu=o.ppu||120;const tex=ctex(Math.round(w*ppu),Math.round(h*ppu),(g,W,H)=>{
    g.fillStyle=o.bg||'#14182a';g.fillRect(0,0,W,H);if(o.grad){const gr=g.createLinearGradient(0,0,0,H);gr.addColorStop(0,o.grad[0]);gr.addColorStop(1,o.grad[1]);g.fillStyle=gr;g.fillRect(0,0,W,H)}
    if(o.border!==false){g.strokeStyle=o.border||'#e8c14a';g.lineWidth=Math.max(6,H*.04);rr(g,g.lineWidth,g.lineWidth,W-g.lineWidth*2,H-g.lineWidth*2,H*.08);g.stroke()}
    const n=lines.length;lines.forEach((l,i)=>{const L=typeof l==='string'?{t:l}:l;fitText(g,L.t,W/2,H*(i+.5)/n+(L.dy||0)*H,W*.88,(L.s||.8/n)*H,L.c||o.fg||'#fff',{stroke:L.stroke,shadow:4})})});
  const side=toon(o.side||'#0d0f1a');const front=new THREE.MeshBasicMaterial({map:tex,toneMapped:false});
  const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,o.d||.25),[side,side,side,side,front,side]);if(o.ol!==false)OL(m,.03);m.castShadow=!!o.cast;m.userData.tex=tex;return m}

/* ---------- dispose ---------- */
export function disposeAll(obj){obj.traverse(o=>{if(o.geometry&&!o.userData.outline)o.geometry.dispose();const ms=Array.isArray(o.material)?o.material:[o.material];
  for(const m of ms){if(!m||m.userData?.keep)continue;if(m.map&&!m.map.userData?.c?.keep&&!Object.values(shirtCache).includes(m.map)&&!Object.values(crowdCache).includes(m.map)&&m.map!==ballTex&&m.map!==glowTex)m.map.dispose();if(!Object.values(OLC).includes(m))m.dispose()}})}
