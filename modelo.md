---
layout: default
title: Fundamentación del modelo
nav_order: 2
---
# Fundamentación matemática del simulador

### 1. Estado, acciones y propiedad de Markov
El indicador propuesto en la guía es s = (x,y,b), con x,y ∈ {0,…,9} y b ∈ {SH,SL}. Contiene 10 × 10 × 2 = 200 combinaciones visuales [1, p. 2]. Las acciones son norte, este, sur, oeste, esperar y recargar. La última solo está habilitada en (0,0).

La observación de 200 combinaciones no basta para describir exactamente la transición. Dos robots en la misma celda y con indicador SH pueden tener 41% o 99% de carga; sus riesgos son diferentes. También importa el mapa de latas. Un estado físico más completo es z = (x,y,E,C,n,τ,p), donde C representa las posiciones y colores, n el número de decisiones, τ el tiempo activo y p el perfil energético. En un perfil intercalado debe conocerse también el tramo vigente y su tiempo residual. Así se evita presentar el indicador binario como un MDP finito exacto cuando el simulador conserva variables continuas y contexto adicional.

En términos del modelo, la propiedad de Markov exige que la distribución del siguiente estado y de la recompensa dependa del estado suficiente actual y de la acción, sin requerir la historia completa. Una política determina cómo se elige esa acción. En control manual, la política la constituye la decisión del jugador.

### 2. Ubicación de las latas
La posición candidata sigue la distribución especificada en la guía [1, pp. 1–2]:

<div class="equation">Z = (X,Y)<sup>T</sup> ∼ N(μ,Σ), &nbsp; μ = (6,6)<sup>T</sup>, &nbsp; Σ = diag(4,4). <span>(1)</span></div>

Por tanto, cada coordenada tiene desviación estándar 2 y ambas son independientes antes de discretizar. Se redondean a enteros y se rechazan candidatos fuera del tablero, sobre la base, sobre el robot o sobre otra lata. El resultado es una distribución normal discretizada condicionada al conjunto de celdas admisibles. No se recortan las coordenadas al borde, porque ello concentraría artificialmente muestras en sus extremos. Cada recolección en Práctica adaptada repone una lata para mantener doce activas.

### 3. Dinámica energética por tiempo
Se distinguen el índice de decisión n y el tiempo activo τ. Pulsar una flecha avanza n; el reloj avanza τ aun sin pulsaciones. La transición energética se define mediante:

<div class="equation">ΔE = ∫<sub>τ</sub><sup>τ+Δτ</sup> ρ(u) du, &nbsp; E<sup>−</sup> = E − ΔE. <span>(2)</span></div>

Aquí ρ tiene unidades de puntos porcentuales por segundo. Para tasa constante, ΔE = ρΔτ; para un perfil intercalado, la integral suma las contribuciones de cada tramo. Esta integral es aditiva: dividir un intervalo en varios movimientos o actualizaciones no cambia el consumo total. Tal propiedad es la razón para integrar el tiempo en lugar de restar una cantidad fija por tecla.

<div class="equation">SH: E &gt; 40; &nbsp; SL: 0 &lt; E ≤ 40; &nbsp; rescate: E ≤ 0. <span>(3)</span></div>

| Tasa constante | Autonomía desde 100% | Uso en la interfaz |
|:--|:--|:--|
| 0.5 %/s | 200 s | Partida larga |
| 1 %/s | 100 s | Valor inicial |
| 2 %/s | 50 s | Descarga acelerada |
| 4 %/s | 25 s | Dificultad alta |
| 6 %/s | 16.7 s | Dificultad alta |
| 9 %/s | 11.1 s | Dificultad extrema |

Los perfiles aleatorios eligen entre 1, 2, 4, 6, 9 %/s e intercalado. El perfil intercalado cambia de tasa cada 6–15 segundos y no repite el valor anterior. Las semillas permiten reproducir el perfil. El estimador mostrado es A ≈ E/ρ(τ); para perfiles variables es una extrapolación a tasa constante, no una garantía del tiempo de supervivencia.

### 4. Probabilidades energéticas y diferencia con la guía
En el modelo original, el consumo de búsqueda sigue N(10,4²) en SH y N(16,6²) en SL [1, pp. 2–3]. Si Φ representa la distribución normal acumulada, las probabilidades condicionadas a la carga son:

