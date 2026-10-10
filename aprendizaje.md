---
layout: default
title: Aprendizaje en Python
nav_order: 3
---
# Aprendizaje por refuerzo

### De una cadena de Markov a una política
Una cadena de Markov describe transiciones; un MDP añade acciones y recompensas. Al fijar una política π se induce una dinámica de Markov sobre un estado suficiente. Aquí se utiliza **Q-learning**, aprendizaje por refuerzo sin modelo: el agente desconoce las probabilidades de transición y aprende valores de acción con las recompensas observadas. No se calcula una ruta óptima mediante una regla preprogramada de regreso a la base.

### Representación del agente
La clave tabular es (x, y, ⌊A/4⌋ limitado a 11, Δx_lata, Δy_lata, color_lata, bloque_de_turnos_restantes), donde A = E/ρ es la **autonomía**: segundos de batería restantes a la tasa de desgaste vigente. Así una misma entrada reúne carga y desgaste. La lata objetivo es la más cercana según distancia Manhattan, con desempate lexicográfico; esto es extracción de características, no una orden de movimiento. Incluir posición absoluta permite distinguir la base y las fronteras. La autonomía se divide en doce intervalos de 4 s y el tiempo en bloques de diez turnos.

Esta agregación omite las demás latas y agrupa distintas cargas y tiempos; puede asociar situaciones diferentes a una misma entrada Q. Es una aproximación del estado, con aliasing y sin garantía de convergencia al óptimo del modelo completo. Una codificación exacta del mapa completo aumentaría drásticamente el número de estados y reduciría la repetición útil de experiencias.

### Actualización

```text
Q(s,a) ← Q(s,a) + η [r + γ maxₐ' Q(s',a') − Q(s,a)]
η = 0.15; γ = 0.95; Q inicial = 0
En el turno terminal: objetivo = r (sin bootstrap).
ε(k) = max(0.05, 0.995ᵏ), k = episodios completos entrenados.
```

Con probabilidad ε se explora una acción válida uniforme; en otro caso se elige el mayor valor Q, desempatando al azar. La acción recargar se enmascara fuera de la base. El agente recibe los resultados numéricos del entorno: no se carga una tabla de premios dentro de la política.

### Controles experimentales

- **Aprender desde cero:** borra Q, métricas y episodios; inicia en base con 100% y empieza a explorar.
- **Entrenar +500 episodios:** acelera el mismo entorno en bloques pequeños dentro del worker. Continúa la Q actual, no la reinicia. Pausar detiene al terminar el bloque actual.
- **Evaluar sin explorar:** ε efectiva 0, no actualiza Q ni contadores de entrenamiento. Se detiene al terminar 100 turnos. Los empates siguen siendo aleatorios.
- **Desgaste de batería:** aleatorio por partida, constante (1, 2, 4, 6 o 9 %/s) o intercalado. El agente entrenado con *aleatorio* ve todos los perfiles.
- **Nueva partida manual:** recupera las flechas, avanza la semilla en uno (nueva distribución de latas y, en modo aleatorio, otro desgaste) y conserva Q en la misma modalidad. Cambiar modalidad reinicia el agente para no mezclar recompensas distintas.
- **Descargas del agente** (solo visibles cuando Python controla el robot):
  - **Telemetría (CSV):** una fila por paso con episodio, fase (entrenamiento o evaluación), acción, si fue exploración, ε, posición, energía, tasa de desgaste, descarga, ángulo, recompensa y su tipo, puntaje, retorno, error TD y Q previa. Se conservan los pasos más recientes (unos 400 episodios).
  - **Balance de recompensas (CSV):** una fila por episodio con puntaje, retorno, latas, rescates, desgaste medio y la recompensa separada en latas, movimiento, espera, rescates y recarga, con el número de eventos de cada tipo. Incluye todos los episodios de entrenamiento y de evaluación.
  - **Q y parámetros (JSON):** tabla Q, resúmenes de entrenamiento y evaluación y parámetros. Q no se persiste al cerrar la pestaña.

### Qué observar
Comparar los primeros episodios con los últimos mediante medias por ventanas, no mediante una sola partida. Usar semillas nuevas para evaluar generalización y repetir el entrenamiento con varias semillas. Medir puntaje, G₀, latas y rescates. El programa no promete que 500 episodios basten; su espacio agregado sigue siendo grande.

En Práctica, la recompensa por esperar favorece una política conservadora. En Extendida se anula ese premio: esta modificación cambia el objetivo y evita que esperar sea una fuente gratuita de puntos, pero no garantiza que el agente aprenda una buena política de retorno. En ambas modalidades esperar también gasta batería, de modo que esperar sin recargar acaba en rescate.

### Archivos principales

| Archivo | Responsabilidad |
|:--|:--|
| `docs/game/core.py` | Entorno, RNG, transiciones, Q-learning y entrenamiento CLI |
| `docs/game/worker.js` | Carga Pyodide y comunica Python con JavaScript |
| `docs/game/game.js` | Sprites Canvas, teclado, reloj, gráficas de píxeles, descargas |
| `docs/game/game.css` | Presentación adaptable y estilo de 16 bits |
| `docs/game/fonts/` | Press Start 2P y VT323 (licencia SIL OFL), servidas localmente |
| `tests/test_core.py` | Reglas, fronteras, rescates y actualización terminal |

Para entrenar sin navegador ni bibliotecas externas:

```bash
python docs/game/core.py --episodes 1000 --mode practice --drain random --output training.json --telemetry-csv telemetria.csv --balance-csv balance.csv
```

Este comando genera datos de entrenamiento y, opcionalmente, los mismos CSV que descarga la interfaz; la interfaz gráfica se abre con `python run_local.py`. Pyodide 0.27.2 se descarga desde jsDelivr y requiere conexión. GitHub Pages entrega archivos estáticos; no se intenta ejecutar un servidor Python remoto.

Cada decisión del agente dura 0.2 segundos simulados. Cambiar la velocidad solo acelera la visualización; no cambia el consumo por segundo simulado.
