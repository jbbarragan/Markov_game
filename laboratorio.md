---
layout: default
title: Laboratorio interactivo
nav_order: 4
---
# Laboratorio interactivo

**Versión 5.0.** La descarga inicial es 1 %/s y el reloj comienza con la primera acción. Flechas: desplazamiento; Espacio: esperar; R: recargar en la base. Mantener una flecha genera movimientos continuos. El selector de derrape permite comparar la dinámica gaussiana con el control direccional exacto.

[Abrir el juego en una pestaña]({{ '/game-v5/index.html' | relative_url }}){: .btn target="_blank" }

<iframe class="cf-game" src="{{ '/game-v5/index.html' | relative_url }}" title="Can Finder 5000 versión 5.0" allow="fullscreen" allowfullscreen loading="eager"></iframe>

### Lectura de la interfaz
El tablero conserva las posiciones discretas; el porcentaje muestra la energía continua. El color verde corresponde a E &gt; 40% y el rojo a E ≤ 40%. La curva de batería representa porcentaje contra segundos activos, con el umbral del 40% marcado. La curva gaussiana representa el error angular, con umbrales ±30° y marcador de la última muestra. El panel de transición distingue un derrape de una colisión con el borde.

Los contadores de turno, latas y rescates muestran magnitudes distintas. El puntaje suma las recompensas, mientras G₀ aplica el descuento γ = 0.95. El balance bajo el tablero separa las contribuciones. En modo agente, los botones de telemetría y balance descargan los datos calculados por Python. No existe una sección de bitácora del jugador.
