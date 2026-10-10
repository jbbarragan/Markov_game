# Verificación de la versión 5.0

## Motor
- 29 pruebas automáticas Python aprobadas.
- Consumo independiente de la cantidad de movimientos, tasas constantes e intercaladas, rescate estando quieto, recarga y límites del tablero.
- Tasa inicial 1 %/s; perfil largo 0.5 %/s. Control sin derrape y conservación del perfil al entrenar comprobados.
- Evaluación sin actualización de Q; telemetría y balances de entrenamiento/evaluación verificados.

## Navegador real
Probado con Chromium headless y Playwright, con el motor Python nativo y con el motor Pyodide incluido (sin simulación de respuestas):
- Al esperar antes de la primera acción se conserva 100% y turno cero.
- Seis pulsaciones rápidas hacia la derecha, con derrape desactivado: posición (6,0) y turno 6.
- Mantener abajo aproximadamente un segundo: seis movimientos adicionales, hasta (6,6).
- A 1 %/s: 3 segundos activos consumen exactamente 3 puntos porcentuales dentro de la resolución de la interfaz.
- A 0.5 %/s con Pyodide: aproximadamente 2 segundos consumen 1 punto porcentual.
- Pausa sin gasto de batería. Teclado del juego integrado en el reporte comprobado.
- 500 episodios completos en cada motor. Descargas reales de telemetría CSV, balances CSV y Q en JSON con el motor nativo. Los 500 balances descargados tienen suma de contribuciones igual al puntaje.
- Ningún formulario de bitácora en el juego. Ruta anterior docs/game/index.html redirige a game-v5/index.html.
- Interfaz revisada a 1440 y 420 píxeles de ancho. En móvil: ancho de documento 420 px, sin desbordamiento horizontal. Capturas incluidas en comprobacion/.
- Sin errores JavaScript de página durante las pruebas funcionales. Sintaxis JavaScript también comprobada con Node.

## Reporte y alcance
Reporte local regenerado. Incluye la correspondencia con los requisitos visuales de la guía, ecuaciones energéticas y de derrape, recompensas, estados y fuentes. La descarga por tiempo y la eliminación de la bitácora son adaptaciones solicitadas, no cumplimiento literal de esas reglas del PDF.

No se ejecutó un despliegue a GitHub Pages ni se construyó Jekyll aquí. La prueba estática con Pyodide utiliza los mismos archivos que publica Pages. Las pruebas de funcionamiento no demuestran aprendizaje óptimo ni sustituyen una evaluación estadística del agente.
