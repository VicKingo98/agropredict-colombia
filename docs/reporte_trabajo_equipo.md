# Reporte de trabajo en equipo — AgroPredict Colombia (Grupo 11)

**Integrantes:** Víctor M. Osorio · Simón Jaramillo · Javier Cañarte
**Repositorio:** https://github.com/VicKingo98/agropredict-colombia

> **Borrador.** Las contribuciones se reconstruyeron a partir del historial de commits del repositorio (corte: 22 de noviembre de 2026). Cada integrante debe revisar su parte y completar los campos marcados con `[completar]` antes de la entrega.

## 1. Organización del trabajo

- **Canal de coordinación:** grupo de WhatsApp para reportar avances, repartir tareas y tomar decisiones.
- **Flujo en el repositorio:** cada integrante trabaja en su copia local, publica en `main` y documenta en el mensaje del commit lo realizado. Los cambios de documentación pasaron por *pull request* (PR #1).
- **Versionamiento:** código en GitHub, datos y modelos en DVC (Google Drive) y experimentos en un servidor MLflow compartido en AWS EC2.
- **Reuniones / sesiones de revisión:** `[completar fechas y temas]`

> Simón aparece en el historial con dos identidades de Git (`sijaramillogo` y `Simón Jaramillo G`). En este reporte se suman como una sola persona.

## 2. Contribuciones por integrante

### Víctor M. Osorio

| Fecha | Aporte | Evidencia (commit) |
|---|---|---|
| 22–23 oct | Estructura del repositorio, inicialización de DVC, registro de la base EVA 2019–2025 y remoto en Google Drive | `Crear estructura inicial…`, `Inicializar DVC…`, `Configurar almacenamiento remoto…` |
| 23 oct | Análisis exploratorio inicial y documentación base | `Incorporar análisis exploratorio…` |
| 6–7 nov | Optimización de modelos y registro de experimentos en MLflow EC2; versionamiento del modelo con DVC | `Agregar optimizacion de modelos…`, `Optimizar modelos con rezago secuencial…` |
| 7–8 nov | Desarrollo del tablero en Dash: identidad visual, comparación histórica, predicción múltiple y departamental, exportación CSV/Excel y mapa municipal | `implementar dashboard Dash…`, `Integrar mapa municipal…` |
| 15–18 nov | Validación de rezagos, validación cruzada temporal con ventanas expansivas, búsqueda de hiperparámetros (Random Forest y XGBoost) y selección de XGBoost | `Agregar validaciones de rezagos…`, `Optimizar modelos con validacion temporal…` |
| 19 nov | Integración del modelo con rezagos t-1 y t-2 en el tablero; API REST con FastAPI (`/health`, `/predict`); contenerización de API y tablero con Docker Compose | `integrar modelo XGBoost con rezagos…`, `Integrar API FastAPI y dashboard con Docker Compose` |

### Simón Jaramillo

| Fecha | Aporte | Evidencia (commit) |
|---|---|---|
| 24 oct | Perfil de variables y exportación de figuras del EDA; documentación de DVC con Google Drive; prototipo de *mockup* del tablero con plantillas de carga | `EDA: perfil de variables…`, `Documentar configuración de DVC…`, `Prototipo inicial de mockup…` |
| 1–5 nov | Notebook de preprocesamiento, versionamiento de datos procesados, separación de *featuring* y modelado, configuración del entorno MLflow | `Agrega notebook de preprocesamiento…`, `Separa featuring y modelado…` |
| 7 nov | Modelado secuencial y ajustes al registro de métricas en el servidor MLflow | `Agrega modelado secuencial…`, `actualizacion notebooks ml flow server` |
| 14 nov | Construcción de variables de rezago t-1 y t-2 (`features_rezago_1_2.parquet`, versionado en DVC) y notebooks `04.1` y `05.1`; identificación de registros con rendimiento idéntico al semestre anterior | `actualizacion 03 featuring…`, `Features con rezagos t-1 y t-2…` |
| 18 nov | Base del notebook de optimización con rezagos | `comienzo de optimizacion para rezagos t-1 y t-2` |
| 21 nov | Registro de experimentos y del modelo final en el *Model Registry* de MLflow (`agropredict-maiz-xgb`, alias `champion`, versión 1) y metadatos del modelo | `Registrar experimentos y modelo XGBoost t1-t2 en MLflow EC2…` |
| 21 nov | Empaquetamiento del modelo como paquete de Python (`agropredict-model`) con validación de entradas, pruebas pytest y tox | `Empaquetar modelo XGBoost t1-t2 como paquete Python…` |
| 21 nov | API consumiendo el paquete, construcción en dos etapas, chequeo de salud en Compose, `.dockerignore` sin credenciales y manejo de errores de la API en el tablero | `API consume el paquete agropredict-model…`, `Excluir credenciales…`, `Healthcheck en compose…` |
| 21 nov | Despliegue en AWS EC2 (instancia `agropredict-model`, t3.medium) y capturas de MLflow y del despliegue | Soportes 04–07, 12, 14–16 |

### Javier Cañarte

| Fecha | Aporte | Evidencia (commit) |
|---|---|---|
| 25 oct | Documentación de hallazgos del EDA sobre el rendimiento del maíz | `docs: document EDA findings for maize yield` |
| 7 nov | Guía de reproducibilidad: instalación del entorno, configuración de MLflow en EC2 y estado del proyecto; revisión e integración del PR #1 | `Agrega documentación de instalación, MLflow en EC2…`, `Merge pull request #1` |
| 21–22 nov | Validación de la reproducibilidad en un segundo equipo (Windows): instalación de Docker, construcción de las imágenes y pruebas de la API (`/health`, `/modelo`, `/predict` por lotes) y del tablero | Soportes 08–11 |
| 22 nov | Detección y corrección del error de finales de línea que impedía construir la API en Windows (archivo `.gitattributes`) | `Agregar .gitattributes para conservar finales de línea LF…` |
| 21–22 nov | Soportes de DVC (carpeta remota, trazabilidad del modelo y descarga) | Soportes 02–03 |
| 21–22 nov | Documentación de la Entrega 3: manual de instalación (local y AWS EC2), manual de usuario con capturas y ejemplos, lista de soportes y reporte de trabajo en equipo | `Agregar manuales de instalación y usuario, reporte de trabajo en equipo y soportes…` |
| 21–22 nov | Borrador del reporte de 10 páginas, con la respuesta a la retroalimentación de la Entrega 2 sobre XGBoost frente a la persistencia | `[enlace o archivo del reporte]` |

## 3. Decisiones tomadas en equipo

| Decisión | Motivo |
|---|---|
| Usar rezagos t-1 y t-2 y quitar la variable *año* | Los rezagos mejoraron el desempeño; el año no aportaba al modelo |
| Validación cruzada temporal con ventanas expansivas | Evitar que el modelo "vea el futuro" al entrenar |
| Seleccionar XGBoost frente a Random Forest | Menor RMSE en la validación 2024 |
| Separar API y tablero en dos imágenes Docker | Un cambio de modelo solo exige reconstruir la API |
| Empaquetar el modelo como paquete de Python y construir la API en dos etapas | El modelo se instala con sus dependencias fijas y validación de entradas; la imagen final no lleva herramientas de construcción |
| Desplegar en una instancia EC2 con Docker Compose, separada del servidor MLflow | Reproduce en la nube la misma configuración probada localmente y reutiliza la cuenta de AWS del equipo; se descartaron ECR + ECS por complejidad y Railway porque muestra menos recursos `[confirmar]` |
| Dejar el pronóstico de varios semestres como trabajo futuro `[confirmar]` | El error se acumula al usar predicciones como insumo |

## 4. Pendientes y responsables (Entrega 3 — 24 de noviembre)

| Tarea | Responsable | Estado |
|---|---|---|
| Despliegue de API y tablero en la nube | Simón | Hecho |
| Soportes de MLflow y del despliegue | Simón | Faltan 05 (comparación 2024) y 13 (grupo de seguridad) |
| Soportes locales (DVC, Docker, API) | Javier | Hecho |
| Manuales de usuario e instalación | Javier | Hecho |
| Actualizar la pestaña *Acerca del modelo* con las métricas del modelo `champion` | `[por definir]` | Pendiente |
| Análisis del error en registros repetidos frente a registros que cambiaron (respuesta a la rúbrica) | `[por definir]` | Pendiente |
| Reporte de máximo 10 páginas | Javier (borrador), todos (revisión) | En revisión |
| Diapositivas y video (máx. 10 min, los tres integrantes) | Todos | Pendiente |

## 5. Valoración del trabajo en equipo

`[completar: cómo se distribuyó la carga, qué funcionó bien, qué mejorarían. Si el curso pide autoevaluación o coevaluación, incluirla aquí.]`
