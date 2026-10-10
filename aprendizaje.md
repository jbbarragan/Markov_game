---
layout: default
title: Aprendizaje en Python
nav_order: 3
---
# Aprendizaje por refuerzo

### De una cadena de Markov a una política
Una cadena de Markov describe transiciones; un MDP añade acciones y recompensas. Al fijar una política π se induce una dinámica de Markov sobre un estado suficiente. Aquí se utiliza **Q-learning**, aprendizaje por refuerzo sin modelo: el agente desconoce las probabilidades de transición y aprende valores de acción con las recompensas observadas. No se calcula una ruta óptima mediante una regla preprogramada de regreso a la base.

### Representación del agente
La clave tabular es (x, y, ⌊E/10⌋ limitado a 9, Δx_lata, Δy_lata, color_lata, bloque_de_turnos_restantes). La lata objetivo es la más cercana según distancia Manhattan, con desempate lexicográfico; esto es extracción de características, no una orden de movimiento. Incluir posición absoluta permite distinguir la base y las fronteras. La carga se divide en diez intervalos y el tiempo en bloques de diez turnos.

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
- **Nueva partida manual:** recupera las flechas; conserva Q en la misma modalidad. Cambiar modalidad reinicia el agente para no mezclar recompensas distintas.
- **Exportar datos JSON:** contiene el registro por turno de la partida visible, todos los resúmenes entrenados y la tabla Q. No se persiste automáticamente Q al cerrar; sí se conserva la bitácora manual cuando el navegador lo permite.

### Qué observar
Comparar los primeros episodios con los últimos mediante medias por ventanas, no mediante una sola partida. Usar semillas nuevas para evaluar generalización y repetir el entrenamiento con varias semillas. Medir puntaje, G₀, latas y rescates. El programa no promete que 500 episodios basten; su espacio agregado sigue siendo grande.

En Práctica, la recompensa por esperar favorece una política conservadora. En Extendida se anula ese premio y se cobra energía por tiempo: esta modificación cambia el objetivo y evita que esperar sea una fuente gratuita de puntos, pero no garantiza que el agente aprenda una buena política de retorno.

### Archivos principales

| Archivo | Responsabilidad |
|:--|:--|
| `docs/game/core.py` | Entorno, RNG, transiciones, Q-learning y entrenamiento CLI |
| `docs/game/worker.js` | Carga Pyodide y comunica Python con JavaScript |
| `docs/game/game.js` | Sprites Canvas, teclado, reloj, gráficas, evidencia |
| `docs/game/game.css` | Presentación adaptable y estilo del laboratorio |
| `tests/test_core.py` | Reglas, fronteras, rescates y actualización terminal |

Para entrenar sin navegador ni bibliotecas externas:

```bash
python docs/game/core.py --episodes 1000 --mode practice --output training.json
```

Este comando genera datos de entrenamiento; la interfaz gráfica se abre con `python run_local.py`. Pyodide 0.27.2 se descarga desde jsDelivr y requiere conexión. GitHub Pages entrega archivos estáticos; no se intenta ejecutar un servidor Python remoto.
