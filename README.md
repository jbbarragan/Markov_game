# Can Finder 5000 — versión 5.0

## Abrir en Windows
Extrae este ZIP en una carpeta nueva y ejecuta INICIAR_JUEGO.bat. También puedes abrir una terminal en esa carpeta y ejecutar:

```sh
python run_local.py
```

Se abre http://127.0.0.1:8000/reporte-local.html. Este servidor ejecuta el motor Python nativo: no requiere paquetes externos ni internet. Usa una sola pestaña por servidor local. Para elegir otro puerto: `python run_local.py --port 8001`.

## Comprobar que abriste esta versión
El encabezado del juego debe decir **VERSIÓN 5.0**. Tiene batería segmentada, tasas de descarga, selector de derrape y botones CSV en modo agente. No contiene formulario de bitácora.

La batería empieza a bajar con tu primera acción: 1 %/s por defecto (100 segundos). Puedes elegir 0.5 %/s (200 segundos) o tasas más altas. El perfil aleatorio puede seleccionar 9 %/s y solo durar 11 segundos; úsalo si deseas esa dificultad. Flechas para moverte; mantenerlas repite a intervalos de 180 ms. El derrape gaussiano puede desviarte: desactívalo si deseas dirección exacta.

## GitHub Pages
Reemplaza el contenido del repositorio con el contenido del ZIP, incluidos docs, build_local_report.py y .github/workflows/main.yml. Conserva GitHub Actions como origen de Pages. El juego nuevo está en **docs/game-v5/**. La ruta anterior docs/game/index.html redirige a esta versión; la antigua página de bitácora queda reemplazada por una redirección sin contenido ni entrada de navegación.

Es necesario esperar a que termine el despliegue. Un ZIP descargado no actualiza automáticamente el sitio publicado. Comprueba el rótulo VERSIÓN 5.0 en la página. El juego publicado incluye Pyodide 0.27.2 en docs/game-v5/vendor/pyodide y lo carga desde el mismo sitio, sin depender de un CDN externo. Sube también esa carpeta (incluido el archivo WASM).

## Agente y datos
Aprender desde cero borra Q y los datos anteriores del agente. Entrenar añade 500 episodios y se detiene; Evaluar ejecuta un episodio sin actualizar Q. El botón Pausar permite detener un bloque de entrenamiento. Los CSV contienen telemetría reciente y balances por episodio completo. No se registran partidas manuales.

```sh
python docs/game-v5/core.py --episodes 500 --mode extended --drain random --telemetry-csv telemetria.csv --balance-csv balances.csv
python -m unittest discover -s tests -v
```

## Informe
reporte-local.html y las páginas de docs explican los requisitos visuales, las ecuaciones, las recompensas y las adaptaciones respecto de la guía. No incluyen resultados humanos inventados. `python build_local_report.py` regenera la copia local.
