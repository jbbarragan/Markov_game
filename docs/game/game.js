'use strict';
const $=id=>document.getElementById(id), canvas=$('map'), ctx=canvas.getContext('2d');
const worker=new Worker('worker.js');
let serial=0, pending=new Map(), state=null, agent=null, busy=false, paused=false, pilot='manual', queued=4, timer=0, batch=false, rescueUntil=0, savedTurn=false, sessions=[];
try{sessions=JSON.parse(localStorage.getItem('cf-sessions')||'[]');if(!Array.isArray(sessions))sessions=[];}catch{}
function lock(){for(const id of ['mode','seed','reset','ai','train','evaluate','export'])$(id).disabled=busy||batch;}
function persist(key,value){try{localStorage.setItem(key,JSON.stringify(value));}catch{$('storageNotice').textContent='No se pudo guardar localmente. Descarga la bitácora antes de cerrar.';}}
function rpc(op,fields={}){return new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});worker.postMessage({id,op,...fields});});}
worker.onmessage=({data})=>{const p=pending.get(data.id);if(!p)return;pending.delete(data.id);data.error?p.reject(Error(data.error)):p.resolve(data.result);};
worker.onerror=e=>{for(const p of pending.values())p.reject(Error(e.message));pending.clear();};
function fail(e){paused=true;batch=false;$('status').textContent='Error: '+e.message+' · Revisa internet y abre la página mediante HTTP/HTTPS. Recarga para reintentar.';}
function download(name,data,type='application/json'){const a=document.createElement('a'),u=URL.createObjectURL(new Blob([data],{type}));a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
function pixel(x,y,w,h,color){ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),w,h);}
function robot(x,y,low=false,off=false){
  pixel(x+5,y+28,31,7,'#14202a');pixel(x+5,y+23,8,12,'#18252a');pixel(x+27,y+23,8,12,'#18252a');
  for(let j=0;j<3;j++){pixel(x+6,y+24+j*4,6,2,'#68787b');pixel(x+28,y+24+j*4,6,2,'#68787b');}
  pixel(x+12,y+17,16,15,'#c88734');pixel(x+14,y+17,14,11,'#ecc763');pixel(x+15,y+18,11,3,'#ffdc86');
  pixel(x+18,y+13,4,5,'#9c9f88');pixel(x+7,y+6,12,10,'#c0c8bb');pixel(x+21,y+5,12,10,'#d0d7c8');pixel(x+8,y+8,10,6,'#263842');pixel(x+22,y+7,10,6,'#263842');
  pixel(x+12,y+9,4,4,off?'#66777c':'#b7e4e4');pixel(x+24,y+8,4,4,off?'#66777c':'#b7e4e4');pixel(x+19,y+8,3,3,'#707d73');pixel(x+8,y+18,4,5,'#d4a750');pixel(x+28,y+19,4,5,'#d4a750');pixel(x+16,y+25,8,3,off?'#6e7477':low?'#ff6e6a':'#83ecaa');
}
function draw(){
  ctx.imageSmoothingEnabled=false;
  for(let y=0;y<10;y++)for(let x=0;x<10;x++){
    pixel(x*40,y*40,40,40,(x+y)%2?'#344442':'#30403f');pixel(x*40,y*40,40,1,'#41504b');pixel(x*40,y*40,1,40,'#41504b');
    const n=(x*31+y*17)%29;pixel(x*40+5+n,y*40+9,2,2,'#536052');pixel(x*40+12,y*40+31,4,1,'#4b5750');
  }
  pixel(1,1,38,38,'#244e60');pixel(3,3,34,2,'#63cfda');pixel(3,36,34,2,'#63cfda');ctx.fillStyle='#85e1e4';ctx.font='8px monospace';ctx.fillText('BASE',8,36);
  if(!state){robot(0,0);return;}
  for(const [x,y,c]of state.cans){const colors=['#62c2a4','#70b9eb','#e494b7'];pixel(x*40+15,y*40+27,13,3,'#1f3033');pixel(x*40+15,y*40+12,10,14,colors[c]);pixel(x*40+15,y*40+10,10,3,'#dce0cc');pixel(x*40+17,y*40+13,2,10,'#eff1d4');pixel(x*40+15,y*40+25,10,2,'#788e84');pixel(x*40+21,y*40+16,3,4,'#34544d');}
  const off=performance.now()<rescueUntil;const pos=off&&state.last.old?state.last.old:[state.x,state.y];robot(pos[0]*40,pos[1]*40,!state.high,off);
}
function gaussian(){const c=$('gaussian'),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);g.strokeStyle='#7fa3ac';g.beginPath();for(let i=0;i<280;i++){const z=(i-140)/42;const y=58-48*Math.exp(-z*z/2);i?g.lineTo(i,y):g.moveTo(i,y);}g.stroke();for(const a of [-30,30]){g.strokeStyle='#bc9362';g.beginPath();g.moveTo(140+a/25*42,5);g.lineTo(140+a/25*42,60);g.stroke();}g.fillStyle='#f5c769';g.fillRect(Math.max(0,Math.min(277,140+state.last.angle/25*42)),3,3,60);}
function chart(){const c=$('chart'),g=c.getContext('2d');g.clearRect(0,0,c.width,c.height);const h=agent?.history||[];g.font='12px monospace';g.fillStyle='#99afb6';if(!h.length){g.fillText('Sin episodios entrenados. Activa Python para comenzar.',20,65);return;}let min=Math.min(0,...h.map(x=>x.score)),max=Math.max(1,...h.map(x=>x.score));g.fillText(max.toFixed(1),4,15);g.fillText(min.toFixed(1),4,120);g.strokeStyle='#e9b85e';g.beginPath();h.forEach((p,i)=>{const x=40+i/Math.max(1,h.length-1)*745,y=115-(p.score-min)/(max-min)*100;i?g.lineTo(x,y):g.moveTo(x,y);});g.stroke();}
function render(result){state=result.state;agent=result.agent;
  $('position').textContent=`POSICIÓN (${state.x}, ${state.y}) · 10 × 10`;
  $('energy').textContent=state.energy.toFixed(1)+'%';$('bar').style.width=state.energy+'%';$('bar').style.background=state.high?'#80d7a3':'#ee7970';$('state').textContent=state.high?'ALTO · SH':'BAJO · SL';$('state').style.color=state.high?'#80d7a3':'#ee7970';
  for(const [id,value]of Object.entries({turn:`${state.t} / 100`,score:state.score.toFixed(2),cans:state.caught,rescues:state.rescues,return:state.discounted.toFixed(3),time:state.elapsed.toFixed(0)+' s',drain:state.last.drain.toFixed(2),angle:state.last.angle.toFixed(2),transition:state.last.message}))$(id).textContent=value;
  $('prob').textContent=(state.high?'α(E) = '+(state.alpha*100).toFixed(1)+'% · seguir alto':'β(E) = '+(state.beta*100).toFixed(1)+'% · sobrevivir')+(state.mode==='extended'?' (solo componente gaussiana)':'');
  $('pilot').textContent=pilot==='manual'?'CONTROL MANUAL':pilot==='learn'?'PYTHON · APRENDIENDO':'PYTHON · EVALUACIÓN';
  $('learning').textContent=`Episodios: ${agent.episodes} · ε = ${agent.epsilon.toFixed(3)} · Estados visitados: ${agent.states} · Exploración: ${agent.explorations} / Explotación: ${agent.exploitations}`;
  $('v2').textContent=state.mode==='practice'?'+1':'+2';$('v3').textContent=state.mode==='practice'?'+1':'+4';
  if(state.last.rescue){rescueUntil=performance.now()+850;$('alert').hidden=false;setTimeout(()=>{$('alert').hidden=true;draw();},870);}
  draw();gaussian();chart();
  $('status').textContent=state.done?'Partida terminada · 100 turnos. '+(pilot==='manual'?'Se registrará en la bitácora.':'El siguiente episodio comienza automáticamente.'):(paused?'Pausado.':pilot==='manual'?(state.mode==='practice'?'Tu decisión es la política. Cada tecla válida avanza un turno.':'Tiempo activo: una decisión por segundo. Sin acción, el robot espera y consume batería.'):'Python decide las acciones. '+(pilot==='learn'?'Q se actualiza con cada transición.':'Q permanece fija.'));
}
async function newGame(fresh=false,nextPilot='manual'){
  if(busy||batch)return;busy=true;lock();clearTimeout(timer);
  try{pilot=nextPilot;paused=false;$('pause').textContent='Pausar';queued=4;savedTurn=false;render(await rpc('reset',{mode:$('mode').value,seed:Number($('seed').value)||42,fresh}));}catch(e){fail(e);}finally{busy=false;lock();schedule();}
}
async function action(a){if(busy||paused||!state||state.done||batch||performance.now()<rescueUntil)return;busy=true;
  try{render(await rpc('step',{action:a,dt:1}));await finish();}catch(e){fail(e);}finally{busy=false;}}
