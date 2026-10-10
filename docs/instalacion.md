---
layout: default
title: Ejecutar y publicar
nav_order: 6
---
# Ejecutar y publicar

### En tu computadora
Descomprime el proyecto. En una terminal dentro de la carpeta ejecuta:

```bash
python run_local.py
```

Se abre un reporte local con el juego integrado. No necesitas Node ni instalar paquetes Python. **Sí necesitas internet para descargar Pyodide la primera vez** (no se ofrece funcionamiento offline garantizado). No abras `game/index.html` con doble clic: los workers y la lectura de Python necesitan HTTP/HTTPS. Para cerrar el servidor pulsa Ctrl+C.

### En un repositorio nuevo de GitHub
1. Crea un repositorio para esta práctica, por ejemplo `can-finder-5000`.
2. Sube **el contenido de la carpeta extraída a la raíz**, incluyendo `.github`, `docs`, `tests`, `README.md` y `run_local.py`. La estructura no debe quedar dentro de otra carpeta `can-finder-5000` en el repo.
3. En **Settings → Pages → Build and deployment → Source**, selecciona **GitHub Actions**.
4. Haz push a `main`. El flujo `Publicar reporte y juego` prueba el motor, construye Just the Docs y publica el sitio.
5. Abre la URL que muestra la ejecución de Actions, normalmente `https://TU_USUARIO.github.io/can-finder-5000/`.

La ruta base se obtiene automáticamente de Pages: no es necesario escribir el nombre del repositorio en el código. Las rutas del juego son relativas y funcionan dentro de un subdirectorio.

### Si lo integras al repositorio de Control Avanzado
No reemplaces su workflow de Pages por este: un repositorio tiene un sitio principal. Copia `docs/game/` al directorio fuente de ese sitio e incorpora las páginas del reporte a su navegación. Ajusta el iframe mediante `relative_url` y conserva el workflow ya existente. El ZIP es autónomo para un repositorio nuevo; esta integración requiere conocer la estructura concreta del repo anterior.

### Verificación local del motor

```bash
python -m unittest discover -s tests -v
python docs/game/core.py --episodes 1000 --mode practice --output training.json
```

El entrenamiento por consola no abre una ventana; produce resultados JSON. `run_local.py` abre el reporte y su interfaz web.
