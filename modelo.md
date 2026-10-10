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
ρ(τ) ∈ {1, 2, 4, 6, 9} %/s       tasa de desgaste en el segundo τ
ΔE = ∫ ρ(τ) dτ  sobre el intervalo activo
E' = E − ΔE
α(E) = 1 si E − ∫[τ,τ+1]ρ(u)du > 40; 0 en otro caso
β(E) = 1 si E − ∫[τ,τ+1]ρ(u)du > 0; 0 en otro caso
```

La descarga es exactamente lineal para tasa constante y lineal por tramos para el perfil intercalado. La tasa puede ser 1, 2, 4, 6 o 9 %/s. En el perfil intercalado cambia cada 6–15 segundos; el perfil aleatorio se sortea con la semilla por partida. No hay ruido adicional asociado a pulsar teclas. α y β son indicadores condicionados al perfil programado; el derrape sigue siendo aleatorio.

En control manual, ambos modos usan un reloj de tiempo activo independiente del teclado. Moverse es inmediato y no añade un consumo fijo; quedarse inmóvil también descarga la batería. Los pulsos de reloj no cuentan como turnos ni dan puntos por esperar. Espacio sí cuenta como una acción de espera. Pausar, ocultar la pestaña y la animación de rescate detienen el reloj.

En aprendizaje y evaluación, cada decisión representa 0.2 s simulados, es decir 5 decisiones por segundo. Las velocidades de reproducción y el entrenamiento acelerado no alteran ese intervalo. El horizonte sigue siendo 100 decisiones (20 s simulados). La autonomía desde 100% es 100, 50, 25, 16.7 u 11.1 segundos para tasas constantes de 1, 2, 4, 6 o 9 %/s.

Al agotarse, se aplica −3, se vuelve a (0,0) y se restablece 100%. Recargar en la base restablece 100%, consume un turno y no da puntos. El modo manual no conserva un historial de acciones; el agente sí registra telemetría y balances exportables.

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

Se cuentan exactamente 100 recompensas. La etiqueta G₀ indica el retorno descontado acumulado desde el inicio, no el retorno futuro de un estado intermedio. Esperar 100 turnos *sin agotar la batería* (solo posible si se recarga en la base a tiempo) produciría puntaje 10 y G₀ = 0.1(1−0.95¹⁰⁰)/(1−0.95) ≈ 1.98816; con el desgaste por tiempo, esperar sin recargar puede terminar en rescates según la tasa y la duración. Es una referencia analítica, **no una partida humana registrada ni una prueba de optimalidad**.