async function finish(){if(!state.done||savedTurn)return;savedTurn=true;if(pilot==='manual'){
  const data=await rpc('export');sessions.push({date:new Date().toISOString(),state:data.state,log:data.log,parameters:data.parameters,screenshot:snapshot()});sessions=sessions.slice(-12);persist('cf-sessions',sessions);showSessions();
}}
function schedule(){clearTimeout(timer);if(!state||paused||batch)return;timer=setTimeout(tick,pilot==='manual'?1000:Number($('speed').value));}
async function tick(){if(paused||batch)return;if(document.hidden){schedule();return;}if(busy||performance.now()<rescueUntil){schedule();return;}
  if(pilot==='manual'){if(state.mode==='extended'&&!state.done){const a=queued;queued=4;await action(a);}schedule();return;}
  busy=true;try{if(state.done){if(pilot==='eval'){paused=true;$('status').textContent='Evaluación terminada. Datos disponibles para exportar.';}else{savedTurn=false;render(await rpc('reset',{mode:state.mode,seed:Math.floor(Math.random()*2147483647)}));}}else{render(await rpc('auto',{learn:pilot==='learn'}));}}catch(e){fail(e);}finally{busy=false;lock();schedule();}}
function manual(a){if(pilot!=='manual'||busy||batch||paused)return;if(a===5&&state&&(state.x!==0||state.y!==0)){$('status').textContent='Solo puedes recargar en la estación (0,0).';return;}if(state?.mode==='extended'){queued=a;$('status').textContent='Siguiente acción: '+['Norte','Este','Sur','Oeste','Esperar','Recargar'][a];}else action(a);}
$('reset').onclick=()=>newGame(false,'manual');$('ai').onclick=()=>newGame(true,'learn');$('mode').onchange=()=>newGame(true,'manual');
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'Reanudar':'Pausar';$('status').textContent=paused?'Pausado.':'Simulación activa.';schedule();};
$('evaluate').onclick=()=>newGame(false,'eval');$('speed').onchange=schedule;
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{$('status').textContent='Pantalla completa no disponible aquí. Abre el juego en una pestaña independiente.';}};
for(const b of document.querySelectorAll('[data-action]'))b.onclick=()=>manual(Number(b.dataset.action));
canvas.addEventListener('keydown',e=>{const map={ArrowUp:0,ArrowRight:1,ArrowDown:2,ArrowLeft:3,' ':4,r:5,R:5};if(e.key in map){e.preventDefault();if(!e.repeat)manual(map[e.key]);}});
$('train').onclick=async()=>{if(busy||batch||!state)return;batch=true;paused=false;clearTimeout(timer);$('train').disabled=true;lock();
  try{for(let i=0;i<50;i++){if(paused)break;render(await rpc('train',{count:10}));$('status').textContent=`Entrenando Python: ${(i+1)*10} / 500 episodios adicionales… Pausar detiene al terminar este bloque.`;}pilot='eval';savedTurn=false;}catch(e){fail(e);}finally{batch=false;lock();schedule();}};
