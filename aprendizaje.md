---
layout: default
title: Extensión de aprendizaje
nav_order: 3
---
# Extensión: agente de aprendizaje por refuerzo

### 1. Propósito
La práctica original estudia una política humana antes de introducir optimización automática [1, p. 1]. El agente constituye una extensión solicitada: utiliza el mismo entorno Python y aprende valores de acción a partir de sus transiciones. Un proceso de Markov describe la dinámica; Q-learning es el procedimiento que actualiza la política de selección a partir de recompensas. No se utiliza una red neuronal ni una trayectoria programada.

### 2. Actualización de valores
La tabla Q inicia con ceros. Para una transición (s,a,r,s′), se aplica la actualización temporal de Q-learning [3]:

<div class="equation">Q(s,a) ← Q(s,a) + η[r + γ max<sub>a′</sub>Q(s′,a′) − Q(s,a)], &nbsp; η = 0.15, γ = 0.95. <span>(7)</span></div>

En la decisión terminal se omite el término de valor futuro. La selección ε-greedy explora una acción admisible con probabilidad ε y elige un máximo estimado en los demás casos. El parámetro es ε<sub>k</sub> = max(0.05,0.995<sup>k</sup>), con k igual al número de episodios completos. Los empates se resuelven aleatoriamente. Durante evaluación, ε = 0 y Q permanece fija.

### 3. Representación y límites
El estado agregado contiene posición, autonomía discretizada en intervalos de cuatro segundos, vector hacia la lata más cercana, color de esa lata y bloque de decisiones restantes. La autonomía se limita a doce intervalos. Esta compresión reduce la tabla, pero omite parte del mapa y del perfil energético; distintos estados físicos pueden compartir la misma clave. Por ello no se afirma que el algoritmo encuentre la política óptima del simulador completo ni que quinientos episodios sean suficientes. El resultado clásico de convergencia de Q-learning tiene hipótesis de representación y muestreo [3] que no se demuestran para esta implementación.

Cada transición del agente representa 0.2 s de simulación. Un episodio de cien decisiones corresponde a veinte segundos; cambiar la velocidad de reproducción no cambia ese tiempo modelado. A 1 %/s, un episodio iniciado al 100% no necesita agotar la batería, por lo que el aprendizaje del rescate requiere evaluar también tasas más altas. Esta diferencia debe considerarse al diseñar experimentos.

### 4. Telemetría y balances
Las exportaciones aparecen cuando Python controla el robot. La telemetría CSV registra fase, episodio, acción, estado inicial y final, energía, tasa, descarga, tiempo, recompensa, exploración y error temporal. Se conservan hasta cuarenta mil transiciones recientes. El balance CSV contiene una fila por episodio completo y separa recompensas por latas, movimiento, espera, rescate y recarga. La suma de esas contribuciones debe coincidir con el puntaje del episodio. El archivo JSON conserva parámetros y tabla Q.

La gráfica presenta el puntaje de los últimos doscientos episodios de entrenamiento y una media móvil de hasta veinte episodios. La media reduce variación visual, pero no demuestra mejora estadística. Las evaluaciones no modifican Q y sus balances se identifican mediante una fase separada. Los datos manuales no se incorporan al entrenamiento ni se guardan en una bitácora.

Las referencias [1]–[3] se encuentran en el informe técnico.
