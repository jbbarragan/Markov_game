> **Corrección de publicación:** consulta `LEEME_CORRECCION.md`. Primero activa GitHub Actions en Settings → Pages.

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

- Práctica: exactamente 12 latas, todas +1, esperar +0.10, rescate −3.
- Extendida: colores +1/+2/+4, latas temporales hasta 20. Movimiento inmediato y batería por tiempo activo.
- Batería: se descarga con el tiempo, no por movimiento. Perfil por partida: aleatorio, constante (1, 2, 4, 6 o 9 %/s) o intercalado. Esperar también gasta; recargar es instantáneo.
- Aprender desde cero: borra Q y comienza exploración con Python.
- Entrenar +500: conserva Q, acelera aprendizaje; Pausar lo detiene al acabar el bloque actual.
- Evaluar: sin exploración ni actualizaciones; termina a los 100 turnos.
- Capturar pantalla: PNG del tablero con su telemetría. Ya no hay bitácora interna; la guía exige tres partidas reales, pendientes de que las juegues.
- Datos del agente (solo cuando Python controla el robot): telemetría paso a paso (CSV), balance de recompensas por episodio (CSV) y Q con parámetros (JSON).

## Código

`docs/game/core.py` es el único motor, compartido por la web y el entrenamiento CLI. Usa Python estándar. `worker.js` carga ese archivo con Pyodide en un worker; `game.js` solo controla interfaz, reloj y dibujo. Se incluyen todas las fuentes del reporte.

```bash
python -m unittest discover -s tests -v
python docs/game/core.py --episodes 1000 --mode practice --drain random --output training.json --telemetry-csv telemetria.csv --balance-csv balance.csv
```

## Convenciones y límites

- Sigma angular = 25°, coherente con ≈77% de aciertos del PDF; su notación de varianza es ambigua.
- Consumo = integral de tasa(t) durante el tiempo activo, independiente del número de movimientos. Latas gaussianas redondeadas y rechazadas fuera de tablero/celdas libres.
- El estado visible de 200 combinaciones no es Markov suficiente: el motor conserva E y el mapa. Q-learning usa agregación de estado; no hay garantía de optimalidad.
- Esperar puede ser atractivo en Práctica; no se altera esa recompensa para forzar al agente a recoger (pero esperar sin recargar acaba en rescate).
- Recompensas no se precargan en Q. El agente conoce sus observaciones y acciones válidas, y aprende de los premios del entorno.
- No hay backend remoto ni envío de datos. Q vive en memoria de la pestaña; se puede exportar, no importar en esta versión. Las fuentes de píxeles (OFL) viajan en `docs/game/fonts/`.
- La interfaz gráfica requiere HTTP/HTTPS y descarga de Pyodide. Entrenar por consola puede hacerse offline.
- No se afirma publicación en GitHub ni se incluyen resultados humanos ficticios.

Consulta `VERIFICACION.md` para el alcance de las pruebas entregadas.

## Actualización 16 bits v4

- Reporte, menús, paneles y gráficas con fuentes locales y estética de píxeles.
- Batería por reloj independiente del teclado en ambos modos; mantener las flechas permite moverse continuamente.
- Perfiles 1, 2, 4, 6, 9 %/s o intercalado; pausa/pestaña oculta detienen el reloj.
- Agente: 0.2 s simulados por decisión, con CSV de telemetría y balance por episodio completo, y JSON de Q.
- Sin página ni registro de bitácora manual. La telemetría del agente conserva hasta 40000 pasos recientes; los balances incluyen todos los episodios completos.

Extrae este ZIP en una carpeta nueva y ejecuta `python run_local.py`. Si actualizas una carpeta anterior, elimina `docs/bitacora.md` y refresca el navegador con Ctrl+F5.
