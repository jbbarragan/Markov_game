'use strict';
const $=id=>document.getElementById(id), canvas=$('map'), ctx=canvas.getContext('2d');
const worker=new Worker('worker.js?v=3');
const FONT='"Press Start 2P","Courier New",monospace', BKEYS=['latas','movimiento','espera','rescates'];
let serial=0, pending=new Map(), state=null, agent=null, busy=false, paused=false, pilot='manual', queued=4, timer=0, batch=false, rescueUntil=0, trace=[], lastT=-1;
const col=name=>getComputedStyle(document.body).getPropertyValue(name).trim()||'#888';
function lock(){for(const id of ['mode','drain','seed','reset','ai','train','evaluate','export','dlTele','dlBal'])$(id).disabled=busy||batch;}
function rpc(op,fields={}){return new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});worker.postMessage({id,op,...fields});});}
worker.onmessage=({data})=>{const p=pending.get(data.id);if(!p)return;pending.delete(data.id);data.error?p.reject(Error(data.error)):p.resolve(data.result);};
worker.onerror=e=>{for(const p of pending.values())p.reject(Error(e.message));pending.clear();};
function fail(e){paused=true;batch=false;$('status').textContent='Error: '+e.message+' · Revisa internet y abre la página mediante HTTP/HTTPS. Recarga para reintentar.';}
function download(name,data,type='application/json'){const a=document.createElement('a'),u=URL.createObjectURL(new Blob([data],{type}));a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
const seedValue=()=>{const s=parseInt($('seed').value,10);return Number.isFinite(s)&&s>=0?s:42;};

/* ---------- Píxeles: todo (tablero y gráficas) se dibuja a baja resolución y se amplía sin suavizar ---------- */
function pixel(x,y,w,h,color){ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),w,h);}
function dot(g,x,y,c){g.fillStyle=c;g.fillRect(Math.round(x),Math.round(y),1,1);}
function line(g,x0,y0,x1,y1,c,dash=false){x0=Math.round(x0);y0=Math.round(y0);x1=Math.round(x1);y1=Math.round(y1);const dx=Math.abs(x1-x0),dy=-Math.abs(y1-y0),sx=x0<x1?1:-1,sy=y0<y1?1:-1;let err=dx+dy,n=0;for(;;){if(!dash||n%2===0)dot(g,x0,y0,c);if(x0===x1&&y0===y1)break;const e2=2*err;if(e2>=dy){err+=dy;x0+=sx;}if(e2<=dx){err+=dx;y0+=sy;}n++;}}
function frame(c){const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.clearRect(0,0,c.width,c.height);g.fillStyle=col('--lo');g.fillRect(0,0,c.width,c.height);return g;}
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
  pixel(1,1,38,38,'#244e60');pixel(3,3,34,2,'#63cfda');pixel(3,36,34,2,'#63cfda');ctx.fillStyle='#85e1e4';ctx.font='8px '+FONT;ctx.fillText('BASE',4,27);
  if(!state){robot(0,0);return;}
  for(const [x,y,c]of state.cans){const colors=['#62c2a4','#70b9eb','#e494b7'];pixel(x*40+15,y*40+27,13,3,'#1f3033');pixel(x*40+15,y*40+12,10,14,colors[c]);pixel(x*40+15,y*40+10,10,3,'#dce0cc');pixel(x*40+17,y*40+13,2,10,'#eff1d4');pixel(x*40+15,y*40+25,10,2,'#788e84');pixel(x*40+21,y*40+16,3,4,'#34544d');}
  const off=performance.now()<rescueUntil;const pos=off&&state.last.old?state.last.old:[state.x,state.y];robot(pos[0]*40,pos[1]*40,!state.high,off);
}
function gaussian(){const c=$('gaussian'),g=frame(c),mid=70,k=21,fill=col('--grid');
  for(let i=0;i<c.width;i++){const z=(i-mid)/k,y=Math.round(28-24*Math.exp(-z*z/2));for(let j=y+1;j<=28;j++)if((i+j)%2===0)dot(g,i,j,fill);}
  let py=null;for(let i=0;i<c.width;i++){const z=(i-mid)/k,y=28-24*Math.exp(-z*z/2);if(py!==null)line(g,i-1,py,i,y,col('--cyan'));py=y;}
  line(g,0,29,c.width-1,29,col('--muted'));
  for(const a of [-30,30])line(g,mid+a/25*k,2,mid+a/25*k,29,col('--gold'),true);
  if(state){const x=Math.max(0,Math.min(c.width-2,Math.round(mid+state.last.angle/25*k)));g.fillStyle=col('--red');g.fillRect(x,1,2,29);}}
