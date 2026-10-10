/* Python lives in this worker: neither rendering nor UI is blocked by training. */
let py;
self.onmessage = async ({data}) => {
  try {
    if (!py) {
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js');
      py = await loadPyodide();
      const response = await fetch('core.py');
      if (!response.ok) throw Error('No se pudo cargar core.py');
      py.globals.set('__name__', 'canfinder_browser');
      await py.runPythonAsync(await response.text());
    }
    py.globals.set('request_json', JSON.stringify(data));
    const result = JSON.parse(py.runPython('dispatch(request_json)'));
    self.postMessage({id:data.id,result});
  } catch(error) { self.postMessage({id:data.id,error:String(error)}); }
};
