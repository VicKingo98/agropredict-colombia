# Reporte de trabajo en equipo — AgroPredict Colombia (Grupo 11)

**Integrantes:** Víctor M. Osorio · Simón Jaramillo · Javier Cañarte
**Repositorio:** https://github.com/VicKingo98/agropredict-colombia

Las contribuciones se reconstruyeron a partir del historial de commits del repositorio y de los avances reportados en el canal del equipo (corte: 24 de noviembre de 2026).

## 1. Organización del trabajo

- **Canal de coordinación:** grupo de WhatsApp para reportar avances, repartir tareas y tomar decisiones.
- **Flujo en el repositorio:** cada integrante trabaja en su copia local, publica en `main` y documenta en el mensaje del commit lo realizado. Los cambios de documentación de la Entrega 2 pasaron por *pull request* (PR #1).
- **Versionamiento:** código en GitHub, datos y modelos en DVC (Google Drive) y experimentos en un servidor MLflow compartido en AWS EC2.

> Simón aparece en el historial con dos identidades de Git (`sijaramillogo` y `Simón Jaramillo G`). En este reporte se suman como una sola persona.

## 2. Contribuciones por integrante

### Víctor M. Osorio

| Fecha | Aporte | Evidencia |
|---|---|---|
| 22–23 oct | Estructura del repositorio, inicialización de DVC, registro de la base EVA 2019–2025 y remoto en Google Drive | `Crear estructura inicial…`, `Inicializar DVC…`, `Configurar almacenamiento remoto…` |
| 23 oct | Análisis exploratorio inicial y documentación base | `Incorporar análisis exploratorio…` |
| 6–7 nov | Optimización de modelos y registro de experimentos en MLflow EC2; versionamiento del modelo con DVC | `Agregar optimizacion de modelos…`, `Optimizar modelos con rezago secuencial…` |
| 7–8 nov | Desarrollo del tablero en Dash: identidad visual, comparación histórica, predicción múltiple y departamental, exportación CSV/Excel y mapa municipal | `implementar dashboard Dash…`, `Integrar mapa municipal…` |
| 15–18 nov | Validación de rezagos, validación cruzada temporal con ventanas expansivas, búsqueda de hiperparámetros (Random Forest y XGBoost) y selección de XGBoost | `Agregar validaciones de rezagos…`, `Optimizar modelos con validacion temporal…` |
| 19 nov | Integración del modelo con rezagos t-1 y t-2 en el tablero; API REST con FastAPI (`/health`, `/predict`); contenerización de API y tablero con Docker Compose | `integrar modelo XGBoost con rezagos…`, `Integrar API FastAPI y dashboard con Docker Compose` |
| 22 nov | Pestaña *Acerca del modelo* conectada al endpoint `/modelo`: las métricas del modelo `champion` se leen desde la API | `Actualizar métricas del dashboard desde la API del modelo` |

### Simón Jaramillo

| Fecha | Aporte | Evidencia |
|---|---|---|
| 24 oct | Perfil de variables y exportación de figuras del EDA; documentación de DVC con Google Drive; prototipo de *mockup* del tablero con plantillas de carga | `EDA: perfil de variables…`, `Documentar configuración de DVC…`, `Prototipo inicial de mockup…` |
| 1–5 nov | Notebook de preprocesamiento, versionamiento de datos procesados, separación de *featuring* y modelado, configuración del entorno MLflow | `Agrega notebook de preprocesamiento…`, `Separa featuring y modelado…` |
| 7 nov | Modelado secuencial y ajustes al registro de métricas en el servidor MLflow | `Agrega modelado secuencial…`, `actualizacion notebooks ml flow server` |
| 14 nov | Construcción de variables de rezago t-1 y t-2 (`features_rezago_1_2.parquet`, versionado en DVC) y notebooks `04.1` y `05.1`; identificación de registros con rendimiento idéntico al semestre anterior | `actualizacion 03 featuring…`, `Features con rezagos t-1 y t-2…` |
| 18 nov | Base del notebook de optimización con rezagos | `comienzo de optimizacion para rezagos t-1 y t-2` |
| 21 nov | Nueva ejecución del notebook `05.1` con registro de experimentos y del modelo final en el *Model Registry* de MLflow (`agropredict-maiz-xgb`, alias `champion`, versión 1) | `Registrar experimentos y modelo XGBoost t1-t2 en MLflow EC2…` |
| 21 nov | Empaquetamiento del modelo como paquete de Python (`agropredict-model`, archivo `.whl`) con validación de entradas y pruebas con pytest y tox | `Empaquetar modelo XGBoost t1-t2 como paquete Python…` |
| 21 nov | API consumiendo el paquete, `Dockerfile.api` en dos etapas, chequeo de salud en Compose, `.dockerignore` sin credenciales y manejo de errores de la API en el tablero | `API consume el paquete agropredict-model…`, `Excluir credenciales…`, `Healthcheck en compose…` |
| 21 nov | Despliegue en AWS EC2 (instancia `agropredict-model`, t3.medium) y pruebas de la solución desplegada | Soportes 12 a 16 |
| 21–24 nov | Capturas de MLflow y del despliegue, incluidas las reglas del grupo de seguridad | Soportes 04 a 07 y 12 a 16 |
| 22–24 nov | Análisis del error de XGBoost y de la persistencia en 2025, separando registros que repiten el valor anterior de los que cambian (respuesta a la retroalimentación de la Entrega 2), registrado en MLflow | Evaluación `Analisis_errores_repetidos_vs_cambios_2025`; soporte 06c |

### Javier Cañarte

| Fecha | Aporte | Evidencia |
|---|---|---|
| 25 oct | Documentación de hallazgos del EDA sobre el rendimiento del maíz | `docs: document EDA findings for maize yield` |
| 7 nov | Guía de reproducibilidad: instalación del entorno, configuración de MLflow en EC2 y estado del proyecto; revisión e integración del PR #1 | `Agrega documentación de instalación, MLflow en EC2…`, `Merge pull request #1` |
| 21–22 nov | Validación de la reproducibilidad en un segundo equipo (Windows): instalación de Docker, construcción de las imágenes y pruebas de la API (`/health`, `/modelo`, `/predict` por lotes) y del tablero | Soportes 08 a 11 |
| 22 nov | Detección y corrección del error de finales de línea que impedía construir la API en Windows (archivo `.gitattributes`) | `Agregar .gitattributes para conservar finales de línea LF…` |
| 21–22 nov | Soportes de DVC (carpeta remota, trazabilidad del modelo y descarga) | Soportes 02 y 03 |
| 21–22 nov | Manual de instalación (local, Windows y AWS EC2), manual de usuario con capturas y ejemplos, lista de soportes y reporte de trabajo en equipo | `Agregar manuales de instalación y usuario, reporte de trabajo en equipo y soportes…` |
| 22 nov | Diagrama de arquitectura de la solución | `Agregar diagrama de arquitectura de la solución` |
| 24 nov | Organización de los soportes de MLflow y del despliegue en el repositorio y actualización de los soportes de la API a la versión 1.1 | `Agregar soportes 06c y 13, y actualizar soportes 08, 09 y 11 a la API 1.1` |
| 21–24 nov | Redacción del informe de la Entrega 3, incluida la respuesta a la retroalimentación de la Entrega 2 sobre XGBoost frente a la persistencia y la lista de verificación de entregables | Informe de la Entrega 3 |

## 3. Decisiones tomadas en equipo

| Decisión | Motivo |
|---|---|
| Usar rezagos t-1 y t-2 y quitar la variable *año* | Los dos rezagos mejoraron el desempeño de los modelos; el año no aportaba |
| Validación cruzada temporal con ventanas expansivas | Evitar que el modelo use información del futuro al entrenar |
| Seleccionar XGBoost frente a Random Forest | Menor RMSE en la validación 2024 y menor complejidad (árboles de profundidad 3), que facilita empaquetarlo y servirlo desde la API |
| Justificar XGBoost frente a la persistencia por el RMSE | La persistencia acierta en los registros que repiten el valor anterior; XGBoost reduce los errores grandes en los registros que cambian, que son los relevantes para planificar |
| Separar API y tablero en dos imágenes Docker | Un cambio de modelo solo exige reconstruir la imagen de la API |
| Empaquetar el modelo como paquete de Python y construir la API en dos etapas | El modelo se instala con sus dependencias fijas y validación de entradas; la imagen final no lleva herramientas de construcción |
| Desplegar en una instancia EC2 con Docker Compose, separada del servidor MLflow | Con el `compose.yaml` las dos imágenes se despliegan juntas en una sola instancia, con la misma configuración probada localmente |
| Dejar fuera del alcance el pronóstico de varios semestres hacia adelante | Al usar cada estimación como insumo de la siguiente, el error se acumula |

## 4. Distribución de los entregables

| Entregable | Responsable |
|---|---|
| Preprocesamiento, variables de rezago y modelado | Simón y Víctor |
| Optimización, experimentos en MLflow y modelo registrado | Víctor y Simón |
| Análisis de errores en registros repetidos frente a registros que cambian | Simón |
| Modelo empaquetado y API | Víctor (primera versión de la API) y Simón (paquete y versión 1.1) |
| Tablero | Víctor |
| Despliegue en AWS EC2 y soportes de MLflow y del despliegue | Simón |
| Validación de la reproducibilidad en Windows y soportes de DVC, Docker y API | Javier |
| Manual de usuario y manual de instalación | Javier |
| Informe de la Entrega 3 y reporte de trabajo en equipo | Javier, con revisión del equipo |
| Video y diapositivas | Víctor, Simón y Javier |