function batteryTrace(){const c=$('trace'),g=frame(c),xmax=Math.max(100,trace.length?trace[trace.length-1][0]:0),X=t=>3+t/xmax*(c.width-6),Y=e=>c.height-4-e/100*(c.height-8);
  for(const e of [25,50,75])line(g,3,Y(e),c.width-4,Y(e),col('--grid'),true);
  line(g,3,Y(40),c.width-4,Y(40),col('--red'),true);line(g,3,c.height-4,c.width-4,c.height-4,col('--muted'));line(g,3,2,3,c.height-4,col('--muted'));
  for(let i=1;i<trace.length;i++)line(g,X(trace[i-1][0]),Y(trace[i-1][1]),X(trace[i][0]),Y(trace[i][1]),col('--green'));
  if(trace.length){const p=trace[trace.length-1];g.fillStyle=col('--gold');g.fillRect(Math.round(X(p[0]))-1,Math.round(Y(p[1]))-1,3,3);}}
function chart(){const c=$('chart'),g=frame(c),h=agent?.history||[];
  if(!h.length){$('ymax').textContent='';$('ymin').textContent='';g.fillStyle=col('--muted');for(let i=0;i<c.width;i+=4)dot(g,i,c.height-3,col('--grid'));return;}
  const vals=h.map(x=>x.score),min=Math.min(0,...vals),max=Math.max(1,...vals),X=i=>3+i/Math.max(1,h.length-1)*(c.width-6),Y=v=>c.height-4-(v-min)/(max-min)*(c.height-8);
  $('ymax').textContent=max.toFixed(1);$('ymin').textContent=min.toFixed(1);
  if(min<0)line(g,3,Y(0),c.width-4,Y(0),col('--muted'),true);
  for(let i=1;i<h.length;i++)line(g,X(i-1),Y(vals[i-1]),X(i),Y(vals[i]),col('--cyan'));
  const avg=vals.map((_,i)=>{const s=vals.slice(Math.max(0,i-19),i+1);return s.reduce((a,b)=>a+b,0)/s.length;});
  for(let i=1;i<h.length;i++)line(g,X(i-1),Y(avg[i-1]),X(i),Y(avg[i]),col('--gold'));}
function redraw(){draw();gaussian();batteryTrace();chart();}

