# Soportes de la Entrega 3 — AgroPredict Colombia

Índice de los soportes de la Entrega 3. Las capturas están en `docs/soportes/` con el nombre indicado en cada fila.

## 1. Repositorio Git

| Soporte | Evidencia | Estado |
|---|---|---|
| Código completo (notebooks, API, tablero, Dockerfiles, `compose.yaml`) | https://github.com/VicKingo98/agropredict-colombia | ✅ |
| Aportes de todos los integrantes | Historial de commits del repositorio y `docs/reporte_trabajo_equipo.md` | ✅ |
| Pipelines de procesamiento y entrenamiento | Notebooks `02`, `03`, `04.1` y `05.1` en `notebooks/` | ✅ |

## 2. Datos versionados en DVC

| Soporte | Evidencia | Estado |
|---|---|---|
| Archivos `.dvc` en el repositorio | `data/raw/*.dvc`, `data/processed/*.dvc`, `models/*.dvc` | ✅ |
| Remoto en Google Drive (`AgroPredict_Colombia_DVC/files/md5`) | `02_dvc_drive.png` | ✅ |
| Trazabilidad del modelo: el archivo `.dvc` (md5 `8af36dc7…`, 360.230 bytes) apunta al archivo guardado en Drive (carpeta `8a`, archivo `f36dc7…`, 352 KB) | `02c_dvc_recibo_modelo.png` y `02b_dvc_modelo_en_drive.png` | ✅ |
| Descarga funcionando | `03_dvc_pull.png` | ✅ |

## 3. Experimentos y modelos en MLflow

Servidor MLflow 3.18.0 en la instancia EC2 `mlflow-server` (t2.medium), experimento **`agropredict-maiz-rezagos-t1-t2`** (36 corridas).

| Soporte | Evidencia | Estado |
|---|---|---|
| Servidor MLflow en EC2 | `04c_ec2_servidor_mlflow.png` | ✅ |
| Lista de corridas (persistencia, Random Forest, XGBoost, comparación, evaluación y modelo de producción) | `04_mlflow_experimento.png` | ✅ |
| Búsqueda de hiperparámetros con validación cruzada temporal (cv_mae, cv_r2 y cv_rmse por combinación) | `04b_mlflow_busqueda_cv.png` | ✅ |
| Evaluación final 2025: métricas y parámetros | `06_mlflow_eval_2025.png` | ✅ |
| Evaluación final 2025: XGBoost frente a persistencia | `06b_mlflow_eval_2025_vs_persistencia.png` | ✅ |
| Error de XGBoost y persistencia en 2025: registros que repiten el valor anterior frente a registros que cambian | `06c_mlflow_errores_repetidos_vs_cambios.png` | ✅ |
| Modelo registrado `agropredict-maiz-xgb`, alias `champion` | `07_mlflow_registry.png` | ✅ |
| Versión 1: descripción, corrida de origen y esquema de entrada y salida | `07b_mlflow_registry_version1.png` | ✅ |

## 4. Modelo empaquetado y API

| Soporte | Evidencia | Estado |
|---|---|---|
| Modelo serializado (`models/xgboost_maiz_t1_t2.skops`) y sus metadatos (`models/xgboost_maiz_t1_t2.json`) | Repositorio y DVC | ✅ |
| Modelo empaquetado como paquete de Python (`agropredict-model 1.0.0`, wheel) con pruebas pytest y tox | `model-package/` | ✅ |
| Construcción en dos etapas (paquete → imagen de la API) | `08b_build_multietapa.png` | ✅ |
| Imágenes Docker construidas y contenedores activos (API *healthy*, `agropredict-api:1.1`) | `08_docker_images.png` | ✅ |
| API respondiendo con el modelo `champion` (`/health`) | `09_api_health.png` | ✅ |
| Información del modelo servido (`/modelo`) | `09b_api_modelo.png` | ✅ |
| Prueba de `/predict` por lote, con un registro válido y uno inválido | `10_api_predict.png` | ✅ |
| Tablero llamando a la API (`POST /predict 200 OK` desde el contenedor del tablero) | `11_logs_predict.png` | ✅ |

## 5. Recursos del despliegue en la nube

Instancia EC2 `agropredict-model` (t3.medium, us-east-1 Norte de Virginia) con Docker Compose. La IP pública cambia cada vez que la instancia se reinicia; al momento de las pruebas era 52.91.184.169.

| Soporte | Evidencia | Estado |
|---|---|---|
| Instancia en ejecución (tipo, región e IP) | `12_ec2_instancia.png` | ✅ |
| Reglas de entrada del grupo de seguridad (TCP 8000 y 8050, SSH 22) | `13_ec2_security_group.png` | ✅ |
| Contenedores activos en el servidor (API *healthy*, imágenes 1.1 y 2.0) | `14_ec2_compose_ps.png` | ✅ |
| Tablero accesible por IP pública (puerto 8050) | `15_tablero_publico.png` | ✅ |
| API accesible por IP pública (puerto 8000) | `16_api_publica.png` | ✅ |

## 6. Documentos

| Documento | Ubicación | Estado |
|---|---|---|
| Manual de instalación | `docs/manual_instalacion.md` | ✅ |
| Manual de usuario del tablero | `docs/manual_usuario.md` (capturas en `docs/img/`) | ✅ |
| Reporte de trabajo en equipo | `docs/reporte_trabajo_equipo.md` | ✅ |
| Video (máx. 10 min, con los tres integrantes, mostrando el despliegue y sus recursos) | https://youtu.be/S0w2Fk9QMWE | ✅ |
