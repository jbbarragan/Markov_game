---
layout: default
title: Informe técnico
nav_order: 1
---
<div class="report-label">UNIVERSIDAD IBEROAMERICANA CIUDAD DE MÉXICO · APRENDIZAJE REFORZADO</div>

# Simulación del robot Can Finder 5000 en un entorno estocástico

**Joshua Abdiel Barragán Guardado**

Ingeniería Mecatrónica y Sistemas Ciberfísicos

Práctica 5 · Procesos de decisión de Markov

Docentes: Dr. Alexandro López González y Mtro. Julio A. Caballero Mora

### Resumen
Se presenta un simulador de recolección en una cuadrícula de 10 × 10 celdas con recursos energéticos limitados. El jugador selecciona acciones de desplazamiento, espera y recarga, mientras el sistema representa la posición, la energía disponible, las recompensas y las perturbaciones del movimiento. El informe fundamenta los elementos de la interfaz exigidos en la sección 6.2 de la guía [1] y explica su relación con el modelo de transición. La implementación separa el entorno, escrito en Python, de la representación gráfica. La descarga se adapta a una función del tiempo activo, de acuerdo con la modificación solicitada para el juego. Se conservan el horizonte de 100 decisiones, los umbrales de batería y la tabla de recompensas de la modalidad base.

**Palabras clave:** proceso de decisión de Markov; simulación; incertidumbre; telemetría; gestión energética.

### 1. Objetivo y alcance
El objetivo es representar de forma interpretable una decisión secuencial bajo incertidumbre: el robot debe obtener recompensas sin perder la energía necesaria para regresar a la estación. La representación gráfica no se limita a ilustrar una trayectoria; permite observar qué acción se solicitó, qué transición ocurrió y qué consecuencia produjo.

El alcance principal de este informe corresponde al tablero y al panel de telemetría exigidos por la guía [1, pp. 2–4]. La extensión de aprendizaje por refuerzo se describe por separado, para distinguir la política humana de una política aprendida. No se incluyen formularios, registros ni una sección de bitácora del jugador. Tampoco se presentan observaciones humanas o mejoras del agente que no hayan sido medidas.

### 2. Correspondencia con los requisitos visuales

| Requisito de la guía [1, p. 4] | Implementación | Finalidad de la representación |
|:--|:--|:--|
| Tablero izquierdo de 10 × 10 | Cuadrícula indexada de 0 a 9 en cada eje | Ubicar al robot y delimitar las acciones admisibles |
| Estación en la esquina inicial | Celda cian rotulada BASE en (0,0) | Identificar el único punto de recarga voluntaria |
| Latas distribuidas en el mapa | Doce latas iniciales; reposición al recolectar | Representar las oportunidades de recompensa |
| Indicador verde o rojo del robot | Luz del robot y segmentos de batería según SH/SL | Hacer visible el cambio de régimen energético |
| Alerta de rescate | Robot apagado, zZz, X roja y penalización −3 | Mostrar el evento antes de regresar a la base |
| Medidor y estado de batería | Porcentaje numérico, barra segmentada y etiqueta SH/SL | Distinguir carga continua y clasificación discreta |
| Descarga y derrape de la transición | ΔE, θ, curva gaussiana y aviso de desvío | Relacionar incertidumbre, acción y resultado |
| Marcador de desempeño | Turno, latas, rescates, puntaje y retorno descontado | Evaluar consecuencias inmediatas y acumuladas |

Todos los componentes del laboratorio usan una paleta limitada, fuentes locales de píxeles y trazos discretos sin interpolación. El informe emplea tipografía y composición académicas para facilitar la lectura de la fundamentación.

### 3. Adaptaciones respecto del enunciado
La guía prescribe una descarga gaussiana por movimiento y ausencia de consumo al esperar [1, pp. 2–3]. Esta versión utiliza descarga por tiempo activo, incluso cuando el robot permanece inmóvil después de iniciar la partida. Por tanto, constituye una **adaptación energética explícita** y no una reproducción literal de esas dos reglas. La modalidad «Práctica adaptada» conserva las recompensas originales, pero no debe confundirse con el modelo energético original.

La tasa inicial es 1 punto porcentual por segundo: una carga completa dura aproximadamente 100 segundos sin recarga. La alternativa de 0.5 %/s permite 200 segundos; las tasas 2, 4, 6 y 9 %/s se seleccionan como mayores niveles de dificultad. También pueden elegirse perfiles aleatorios por partida o intercalados. El reloj manual comienza con la primera acción; carga de la página, pausa, pestaña oculta y animación de rescate no descuentan batería.

El derrape gaussiano permanece activado inicialmente. Puede desactivarse para comprobar el control direccional; esa opción produce una dinámica determinista de movimiento y se identifica en el panel. El modo Extendida añade premios por color y apariciones temporales de latas; sus resultados se analizan por separado.

### 4. Criterios de interpretación
El puntaje acumulado mide el saldo de recompensas. El retorno descontado asigna menor peso a consecuencias lejanas en número de decisiones. El número de latas cuantifica la tarea de recolección, mientras los rescates reflejan agotamientos. Ninguna métrica aislada demuestra una política adecuada: la recompensa positiva por esperar puede elevar el puntaje sin aumentar la recolección.

Las comprobaciones de funcionamiento no sustituyen un experimento comparativo. Para afirmar que una política mejora deben fijarse modalidad, perfil energético, derrape y semillas de evaluación; después deben contrastarse latas, rescates y recompensas sobre el mismo conjunto de condiciones.

### 5. Conclusión
La organización del tablero y de la telemetría permite vincular posición, acción, perturbación y recompensa en una misma transición. La separación entre reloj y entradas de teclado evita que pulsar más rápido implique un gasto energético artificial. La distinción entre SH y SL facilita la lectura visual, aunque no contiene por sí sola toda la información del entorno. La interpretación de los resultados exige considerar la energía continua, el mapa de latas y las adaptaciones declaradas.

### Referencias
[1] A. López González y J. A. Caballero Mora, «Práctica: El Juego del “Can Finder 5000” en un Gridworld Estocástico», material de la asignatura Aprendizaje Reforzado, Universidad Iberoamericana, pp. 1–5, documento proporcionado por el usuario.

[2] R. S. Sutton y A. G. Barto, [Reinforcement Learning: An Introduction, segunda edición](https://mitpress.mit.edu/9780262039246/reinforcement-learning/), MIT Press, 2018. Referencia conceptual complementaria.

[3] C. J. C. H. Watkins y P. Dayan, [«Q-learning»](https://www.gatsby.ucl.ac.uk/~dayan/papers/wd92.html), Machine Learning, vol. 8, pp. 279–292, 1992. DOI: 10.1007/BF00992698.
