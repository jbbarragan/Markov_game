# Verificación de la entrega

- 22 pruebas automáticas del entorno y del agente: aprobadas con Python 3.12.
- Desgaste de batería: tasas constantes de 1, 2, 4, 6 y 9 %/s lineales en el tiempo; descarga idéntica al esperar o moverse; perfil intercalado por tramos (aditividad de la integral); perfil aleatorio reproducible por semilla; recarga instantánea que nunca provoca rescate; α y β según la tasa vigente.
- Balance de recompensas: la suma por tipo (latas, movimiento, espera, rescates, recarga) coincide con el puntaje, y los eventos suman 100 por episodio.
- Exportaciones: telemetría CSV (400 filas en la prueba, columnas fijas, fases de entrenamiento y evaluación) y balance CSV (una fila por episodio) generadas por el mismo código que usa la interfaz; entrenamiento por CLI con `--telemetry-csv` y `--balance-csv`.
- Interfaz comprobada en Chromium headless con el motor Python real (sin Pyodide): partida manual con desgaste 4 %/s, perfil intercalado, semilla que avanza en «Nueva partida manual», entrenamiento de +500 episodios, descargas visibles solo con Python al control, tres descargas funcionales, temas oscuro y claro, ancho de 420, 900 y 1280 px, sin errores de consola.
- Sintaxis JavaScript de interfaz verificada con `node --check`. YAML de configuración y workflow: parseado correctamente.

Límites: la comprobación visual usó un servidor local que expone el mismo `core.py`; no se descargó Pyodide dentro del navegador de prueba ni se construyó Jekyll aquí (lo hace GitHub Actions). El aprendizaje por refuerzo con esperas sigue siendo una política atractiva en Práctica; las pruebas no sustituyen las tres partidas humanas de la práctica.

## Corrección de despliegue

Ver `LEEME_CORRECCION.md`. `docs/Gemfile` y `docs/_config.yml` usan `theme: just-the-docs` como gema, sin `remote_theme`.
