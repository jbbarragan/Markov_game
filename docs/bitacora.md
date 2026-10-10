---
layout: default
title: Bitácora y evaluación
nav_order: 5
---
# Bitácora de tres partidas

**Pendiente de ejecución por el jugador.** No se sustituyen tus observaciones por recorridos automáticos. El laboratorio registra las partidas completas y guarda capturas del tablero con telemetría. Los resúmenes y logs se descargan como JSON; las imágenes se descargan como PNG.

### Procedimiento
1. Selecciona **Práctica**, elige una semilla y pulsa Nueva partida manual.
2. Juega hasta el turno 100. No reinicies a mitad del episodio.
3. Repite hasta reunir tres partidas (por ejemplo, semillas 42, 43 y 44).
4. Descarga las tres capturas automáticas y la bitácora completa.
5. Contesta las dos preguntas dentro del juego usando lo que realmente ocurrió.
6. Completa la tabla de abajo y publica las capturas junto con tu conclusión en este archivo del repositorio.

| Partida | Semilla | Puntaje | G₀ | Latas | Rescates | Evidencia |
|:--|:--|--:|--:|--:|--:|:--|
| 1 | Pendiente | — | — | — | — | Pendiente |
| 2 | Pendiente | — | — | — | — | Pendiente |
| 3 | Pendiente | — | — | — | — | Pendiente |

### Reflexión solicitada
**¿Cuál fue tu política humana π(s) cuando el robot entraba en batería baja lejos de la base?**  
Pendiente de la experiencia del jugador. Conviene señalar posición, energía, distancia a la base y decisión concreta. No basta con indicar “regresar”: el derrape puede impedirlo y el presupuesto de energía suele ser menor que esa distancia.

**¿En qué situaciones preferiste esperar en vez de arriesgarte a buscar una lata o regresar?**  
Pendiente de la experiencia del jugador. Relaciona el +0.10 seguro con el riesgo de −3, el horizonte restante y la recompensa de una lata.

### Criterios de análisis
La distancia Manhattan d = x+y es un mínimo de movimientos para volver sin derrapes. No es una garantía de supervivencia. El consumo promedio alto de 10 por paso y bajo de 16 por paso hace difícil alcanzar latas concentradas en (6,6) y regresar: identifica esa tensión como parte del diseño, sin reducir el gasto a escondidas. Compara el desempeño humano con la referencia analítica de esperar y, después, con evaluaciones de un agente entrenado.

### Trazabilidad con la práctica

| Requisito | Implementación / evidencia |
|:--|:--|
| Cuadrícula 10 × 10 y base (0,0) | `World`, Canvas |
| 12 latas y normal bivariada | `World.spawn`, reposición inmediata |
| SH/SL y energía continua | `World.energy`, umbral 40 |
| Flechas / Espacio / R | Controles del laboratorio |
| Consumo N(10,4²), N(16,6²) | `World.step`, recorte negativo declarado |
| Derrape y colisión | `World.step`, σθ=25° documentada |
| Recompensas de la tabla | Modo Práctica |
| Rescate −3 y regreso al inicio | Motor y alerta zZz/X roja |
| 100 turnos y γ=0.95 | Motor, panel y exportación |
| Tablero izquierdo / telemetría derecha | Interfaz adaptable |
| Entorno separado de GUI | Python independiente y JavaScript visual |
| Código Python ejecutable | `core.py`, CLI y Pyodide |
| 3 partidas, capturas y reflexión | Registro implementado; ejecución humana pendiente |
| Extensión solicitada de aprendizaje | Q-learning sin experiencia inicial |
| Página con reporte y juego ampliable | Just the Docs, iframe y Fullscreen API |
