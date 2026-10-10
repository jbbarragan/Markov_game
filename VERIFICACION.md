# Verificación de la entrega

- 14 pruebas automáticas del entorno y del agente: aprobadas con Python 3.12.
- Casos: estados iniciales y generación, esperar 100 turnos y G0 analítico, bordes, derrape, precedencia del rescate sobre recogida, recarga válida/inválida, descarga temporal, recompensas de color, reproducibilidad por semilla, probabilidades, bootstrap terminal, evaluación sin modificar Q e invariantes en 20 episodios.
- Ejecución adicional de 20 episodios mediante CLI: completada, JSON válido.
- Sintaxis JavaScript de interfaz y worker: verificada con `node --check`.
- YAML de configuración y workflow: parseado correctamente.
- Sintaxis de archivos Python: verificada.

Límites: no se ejecutó una comprobación visual en navegador, ni se descargó Pyodide dentro de un navegador, ni se construyó Jekyll en este entorno. GitHub Actions realiza la construcción al subir el repositorio. No se ha publicado el sitio ni se ha creado un repositorio de GitHub. Se requiere una comprobación final de teclado, pantalla completa y carga de Python en el navegador del usuario.

Las pruebas del software no sustituyen las tres partidas humanas de la práctica. El reporte deja esa evidencia pendiente y el juego proporciona captura y exportación para generarla.

## Corrección de despliegue

Se verificó el intento 38073801796 por la API pública de GitHub. El fallo fue `configure-pages`: sitio Pages no encontrado. Las pruebas habían pasado; Jekyll quedó omitido. Se corrigieron también las dependencias declaradas del tema. Ver `LEEME_CORRECCION.md`.