/* ---------- Interfaz ---------- */
const bat=$('battery');for(let i=0;i<20;i++)bat.append(document.createElement('i'));
const sign=v=>(v<0?'−':'+')+Math.abs(v).toFixed(2);
function render(result){state=result.state;agent=result.agent;
  if(state.t===0)trace=[[0,state.energy]];else if(state.t!==lastT)trace.push([state.elapsed,state.energy]);lastT=state.t;
  $('position').textContent=`POSICIÓN (${state.x}, ${state.y}) · 10 × 10`;
  const lit=Math.ceil(state.energy/5);[...bat.children].forEach((b,i)=>b.classList.toggle('on',i<lit));bat.classList.toggle('low',!state.high);
  $('energy').textContent=state.energy.toFixed(1)+'%';$('state').textContent=state.high?'ALTO · SH':'BAJO · SL';$('state').style.color=state.high?col('--green'):col('--red');
  $('rate').textContent=state.rate+' %/s';$('autonomy').textContent='AUTONOMÍA ≈ '+Math.round(state.autonomy)+' s';
  document.querySelectorAll('#pips span').forEach(s=>s.classList.toggle('on',Number(s.dataset.r)===state.rate));
  $('profile').textContent=state.profile==='mixed'?'Perfil: intercalado, la tasa cambia entre 1 y 9 %/s a lo largo de la partida.':`Perfil: constante ${state.rate} %/s`+(state.drain_option==='random'?' (sorteado para esta partida).':'.');
  for(const [id,value]of Object.entries({turn:`${state.t}/100`,score:state.score.toFixed(2),cans:state.caught,rescues:state.rescues,return:state.discounted.toFixed(3),time:state.elapsed.toFixed(0)+' s','drain-last':state.last.drain.toFixed(2),angle:state.last.angle.toFixed(2),transition:state.last.message}))$(id).textContent=value;
  for(const k of BKEYS){const b=state.balance[k],el=$('b-'+k);el.textContent=sign(b);el.className=b>0?'pos':b<0?'neg':'';$('n-'+k).textContent='×'+state.counts[k];}
  $('prob').textContent=(state.high?'α(E) = '+(state.alpha*100).toFixed(1)+'% · seguir alto':'β(E) = '+(state.beta*100).toFixed(1)+'% · sobrevivir')+' en el siguiente segundo';
  $('pilot').textContent=pilot==='manual'?'CONTROL MANUAL':pilot==='learn'?'PYTHON · APRENDIENDO':'PYTHON · EVALUACIÓN';
  $('learning').textContent=`Episodios: ${agent.episodes} · ε = ${agent.epsilon.toFixed(3)} · Estados visitados: ${agent.states} · Exploración: ${agent.explorations} / Explotación: ${agent.exploitations}`;
  $('downloads').hidden=pilot==='manual';
  $('dlinfo').textContent=`Telemetría: ${agent.telemetry_rows} pasos recientes · Balance de recompensas: ${agent.episodes+agent.evaluations} episodios (entrenamiento y evaluación).`;
  $('v2').textContent=state.mode==='practice'?'+1':'+2';$('v3').textContent=state.mode==='practice'?'+1':'+4';
  if(state.last.rescue){rescueUntil=performance.now()+850;$('alert').hidden=false;setTimeout(()=>{$('alert').hidden=true;draw();},870);}
  redraw();
  $('status').textContent=state.done?'Partida terminada · 100 turnos. '+(pilot==='manual'?'Pulsa Nueva partida manual para jugar otra.':'El siguiente episodio comienza automáticamente.'):(paused?'Pausado.':pilot==='manual'?(state.mode==='practice'?'Tu decisión es la política. Cada tecla válida avanza un turno.':'Tiempo activo: una decisión por segundo. Sin acción, el robot espera y consume batería.'):'Python decide las acciones. '+(pilot==='learn'?'Q se actualiza con cada transición.':'Q permanece fija.'));
}
async function newGame(fresh=false,nextPilot='manual'){
  if(busy||batch)return;busy=true;lock();clearTimeout(timer);
  try{pilot=nextPilot;paused=false;$('pause').textContent='Pausar';queued=4;render(await rpc('reset',{mode:$('mode').value,seed:seedValue(),drain:$('drain').value,fresh}));}catch(e){fail(e);}finally{busy=false;lock();schedule();}
}
async function action(a){if(busy||paused||!state||state.done||batch||performance.now()<rescueUntil)return;busy=true;
  try{render(await rpc('step',{action:a,dt:1}));}catch(e){fail(e);}finally{busy=false;}}
function schedule(){clearTimeout(timer);if(!state||paused||batch)return;timer=setTimeout(tick,pilot==='manual'?1000:Number($('speed').value));}
async function tick(){if(paused||batch)return;if(document.hidden){schedule();return;}if(busy||performance.now()<rescueUntil){schedule();return;}
  if(pilot==='manual'){if(state.mode==='extended'&&!state.done){const a=queued;queued=4;await action(a);}schedule();return;}
  busy=true;try{if(state.done){if(pilot==='eval'){paused=true;$('status').textContent='Evaluación terminada. Datos disponibles para descargar.';}else{render(await rpc('reset',{mode:state.mode,seed:Math.floor(Math.random()*2147483647),drain:state.drain_option}));}}else{render(await rpc('auto',{learn:pilot==='learn'}));}}catch(e){fail(e);}finally{busy=false;lock();schedule();}}
