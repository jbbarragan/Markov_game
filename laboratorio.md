---
layout: default
title: Laboratorio interactivo
nav_order: 4
---
# Laboratorio interactivo

Elige **Práctica** para las tres partidas evaluables. Haz clic en el tablero y usa las flechas, Espacio y R. Las acciones manuales quedan bloqueadas cuando Python controla el robot. En pantallas pequeñas puedes usar los botones táctiles.

[Abrir juego en una pestaña]({{ '/game/index.html' | relative_url }}){: .btn .btn-primary target="_blank" }

El botón **Pantalla completa** está dentro del juego. Al volver al reporte se conserva la sesión mientras no se recargue la página. La primera carga de Python puede tardar y requiere internet.

<iframe class="cf-game" src="{{ '/game/index.html' | relative_url }}" title="Can Finder 5000, simulador MDP y aprendizaje en Python" allow="fullscreen" allowfullscreen loading="eager"></iframe>

### Lectura de las métricas
La batería se descarga con el tiempo a una tasa de 1, 2, 4, 6 o 9 % por segundo, constante o intercalada; el selector **Desgaste de batería** fija el perfil o lo sortea por partida. La gráfica de batería contra tiempo muestra cómo baja y el umbral SH/SL del 40%. α(E) y β(E) dependen de la tasa vigente. La línea vertical roja en la curva gaussiana marca el último ángulo; las líneas de umbral están en ±30°. Debajo del tablero, el balance de recompensas separa lo ganado o perdido por latas, movimiento, espera y rescates.

Cuando Python controla el robot (aprender o evaluar) aparece la sección **Datos del agente** con la descarga de telemetría, balance de recompensas y tabla Q. En modo manual no hay bitácora ni descargas; el botón **Capturar pantalla** guarda una imagen del tablero con su telemetría.
