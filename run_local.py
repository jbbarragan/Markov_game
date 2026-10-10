"""Juego local con Python nativo; no necesita instalar paquetes ni descargar Pyodide."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
from threading import Lock
import importlib.util
import json
import webbrowser
import argparse

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('canfinder', ROOT/'docs/game-v5/core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
MUTEX = Lock()

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def response(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/canfinder':
            return self.response({'engine':'canfinder-python','version':'5.0'})
        super().do_GET()

    def do_POST(self):
        if self.path != '/api/canfinder': return self.response({'error':'Ruta desconocida'},404)
        try:
            length = int(self.headers.get('Content-Length',0))
            if not 0 < length < 100000: raise ValueError('Solicitud inválida')
            request = self.rfile.read(length).decode('utf-8')
            with MUTEX: result = json.loads(core.dispatch(request))
            self.response(result)
        except Exception as error: self.response({'error':str(error)},400)

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8000);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    url=f'http://127.0.0.1:{args.port}/reporte-local.html'
    print('Can Finder 5000 · versión 5.0\n'+url+'\nCtrl+C para cerrar. Abre una sola pestaña del juego por servidor.',flush=True)
    if not args.no_browser: webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