function manual(a){if(pilot!=='manual'||busy||batch||paused)return;if(a===5&&state&&(state.x!==0||state.y!==0)){$('status').textContent='Solo puedes recargar en la estación (0,0).';return;}if(state?.mode==='extended'){queued=a;$('status').textContent='Siguiente acción: '+['Norte','Este','Sur','Oeste','Esperar','Recargar'][a];}else action(a);}
$('reset').onclick=()=>{$('seed').value=seedValue()+1;newGame(false,'manual');};   /* semilla nueva = partida y desgaste nuevos */
$('ai').onclick=()=>newGame(true,'learn');$('mode').onchange=()=>newGame(true,'manual');$('drain').onchange=()=>newGame(false,'manual');
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'Reanudar':'Pausar';$('status').textContent=paused?'Pausado.':'Simulación activa.';schedule();};
$('evaluate').onclick=()=>newGame(false,'eval');$('speed').onchange=schedule;
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{$('status').textContent='Pantalla completa no disponible aquí. Abre el juego en una pestaña independiente.';}};
for(const b of document.querySelectorAll('[data-action]'))b.onclick=()=>manual(Number(b.dataset.action));
canvas.addEventListener('keydown',e=>{const map={ArrowUp:0,ArrowRight:1,ArrowDown:2,ArrowLeft:3,' ':4,r:5,R:5};if(e.key in map){e.preventDefault();if(!e.repeat)manual(map[e.key]);}});
$('train').onclick=async()=>{if(busy||batch||!state)return;batch=true;paused=false;clearTimeout(timer);$('train').disabled=true;lock();
  try{for(let i=0;i<50;i++){if(paused)break;render(await rpc('train',{count:10}));$('status').textContent=`Entrenando Python: ${(i+1)*10} / 500 episodios adicionales… Pausar detiene al terminar este bloque.`;}pilot='eval';render(await rpc('state'));}catch(e){fail(e);}finally{batch=false;lock();schedule();}};
/* Descargas del agente: solo visibles cuando Python controla el robot */
async function csvDownload(kind,name){if(!state)return;try{const r=await rpc('csv',{kind});download(name,'\ufeff'+r.csv,'text/csv;charset=utf-8');$('dlinfo').textContent=`${name}: ${r.rows} filas descargadas.`;}catch(e){fail(e);}}
$('dlTele').onclick=()=>csvDownload('telemetry','can-finder-telemetria.csv');
$('dlBal').onclick=()=>csvDownload('balance','can-finder-balance-recompensas.csv');
$('export').onclick=async()=>{if(!state)return;try{download('can-finder-q-parametros.json',JSON.stringify(await rpc('export'),null,2));}catch(e){fail(e);}};
/* Captura del tablero y la telemetría visible */
function snapshot(){const c=document.createElement('canvas');c.width=760;c.height=470;const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.fillStyle=col('--bg');g.fillRect(0,0,760,470);g.drawImage(canvas,15,50,400,400);g.fillStyle=col('--text');g.font='bold 13px '+FONT;g.fillText('CAN FINDER 5000 · '+(state.mode==='practice'?'PRÁCTICA':'EXTENDIDA'),15,30);g.font='10px '+FONT;
  [`Turno: ${state.t}/100`,`Bateria: ${state.energy.toFixed(1)}%`,state.high?'Estado ALTO (SH)':'Estado BAJO (SL)',`Desgaste: ${state.rate} %/s`,`Puntaje: ${state.score.toFixed(2)}`,`G0: ${state.discounted.toFixed(3)}`,`Latas: ${state.caught}`,`Rescates: ${state.rescues}`,`Angulo: ${state.last.angle.toFixed(2)}`,`Semilla: ${state.seed}`,`Control: ${pilot}`].forEach((s,i)=>g.fillText(s,435,75+i*31));return c.toDataURL('image/png');}
$('capture').onclick=()=>{if(!state)return;const a=document.createElement('a');a.href=snapshot();a.download='can-finder-captura.png';a.click();};
window.addEventListener('message',e=>{if(e.origin===location.origin&&e.data?.theme){document.body.classList.toggle('light',e.data.theme==='light');if(state)$('state').style.color=state.high?col('--green'):col('--red');redraw();}});
document.fonts?.ready.then(()=>{if(state)redraw();else draw();});
draw();gaussian();batteryTrace();chart();newGame(true);
