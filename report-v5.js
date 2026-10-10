document.addEventListener('DOMContentLoaded',()=>{
const frames=()=>[...document.querySelectorAll('iframe.cf-game')];
window.addEventListener('message',e=>{const f=frames().find(f=>f.contentWindow===e.source);if(e.origin===location.origin&&f&&Number.isFinite(e.data?.gameHeight))f.style.height=Math.max(600,e.data.gameHeight)+'px';});
for(const type of ['keydown','keyup'])document.addEventListener(type,e=>{if(e.target.matches('input,select,textarea')||!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' ','r','R'].includes(e.key))return;const f=frames().find(f=>{const b=f.getBoundingClientRect();return b.top<innerHeight&&b.bottom>0;});if(f){e.preventDefault();f.contentWindow.postMessage({control:type,key:e.key,repeat:e.repeat},location.origin);}});
window.addEventListener('blur',()=>{for(const f of frames())f.contentWindow.postMessage({clearInput:true},location.origin);});
});