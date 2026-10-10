---
layout: default
title: Modelo matemático
nav_order: 2
---
# Modelo matemático

### 1. Formulación
El proceso de decisión se expresa como M = (S, A, P, r, γ), con γ = 0.95 y N = 100. El estado visible propuesto en la guía es sₜ = (xₜ, yₜ, bₜ), con x,y ∈ {0,…,9} y b ∈ {SH,SL}. Son 200 combinaciones visibles. Las acciones son norte, este, sur, oeste, esperar y recargar; recargar solo se habilita en (0,0).

**Precisión de modelado:** ese estado visible no es suficiente para un MDP exacto. Dos cargas de 41% y 99%, ambas SH, tienen diferentes probabilidades de cruzar el umbral. Además, recoger depende del mapa actual. Un estado suficiente del simulador es (x,y,E,C,t), donde C contiene posiciones y colores de todas las latas y t incorpora el horizonte. La energía continua hace que este modelo ampliado no sea estrictamente un MDP finito. La interfaz conserva los estados de la guía; el aprendizaje usa una discretización aproximada, sin afirmar equivalencia exacta.

### 2. Energía y probabilidades

```text
SH: E > 40                    SL: 0 < E ≤ 40
ΔE = max(0, Z)
Z | SH ~ N(10, 4²)            Z | SL ~ N(16, 6²)
E' = E − ΔE
α(E) = Φ((E − 40 − 10) / 4)  para E > 40
β(E) = Φ((E − 16) / 6)       para 0 < E ≤ 40
```

Φ es la CDF normal estándar. α y β dependen de E, no son constantes. El recorte max(0,Z) evita que una muestra negativa cargue la batería: introduce una masa de probabilidad en cero y se declara como convención física de implementación. Para los umbrales positivos usados arriba, las fórmulas de cruce siguen siendo válidas. En E=40 se usa el régimen bajo.

Si E'≤0, el rescate asigna recompensa −3, incrementa el contador y retorna a (0,0,100%). Se evalúa el agotamiento **antes de otorgar la recompensa de una lata**. Una colisión gasta energía aunque no cambie la posición. Esperar no gasta energía en Práctica. Recargar no avanza la posición ni otorga puntos.

En Extendida: E' = E − ΔE_movimiento − 0.5Δt. El reloj usa segundos **activos de simulación**, no tiempo de pared durante pausa, pestaña oculta, carga de Python o alerta de rescate. Cada paso dura Δt=1 s tanto en modo manual como automático y en entrenamiento acelerado. La animación puede acelerarse sin alterar el modelo. Al no elegir una acción, se ejecuta esperar. Recargar toma un turno y restablece a 100% si no hubo agotamiento previo en ese paso.

### 3. Derrape

```text
θ ~ N(0, 25²), en grados
|θ| ≤ 30       dirección solicitada
θ > 30         dirección perpendicular derecha
θ < −30        dirección perpendicular izquierda
```

Con σ=25°, P(éxito)=2Φ(1.2)−1≈0.76986 y cada desvío tiene probabilidad ≈0.11507. Se interpreta **25° como desviación estándar**, consistente con el 77% que menciona la guía. Leer literalmente su varianza como 25 grados² daría σ=5° y una probabilidad muy distinta. En el arreglo norte→este→sur→oeste, derecha suma uno e izquierda resta uno módulo cuatro. Coordenada y crece hacia abajo en pantalla.

### 4. Generación de latas
Se generan X,Y independientes con N(6,2²), equivalente a media (6,6) y covarianza diag(4,4). Se redondea a la celda más cercana y se rechaza toda muestra fuera de [0,9]², ocupada por otra lata, por el robot o por la base. La distribución final es, por tanto, una normal discretizada condicionada a celdas admisibles; no una normal continua sin modificar. Cada color tiene probabilidad 1/3.

En Práctica cada recolección repone inmediatamente la lata para mantener 12. En Extendida hay además una prueba de aparición por turno con p=1−exp(−Δt/8), limitada a una lata adicional por turno y 20 activas. Esta es una aproximación Bernoulli al evento de al menos una llegada de un proceso Poisson, no un muestreo completo del número de llegadas.

### 5. Recompensa y retorno

| Evento | r en Práctica |
|:--|--:|
| Buscar y recolectar sin agotarse | +1.00 |
| Buscar sin recolectar | −0.05 |
| Esperar | +0.10 |
| Recargar en base | 0.00 |
| Agotamiento y rescate | −3.00 |

```text
Puntaje = Σ[t=0..99] rₜ
G₀ = Σ[t=0..99] γᵗ rₜ,     γ = 0.95
```

Se cuentan exactamente 100 recompensas. La etiqueta G₀ indica el retorno descontado acumulado desde el inicio, no el retorno futuro de un estado intermedio. Permanecer esperando los 100 turnos produce puntaje 10 y G₀ = 0.1(1−0.95¹⁰⁰)/(1−0.95) ≈ 1.98816. Es una referencia analítica, **no una partida humana registrada ni una prueba de optimalidad**.
