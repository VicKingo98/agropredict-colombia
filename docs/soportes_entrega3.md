# Soportes de la Entrega 3 — AgroPredict Colombia

Lista de verificación de los soportes que exige la guía de la Entrega 3. La guía advierte que **no entregar soportes lleva a una alta penalización**, así que cada ítem debe tener su evidencia (captura, enlace o archivo).

Guardar las capturas en `docs/soportes/` con el nombre indicado.

## 1. Repositorio Git

| Soporte | Evidencia | Estado |
|---|---|---|
| Código completo (notebooks, API, tablero, Dockerfiles, `compose.yaml`) | Enlace al repositorio | ✅ En GitHub |
| Aportes de todos los integrantes | Captura de *Insights → Contributors* o `git shortlog -sn` → `01_contribuidores.png` | ☐ |
| Pipelines de procesamiento y entrenamiento | Notebooks `02`, `03`, `04.1`, `05.1` | ✅ En GitHub |

## 2. Datos versionados en DVC

| Soporte | Evidencia | Estado |
|---|---|---|
| Archivos `.dvc` en el repositorio | `data/raw/*.dvc`, `data/processed/*.dvc`, `models/*.dvc` | ✅ |
| Remoto en Google Drive (`AgroPredict_Colombia_DVC/files/md5`) | Captura de la carpeta de Drive → `02_dvc_drive.png` | ✅ |
| Trazabilidad del modelo: el recibo `.dvc` (md5 `8af36dc7…`, 360.230 bytes) apunta al archivo guardado en Drive (carpeta `8a`, archivo `f36dc7…`, 352 KB) | `02c_dvc_recibo_modelo.png` y `02b_dvc_modelo_en_drive.png` | ✅ |
| Descarga funcionando | Captura de `dvc pull` exitoso → `03_dvc_pull.png` | ✅ |

## 3. Experimentos y modelos en MLflow

Servidor MLflow 3.18.0 en la instancia EC2 `mlflow-server` (t2.medium), experimento **`agropredict-maiz-rezagos-t1-t2`** (36 corridas).

| Soporte | Evidencia | Estado |
|---|---|---|
| Servidor MLflow en EC2 | Consola EC2 de `mlflow-server` → `04c_ec2_servidor_mlflow.png` | ✅ |
| Lista de corridas (baseline, Random Forest, XGBoost, comparación, evaluación y modelo de producción) | `04_mlflow_experimento.png` | ✅ |
| Búsqueda de hiperparámetros con validación cruzada temporal (cv_mae, cv_r2, cv_rmse por combinación) | `04b_mlflow_busqueda_cv.png` | ✅ |
| Comparación de modelos en validación 2024 | Captura de la corrida `Comparacion_modelos_validacion_2024` → `05_mlflow_comparacion.png` | ☐ Falta |
| Evaluación final 2025: métricas y parámetros | `06_mlflow_eval_2025.png` | ✅ |
| Evaluación final 2025: XGBoost frente a persistencia | `06b_mlflow_eval_2025_vs_persistencia.png` | ✅ |
| Modelo registrado `agropredict-maiz-xgb`, alias `champion` | `07_mlflow_registry.png` | ✅ |
| Versión 1: descripción, corrida de origen y esquema de entrada/salida | `07b_mlflow_registry_version1.png` | ✅ |

> Capturas tomadas por Simón Jaramillo. La IP del servidor MLflow cambia cuando se reinicia la instancia.

## 4. Modelo empaquetado y API

| Soporte | Evidencia | Estado |
|---|---|---|
| Modelo serializado (`models/xgboost_maiz_t1_t2.skops`) y sus metadatos (`.json`) | Repositorio y DVC | ✅ |
| Modelo empaquetado como paquete Python (`agropredict-model 1.0.0`, wheel) con pruebas pytest/tox | `model-package/` en el repositorio | ✅ |
| Construcción en dos etapas (paquete → imagen de la API) | Captura de `docker compose up --build` → `08b_build_multietapa.png` | ✅ (local) |
| Imágenes Docker construidas y contenedores activos (API *healthy*) | Captura de `docker compose ps` y `docker images` con `agropredict-api:1.1` → `08_docker_images.png` | ✅ (local) |
| API respondiendo con el modelo `champion` | Captura de `/health` → `09_api_health.png` | ✅ (local) |
| Información del modelo servido | Captura de `/modelo` → `09b_api_modelo.png` | ✅ (local) |
| Prueba de `/predict` por lote, con un registro válido y uno inválido | Captura de `/docs` con entrada y respuesta 200 → `10_api_predict.png` | ✅ (local) |
| Tablero llamando a la API | Predicción en el tablero + `docker compose logs api \| findstr predict` con `172.18.0.3 POST /predict 200 OK` → `11_logs_predict.png` | ✅ (local) |

## 5. Recursos del despliegue en la nube

Instancia EC2 `agropredict-model` (t3.medium, us-east-1 Norte de Virginia, IP pública 52.91.184.169), con Docker Compose.

| Soporte | Evidencia | Estado |
|---|---|---|
| Instancia en ejecución (tipo, región, IP) | Consola EC2 → `12_ec2_instancia.png` | ✅ |
| Reglas del grupo de seguridad (puertos 22, 8000, 8050) | Pestaña *Seguridad* de la instancia → `13_ec2_security_group.png` | ☐ Falta |
| Contenedores activos en el servidor (API *healthy*, imágenes 1.1 y 2.0) | `docker compose up --build` y `docker compose ps` por SSH → `14_ec2_compose_ps.png` | ✅ |
| Tablero accesible por IP pública | Predicción de Samaná (Caldas) en `http://52.91.184.169:8050` → `15_tablero_publico.png` | ✅ |
| API accesible por IP pública | `/health` desde `http://52.91.184.169:8000/docs` → `16_api_publica.png` | ✅ |

> Capturas tomadas por Simón Jaramillo.

## 6. Documentos

| Documento | Ubicación | Estado |
|---|---|---|
| Manual de instalación | `docs/manual_instalacion.md` | Borrador |
| Manual de usuario del tablero | `docs/manual_usuario.md` | ✅ Completo (7 capturas en `docs/img/`) |
| Reporte de trabajo en equipo | `docs/reporte_trabajo_equipo.md` | Borrador (cada integrante valida) |
| Reporte de máximo 10 páginas | `[completar]` | ☐ |
| Video (máx. 10 min, con los tres integrantes, mostrando despliegue y recursos) | `[enlace]` | ☐ |
| Diapositivas de apoyo del video | `[completar]` | ☐ |