<div class="equation">α(E) = Φ((E − 40 − 10)/4), &nbsp; β(E) = Φ((E − 16)/6). <span>(4)</span></div>

La primera expresa la probabilidad de permanecer por encima de 40%; la segunda, la de no alcanzar cero. No son constantes de cada estado binario: dependen del valor continuo E. En la adaptación por tiempo ya no existe ese consumo gaussiano. Condicionados al perfil programado, los indicadores mostrados para el siguiente segundo valen 1 o 0 según E − ∫ρ permanezca por encima de 40 o de 0, respectivamente. No deben interpretarse como estimaciones de incertidumbre gaussiana de la batería.

### 5. Movimiento y derrape
El simulador muestrea θ ∼ N(0,25²) grados cuando el derrape está activo. Si −30° ≤ θ ≤ 30°, se mantiene la dirección solicitada; si θ &gt; 30°, se gira 90° a la derecha; si θ &lt; −30°, 90° a la izquierda. Una salida del tablero conserva la posición y no añade gasto energético distinto del correspondiente al tiempo transcurrido.

<div class="equation">P(recto) = 2Φ(30/25) − 1 ≈ 0.7699; &nbsp; P(izquierda) = P(derecha) ≈ 0.1151. <span>(5)</span></div>

La guía contiene una inconsistencia: escribe una varianza de 25 grados², pero indica aproximadamente 77% de éxito [1, p. 3]. Interpretar literalmente esa varianza daría σ = 5° y P(recto) = 2Φ(6) − 1, prácticamente 100%. Se adopta σ = 25° para reproducir las probabilidades indicadas. La curva de telemetría muestra esa elección y los umbrales ±30°. Al desactivar el derrape, la flecha define exactamente el desplazamiento, salvo colisión.

### 6. Recompensas y orden de eventos

| Evento | Práctica adaptada | Extendida |
|:--|--:|--:|
| Recolección sin agotamiento | +1.00 | +1 / +2 / +4 según color |
| Desplazamiento sin recolección | −0.05 | −0.05 |
| Acción explícita de esperar | +0.10 | 0.00 |
| Recarga voluntaria | 0.00 | 0.00 |
| Agotamiento y rescate | −3.00 | −3.00 |

La recompensa por una lata sustituye al costo de movimiento; no se suman +1 y −0.05. Si el paso produce agotamiento, prevalece la penalización y no se acredita una lata. Después se restaura la energía a 100% y la posición a la base. Una actualización de reloj sin acción no otorga puntos de espera ni consume un turno; sí puede producir un rescate. En la base, R restablece 100% y cuenta como decisión.

<div class="equation">R<sub>total</sub> = Σ<sub>n=0</sub><sup>99</sup> r<sub>n</sub>, &nbsp; G<sub>0</sub> = Σ<sub>n=0</sub><sup>99</sup> 0.95<sup>n</sup>r<sub>n</sub>. <span>(6)</span></div>

La expresión contiene exactamente 100 recompensas de decisiones. En modo manual, un rescate entre decisiones se añade con el exponente del siguiente índice n, sin incrementar el contador de turnos. Esta convención se declara porque la descarga temporal permite eventos sin pulsación. En el agente, cada decisión representa 0.2 s y sus eventos energéticos se resuelven dentro de la transición.

### 7. Ejemplos de interpretación
A 1 %/s, diez segundos activos consumen diez puntos porcentuales, tanto si se ejecutan dos movimientos como si se ejecutan veinte. Un desplazamiento inmediato sin tiempo transcurrido no tiene un cargo energético fijo. Desde (6,6), la distancia Manhattan mínima a la base es doce celdas. A cinco decisiones por segundo, el trayecto ideal requiere 2.4 s; a 1 %/s consume 2.4 puntos. Es un límite ideal: los derrapes, las colisiones y las pausas de decisión aumentan el tiempo real necesario.

En la tabla de recompensas original, esperar cien veces sin rescate produce R = 10 y G₀ = 0.1(1 − 0.95¹⁰⁰)/(1 − 0.95) ≈ 1.9882. Este cálculo muestra por qué puntaje y cantidad de latas deben analizarse conjuntamente. No es un resultado experimental ni una afirmación de optimalidad.

Las referencias [1]–[3] se encuentran en el informe técnico.
