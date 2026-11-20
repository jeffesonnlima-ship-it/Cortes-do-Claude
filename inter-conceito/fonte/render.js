const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
  const [mode,out]=[process.argv[2],process.argv[3]];
  const b=await chromium.launch();
  const pg=await b.newPage({viewport:{width:540,height:960},deviceScaleFactor:mode==='full'?2:1});
  await pg.goto('file://'+path.resolve(__dirname,'scene.html'));await pg.evaluate(()=>document.fonts.ready);
  fs.mkdirSync(out,{recursive:true});
  const times=mode==='full'?[...Array(300).keys()].map(i=>i/30):[0.3,0.85,1.3,1.9,2.2,2.8,3.2,3.6,4.25,5.0,5.5,6.5,6.9,7.5,7.8,8.2,9.0,9.8];
  for(let i=0;i<times.length;i++){await pg.evaluate(t=>render(t),times[i]);
    await pg.screenshot({path:`${out}/f${String(i).padStart(4,'0')}.${mode==='full'?'png':'jpg'}`});}
  await b.close();
})();
