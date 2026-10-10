/* Python nativo en el servidor local; Pyodide en GitHub Pages. */
let py, initialization, native=false;
async function init(){
  if(['127.0.0.1','localhost'].includes(location.hostname)){
    try{const r=await fetch('/api/canfinder',{cache:'no-store'});const info=await r.json();native=info.engine==='canfinder-python'&&info.version==='5.0';}catch{}
  }
  if(native)return;
  importScripts('vendor/pyodide/pyodide.js');
  py=await loadPyodide({indexURL:new URL('vendor/pyodide/',self.location.href).href});
  const response=await fetch('core.py?v=5',{cache:'no-store'});
  if(!response.ok)throw Error('No se pudo cargar el motor versión 5.0');
  py.globals.set('__name__','canfinder_browser');
  await py.runPythonAsync(await response.text());
}
let queue=Promise.resolve();
self.onmessage=({data})=>{
  queue=queue.then(async()=>{
    try{
      if(!initialization)initialization=init();await initialization;
      let result;
      if(native){const r=await fetch('/api/canfinder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});result=await r.json();if(!r.ok)throw Error(result.error);}
      else{py.globals.set('request_json',JSON.stringify(data));result=JSON.parse(py.runPython('dispatch(request_json)'));}
      self.postMessage({id:data.id,result});
    }catch(error){self.postMessage({id:data.id,error:String(error)});}
  });
};
