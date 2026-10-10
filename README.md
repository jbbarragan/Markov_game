# Can Finder 5000 — Práctica 5

Reporte Just the Docs + juego Canvas de estética 16 bits + motor y Q-learning en Python.

## Probar

```bash
python run_local.py
```

Abre `http://127.0.0.1:8000/reporte-local.html`. Internet necesario para Pyodide 0.27.2. No abrir con `file://`.

## Publicar

Sube el **contenido** de esta carpeta a la raíz de un repositorio nuevo. Incluye `.github/workflows/pages.yml`. En Settings → Pages selecciona **GitHub Actions**. Publicar en `main` inicia la construcción. El workflow calcula la ruta base del repo automáticamente. Si ya tienes un sitio en otro repositorio, no sobrescribas su workflow: revisa `docs/instalacion.md`.

## Jugar

Haz clic en el tablero. Flechas: mover; Espacio: esperar; R: recargar en (0,0). También hay botones táctiles. 100 turnos. Pantalla completa desde el botón superior.

- Práctica: exactamente 12 latas, todas +1, esperar +0.10 sin gasto, rescate −3.
- Extendida: colores +1/+2/+4, latas temporales hasta 20, descarga adicional 0.5%/segundo simulado. Un turno por segundo activo. Las teclas eligen la siguiente acción.
- Aprender desde cero: borra Q y comienza exploración con Python.
- Entrenar +500: conserva Q, acelera aprendizaje; Pausar lo detiene al acabar el bloque actual.
- Evaluar: sin exploración ni actualizaciones; termina a los 100 turnos.
- Bitácora: conserva últimas 12 partidas manuales, capturas y reflexiones localmente; descarga JSON y PNG. La guía exige tres partidas reales, pendientes de que las juegues.

## Código

`docs/game/core.py` es el único motor, compartido por la web y el entrenamiento CLI. Usa Python estándar. `worker.js` carga ese archivo con Pyodide en un worker; `game.js` solo controla interfaz, reloj y dibujo. Se incluyen todas las fuentes del reporte.

```bash
python -m unittest discover -s tests -v
python docs/game/core.py --episodes 1000 --mode practice --output training.json
```

## Convenciones y límites

- Sigma angular = 25°, coherente con ≈77% de aciertos del PDF; su notación de varianza es ambigua.
- Consumo gaussiano recortado en cero. Latas gaussianas redondeadas y rechazadas fuera de tablero/celdas libres.
- El estado visible de 200 combinaciones no es Markov suficiente: el motor conserva E y el mapa. Q-learning usa agregación de estado; no hay garantía de optimalidad.
- Esperar puede ser atractivo en Práctica; no se altera esa recompensa para forzar al agente a recoger.
- Recompensas no se precargan en Q. El agente conoce sus observaciones y acciones válidas, y aprende de los premios del entorno.
- No hay backend remoto ni envío de datos. Q vive en memoria de la pestaña; se puede exportar, no importar en esta versión. La bitácora depende del almacenamiento del navegador.
- La interfaz gráfica requiere HTTP/HTTPS y descarga de Pyodide. Entrenar por consola puede hacerse offline.
- No se afirma publicación en GitHub ni se incluyen resultados humanos ficticios.

Consulta `VERIFICACION.md` para el alcance de las pruebas entregadas.
