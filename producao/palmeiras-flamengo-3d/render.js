const {chromium}=require('playwright');const {spawn}=require('child_process');
const [,,a,b,out]=process.argv;const FPS=30;
(async()=>{const br=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const p=await br.newPage({viewport:{width:720,height:1280}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/v3d/index.html');await p.waitForFunction(()=>window.READY,null,{timeout:120000});
const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p',out]);
let t0=Date.now();
for(let f=+a;f<+b;f++){await p.evaluate(t=>renderAt(t),f/FPS);const buf=await p.screenshot({type:'jpeg',quality:94});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if(f%60==0)console.log(out,f,((Date.now()-t0)/((f-+a+1))).toFixed(0)+'ms/f');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));if(errs.length)console.log('ERR',errs.slice(0,3));console.log('DONE',out);await br.close()})();
