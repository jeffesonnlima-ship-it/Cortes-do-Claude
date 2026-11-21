const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
  const [mode,out,a,b]=process.argv.slice(2);
  const br=await chromium.launch();
  const pg=await br.newPage({viewport:{width:540,height:960},deviceScaleFactor:mode==='full'?2:1});
  const errs=[];pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(__dirname,'scene.html'));await pg.evaluate(()=>document.fonts.ready);
  fs.mkdirSync(out,{recursive:true});
  let times;
  if(mode==='full'){const s=+a,e=+b;times=[];for(let i=s;i<e;i++)times.push(i);}
  else times=process.argv.slice(4).length?process.argv.slice(4).map(Number):[];
  for(let k=0;k<times.length;k++){const t=mode==='full'?times[k]/30:times[k];
    await pg.evaluate(t=>render(t),t);
    const name=mode==='full'?`f${String(times[k]).padStart(5,'0')}.png`:`p${String(k).padStart(3,'0')}.jpg`;
    await pg.screenshot({path:`${out}/${name}`,type:mode==='full'?'png':'jpeg'});}
  if(errs.length)console.log('ERR',errs.slice(0,5));
  await br.close();
})();
