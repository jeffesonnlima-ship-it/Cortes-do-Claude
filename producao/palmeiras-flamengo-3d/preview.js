const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:720,height:1280}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('http://127.0.0.1:8765/v3d/index.html');try{await p.waitForFunction(()=>window.READY,null,{timeout:60000})}catch(e){console.log('ERR',errs.join('\n'));process.exit(1)}
const ts=process.argv[2].split(',').map(Number);
for(const t of ts){try{const id=await p.evaluate(t=>renderAt(t),t);await p.screenshot({path:`prev/${t.toFixed(2)}.jpg`,type:'jpeg',quality:80});console.log(t,id)}catch(e){console.log('fail',t,e.message.slice(0,300))}}
if(errs.length)console.log('ERRORS:\n'+errs.slice(0,5).join('\n'));await b.close()})();