$('export').onclick=async()=>{if(busy||batch)return;try{download('can-finder-datos.json',JSON.stringify(await rpc('export'),null,2));}catch(e){fail(e);}};
function snapshot(){const c=document.createElement('canvas');c.width=760;c.height=470;const g=c.getContext('2d');g.fillStyle='#14232c';g.fillRect(0,0,760,470);g.drawImage(canvas,15,50,400,400);g.fillStyle='#e9e8dc';g.font='bold 19px monospace';g.fillText('CAN FINDER 5000 · '+(state.mode==='practice'?'PRÁCTICA':'EXTENDIDA'),15,30);g.font='16px monospace';[`Turno: ${state.t}/100`,`Batería: ${state.energy.toFixed(1)}%`,state.high?'Estado ALTO (SH)':'Estado BAJO (SL)',`Puntaje: ${state.score.toFixed(2)}`,`G0: ${state.discounted.toFixed(3)}`,`Latas: ${state.caught}`,`Rescates: ${state.rescues}`,`ΔE: ${state.last.drain.toFixed(2)}`,`Ángulo: ${state.last.angle.toFixed(2)}°`,`Semilla: ${state.seed}`,`Control: ${pilot}`].forEach((s,i)=>g.fillText(s,435,75+i*31));return c.toDataURL('image/png');}
function saveImage(url,name){const a=document.createElement('a');a.href=url;a.download=name;a.click();}
$('capture').onclick=()=>state&&saveImage(snapshot(),'can-finder-captura.png');
function showSessions(){const box=$('sessions');box.textContent='';const valid=sessions.filter(s=>s.state.mode==='practice').length;const intro=document.createElement('p');intro.textContent=`Práctica: ${valid} / 3 partidas completadas. Se conservan las últimas 12 partidas manuales.`;box.append(intro);sessions.forEach((s,i)=>{const d=document.createElement('div');d.className='session';d.textContent=`${i+1}. ${s.state.mode==='practice'?'Práctica':'Extendida'} · ${s.state.score.toFixed(2)} puntos · ${s.state.caught} latas · ${s.state.rescues} rescates `;const b=document.createElement('button');b.textContent='Captura PNG';b.onclick=()=>saveImage(s.screenshot,`partida-${i+1}.png`);d.append(b);box.append(d);});}
for(const id of ['reflection1','reflection2']){try{$(id).value=JSON.parse(localStorage.getItem('cf-'+id)||'""');}catch{}$(id).oninput=()=>persist('cf-'+id,$(id).value);}
$('downloadLog').onclick=()=>download('bitacora-can-finder.json',JSON.stringify({partidas:sessions,reflexiones:{politica_bateria_baja:$('reflection1').value,esperar:$('reflection2').value}},null,2));
window.addEventListener('message',e=>{if(e.origin===location.origin&&e.data?.theme)document.body.classList.toggle('light',e.data.theme==='light');});
showSessions();draw();newGame(true);
