"""Servidor local del reporte y juego, sin dependencias externas."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import webbrowser

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    server = ThreadingHTTPServer(('127.0.0.1', 8000), partial(SimpleHTTPRequestHandler, directory=str(root)))
    url='http://127.0.0.1:8000/reporte-local.html'
    print('Reporte:',url, '\nCtrl+C para cerrar. Python del navegador requiere internet.')
    webbrowser.open(url)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
