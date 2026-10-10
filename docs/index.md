---
layout: default
title: Reporte de la práctica
nav_order: 1
---
<div class="cf-kicker">IBERO CDMX / APRENDIZAJE REFORZADO / PRÁCTICA 05</div>

# Can Finder 5000
## Un robot, cien decisiones y una batería finita

**Joshua Abdiel Barragán Guardado**  
Ingeniería Mecatrónica y Sistemas Ciberfísicos · Universidad Iberoamericana Ciudad de México  
Docentes: Dr. Alexandro López González y Mtro. Julio A. Caballero Mora

<div class="cf-hero"><span class="cf-kicker">SIMULACIÓN INTERACTIVA DE UN MDP</span><h2>Reciclar bajo incertidumbre.</h2><p>Un pequeño robot de orugas explora un mundo de 10 × 10 celdas. Cada desplazamiento puede cambiar de dirección, cada búsqueda consume energía y cada decisión tiene una recompensa.</p><div class="cf-tags">16 BITS &nbsp; / &nbsp; PYTHON + JAVASCRIPT &nbsp; / &nbsp; Q-LEARNING</div></div>

[Abrir el laboratorio]({{ '/laboratorio/' | relative_url }}){: .btn .btn-primary }
[Consultar el modelo]({{ '/modelo/' | relative_url }}){: .btn }

### Resumen
Se implementa un entorno de recolección basado en procesos de decisión de Markov. El jugador controla un robot mediante el teclado y observa transiciones estocásticas de movimiento y energía. El sistema mide recompensa acumulada, retorno descontado, recolecciones y rescates durante episodios de 100 turnos. Como extensión, se incorpora un agente de Q-learning escrito en Python, inicializado sin experiencia, y una modalidad con recompensas por color y descarga dependiente del tiempo.

El sitio presenta el reporte y permite experimentar dentro de la misma página. Python ejecuta el entorno y el agente en un trabajador del navegador mediante Pyodide; JavaScript dibuja el tablero, captura los controles y muestra las métricas. La separación permite reutilizar el mismo entorno en experimentos fuera del navegador.

### 1. Objetivo
Experimentar el compromiso entre recolectar recompensas, preservar energía y evitar rescates; identificar estados, acciones, recompensas y transiciones; observar la diferencia entre una política humana y una política que aprende de su interacción.

### 2. Alcance y modalidades

| Característica | Práctica | Extendida |
|:--|:--|:--|
| Tablero / base / horizonte | 10 × 10 / (0,0) / 100 turnos | Iguales |
| Latas iniciales | 12 | 12 |
| Reposición tras recolectar | Inmediata, mantiene 12 | Inmediata |
| Aparición adicional | No | Probabilidad 1−exp(−Δt/8), máximo 20 |
| Premio por lata | +1 en todos los colores | Verde +1, azul +2, rosa +4 |
| Casilla vacía / rescate | −0.05 / −3 | Iguales |
| Esperar | +0.10, sin consumo | 0, con descarga temporal |
| Descarga temporal | Solo por desplazamiento | Gaussiana de movimiento + 0.5% por segundo activo |
| Avance manual | Una tecla válida, un turno | Un turno por segundo activo |
| Recarga | R sobre la base: 100% | Igual |

La modalidad Práctica conserva las reglas evaluables. La modalidad Extendida satisface el diseño adicional del videojuego y debe analizarse por separado. El PDF propone Python o MATLAB: aquí la lógica completa es Python y la interfaz web es una adaptación de presentación, no una implementación en Pygame/Tkinter. Se incluye además ejecución de entrenamiento con Python estándar.

### 3. Diseño del sistema
El mapa usa sprites originales dibujados por código: robot amarillo con orugas y ojos binoculares inspirado en WALL·E, latas de tres colores, estación cian y terreno cuadriculado. El lenguaje visual evoca videojuegos de 16 bits, con píxeles nítidos y paleta limitada; no requiere imágenes externas.

El panel derecho muestra energía, SH/SL, ΔE, ángulo de derrape, curva gaussiana, probabilidades condicionadas a la carga, turno, latas, rescates, puntaje y G₀. El agotamiento presenta una alerta con zZz y X roja durante aproximadamente 850 ms, antes de mostrar el robot de nuevo en la base.

### 4. Resultados y estado de la evidencia
Este reporte describe una implementación y un protocolo reproducible. **No se presentan partidas humanas ni mejoras del agente como resultados ya observados.** La bitácora registra tus partidas completas, captura su tablero y telemetría, y admite las dos reflexiones solicitadas. El entrenamiento produce una curva real en cada ejecución y permite descargar sus métricas y tabla Q.

Una recompensa positiva por esperar puede favorecer la inactividad; por tanto, aprender no implica necesariamente recolectar más. Deben compararse puntaje, retorno, latas y rescates conjuntamente. El aprendizaje tabular con estado agregado tampoco garantiza convergencia a la política óptima del entorno completo.

### 5. Conclusión de diseño
La simulación vuelve visibles los componentes de una decisión secuencial bajo incertidumbre. Regresar a la base tiene un costo y también un riesgo: con batería baja el consumo aumenta y el derrape dificulta alcanzar la estación. La extensión de aprendizaje permite investigar cómo esas reglas producen estrategias, incluyendo comportamientos poco intuitivos como esperar. La conclusión experimental final se completa después de las tres partidas reales.

### Referencias
1. López González, A. y Caballero Mora, J. A. *Práctica: El Juego del “Can Finder 5000” en un Gridworld Estocástico*. Material de clase proporcionado, 5 páginas.
2. [Pyodide: uso de Python en el navegador](https://pyodide.org/en/0.27.2/usage/index.html). Versión fijada: 0.27.2.
3. [Just the Docs](https://just-the-docs.com/). Tema de documentación para Jekyll.
4. [GitHub Pages: publicación mediante GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
