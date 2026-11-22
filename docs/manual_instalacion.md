# Manual de instalación — AgroPredict Colombia

Este manual explica cómo poner en marcha el prototipo **AgroPredict Colombia** (API de predicción + tablero) en un computador local o en un servidor en la nube. La solución corre en **dos contenedores Docker** que se levantan juntos con Docker Compose.

> **Idea general.** Piense en la solución como un restaurante con dos áreas: la **cocina (API)** prepara las predicciones con el modelo, y el **salón (tablero)** atiende al usuario y le lleva los pedidos a la cocina. Docker Compose abre las dos áreas al mismo tiempo, las deja comunicadas y no abre el salón hasta que la cocina está lista.

---

## 1. Componentes

| Componente | Qué hace | Puerto | Archivos que lo construyen |
|---|---|---|---|
| **Paquete del modelo** (`agropredict-model 1.0.0`) | Empaqueta el modelo XGBoost (`.skops`) y sus metadatos (`.json`) como paquete de Python. Valida cada registro de entrada antes de predecir. | — | `model-package/` |
| **API** (FastAPI) | Instala el paquete del modelo y sirve las predicciones. Endpoints: `/health`, `/modelo`, `/predict` y `/docs`. | 8000 | `Dockerfile.api`, `requirements-api.txt` |
| **Tablero** (Dash) | Interfaz web con consulta histórica, predicción, resultados e información del modelo. Pide las predicciones a la API por HTTP. | 8050 | `Dockerfile`, `requirements-dashboard.txt` |
| **Orquestación** | Levanta ambos servicios en una red interna. El tablero encuentra la API en `http://api:8000` y arranca solo cuando la API responde a `/health`. | — | `compose.yaml` |

Los archivos pesados (modelo y datos procesados) **no están en GitHub**: se versionan con **DVC** en Google Drive y hay que descargarlos antes de construir las imágenes.

| Archivo necesario | Lo usa | Cómo se obtiene |
|---|---|---|
| `models/xgboost_maiz_t1_t2.skops` | Paquete del modelo → API | `dvc pull` |
| `models/xgboost_maiz_t1_t2.json` | Paquete del modelo → API | Ya viene en el repositorio |
| `data/processed/features_rezago_1_2.parquet` | Tablero | `dvc pull` |
| `data/geografica/municipios_dane_2025_plotly.geojson` | Tablero (mapa) | Ya viene en el repositorio |

---

## 2. Requisitos previos

- **Git** para clonar el repositorio.
- **Docker Desktop** (Windows/macOS) o Docker Engine con el plugin Compose (Linux). En Windows debe estar abierto antes de ejecutar los comandos.
- **Python 3.12 o superior** y **DVC con soporte para Google Drive**, solo para descargar el modelo y los datos.
- Una cuenta de Google con permiso sobre la carpeta de Drive del proyecto (ver la sección de DVC del `README.md`).

> **Windows: virtualización.** Docker Desktop necesita la virtualización del procesador activada en la BIOS (en equipos AMD se llama *SVM Mode*; en Intel, *Intel Virtualization Technology*) y el componente *Plataforma de máquina virtual* de Windows. Este último se activa ejecutando `wsl --install --no-distribution` en PowerShell como administrador y reiniciando. Se puede comprobar en el Administrador de tareas → Rendimiento → CPU → *Virtualización: Habilitado*.

---

## 3. Instalación local paso a paso

Los comandos se escriben en una terminal ubicada en la carpeta donde se quiere guardar el proyecto.

### 3.1 Obtener el código

```bash
git clone https://github.com/VicKingo98/agropredict-colombia.git
cd agropredict-colombia
```

Si ya se tenía el repositorio clonado, basta con traer la última versión:

```bash
git pull origin main
```

> **Windows: finales de línea.** El repositorio incluye un archivo `.gitattributes` que obliga a Git a conservar los scripts `.sh` con finales de línea de Linux. Sin él, Git en Windows los convierte al formato de Windows y la construcción de la API falla con el error `$'\r': command not found` en `build.sh`. Si el repositorio se clonó antes de que existiera ese archivo, basta con volver a descargar el script:
>
> ```
> del model-package\build.sh
> git checkout -- model-package/build.sh
> ```

### 3.2 Descargar el modelo y los datos con DVC

Crear un ambiente virtual e instalar DVC (solo la primera vez):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (cmd); en PowerShell: .venv\Scripts\Activate.ps1
python -m pip install "dvc[gdrive]"
```

Descargar los archivos versionados:

```bash
dvc pull
```

La primera vez se abre el navegador para autorizar la cuenta de Google. Si Google bloquea el acceso, seguir las alternativas del `README.md` (cliente OAuth propio o cuenta de servicio).

Verificar que existan los dos archivos clave:

```bash
dir models\xgboost_maiz_t1_t2.skops
dir data\processed\features_rezago_1_2.parquet
```

### 3.3 Construir y levantar los contenedores

```bash
docker compose up --build -d
```

- `--build` construye las imágenes `agropredict-api:1.1` y `agropredict-colombia:2.0`.
- `-d` deja los servicios corriendo en segundo plano.

**Qué pasa durante la construcción de la API.** El `Dockerfile.api` trabaja en **dos etapas**:

1. **Etapa de construcción:** copia `model-package/` y el modelo, y ejecuta `model-package/build.sh`, que mete el `.skops` y el `.json` dentro del paquete y genera el archivo instalable (`agropredict_model-1.0.0-py3-none-any.whl`).
2. **Etapa final:** parte de una imagen limpia de Python, instala solo ese `.whl` junto con FastAPI y uvicorn, y copia el código de la API.

Así, las herramientas de construcción y los archivos intermedios no quedan en la imagen que se despliega.

La primera construcción tarda varios minutos porque descarga la imagen base de Python e instala las librerías. Las siguientes son más rápidas porque Docker reutiliza los pasos que no cambiaron (aparecen como `CACHED`).

### 3.4 Verificar que todo funciona

```bash
docker compose ps
```

La API debe aparecer con estado **`Up ... (healthy)`** y el tablero con **`Up`**. Compose consulta `/health` cada 10 segundos y no arranca el tablero hasta que la API responde.

| Verificación | Dirección | Resultado esperado |
|---|---|---|
| Estado de la API | http://localhost:8000/health | `"status": "ok"`, el modelo `agropredict-maiz-xgb`, su versión y las métricas de la prueba 2025 |
| Información del modelo | http://localhost:8000/modelo | Variables, departamentos válidos, hiperparámetros y métricas frente a la persistencia |
| Documentación interactiva | http://localhost:8000/docs (también http://localhost:8000 redirige ahí) | Página de FastAPI con todos los endpoints |
| Tablero | http://localhost:8050 | Tablero con las pestañas *Consulta histórica*, *Predicción*, *Resultados* y *Acerca del modelo* |

Para ver los registros de la API:

```bash
docker compose logs api
```

La mayoría de líneas son el chequeo automático de `/health` (desde `127.0.0.1`). Para ver solo las predicciones:

```bash
docker compose logs api | findstr predict      # Windows
docker compose logs api | grep predict         # Linux / macOS
```

Cada predicción hecha desde el tablero aparece como `POST /predict HTTP/1.1" 200 OK`, desde la dirección interna del contenedor del tablero.

### 3.5 Probar la API directamente (opcional)

`POST /predict` recibe una lista de registros con cinco variables:

| Variable | Tipo | Descripción |
|---|---|---|
| `semestre_b` | entero (0 o 1) | 0 = semestre A, 1 = semestre B |
| `rendimiento_rezago_1` | número | Rendimiento del semestre anterior (t-1), en t/ha |
| `rendimiento_rezago_2` | número | Rendimiento de dos semestres atrás (t-2), es decir, el mismo semestre del año anterior, en t/ha |
| `departamento` | texto | Uno de los 31 departamentos del entrenamiento; acepta minúsculas y sin tildes (`cordoba`) |
| `sistema_productivo` | texto | `tradicional` o `tecnificado` |

La forma más sencilla de probarla es desde http://localhost:8000/docs → **POST /predict** → **Try it out**, pegando por ejemplo:

```json
{
  "registros": [
    {"semestre_b": 0, "rendimiento_rezago_1": 4.2, "rendimiento_rezago_2": 4.0,
     "departamento": "cordoba", "sistema_productivo": "tecnificado"},
    {"semestre_b": 1, "rendimiento_rezago_1": 2.0, "rendimiento_rezago_2": 1.8,
     "departamento": "Atlántida", "sistema_productivo": "tradicional"}
  ]
}
```

Respuesta esperada (código 200):

```json
{
  "predicciones": [4.1671, null],
  "unidad": "t/ha",
  "errores": [{"indice": 1, "detalle": ["... Departamento 'Atlántida' no fue visto en el entrenamiento ..."]}],
  "modelo": "agropredict-maiz-xgb",
  "version_modelo": 1
}
```

Cada registro se valida por separado: un registro inválido queda en `null` con su explicación en `errores`, sin afectar a los demás. Solo si **ningún** registro es válido la API responde con código 422.

### 3.6 Detener los servicios

```bash
docker compose down
```

---

## 4. Actualizar el modelo

Como la API y el tablero están en imágenes separadas, **un cambio de modelo solo obliga a reconstruir la API**:

```bash
git pull origin main
dvc pull
docker compose build api
docker compose up -d
```

El tablero no necesita reconstruirse, salvo que cambie su código (`dashboard/`) o los datos históricos (`features_rezago_1_2.parquet`).

Las imágenes antiguas que ya no se usan se pueden borrar para liberar espacio, por ejemplo `docker rmi agropredict-api:1.0`.

---

## 5. Pruebas del paquete del modelo (opcional)

El paquete incluye pruebas automáticas con pytest (carga del modelo, predicción individual y por lotes, departamentos sin tildes, departamentos desconocidos y valores inválidos). Se ejecutan con tox, que construye el paquete y lo prueba en un ambiente aislado:

```bash
pip install tox
cd model-package
tox
```

En Windows, tox necesita `bash` para ejecutar `build.sh`; se puede usar la terminal *Git Bash* que se instala con Git.

---

## 6. Ejecución sin Docker (modo desarrollo)

Útil para hacer cambios rápidos al código. Se necesitan dos terminales con el ambiente virtual activado.

**Terminal 1 — paquete y API:**

```bash
pip install build
bash model-package/build.sh
pip install model-package/dist/agropredict_model-1.0.0-py3-none-any.whl
pip install -r requirements-api.txt
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — tablero:**

```bash
pip install -r requirements-dashboard.txt
python dashboard/app.py
```

Por defecto el tablero busca la API en `http://127.0.0.1:8000`. Para apuntar a otra dirección se usa la variable de entorno `AGROPREDICT_API_URL`:

```powershell
$env:AGROPREDICT_API_URL = "http://IP_DEL_SERVIDOR:8000"
python dashboard/app.py
```

---

## 7. Despliegue en AWS EC2

La solución se desplegó en una instancia EC2 independiente de la que aloja el servidor MLflow:

| Recurso | Uso | Tipo | Región |
|---|---|---|---|
| `agropredict-model` | API y tablero con Docker Compose | t3.medium | us-east-1 (Norte de Virginia) |
| `mlflow-server` | Servidor de experimentos y Model Registry de MLflow | t2.medium | us-east-1 (Norte de Virginia) |

La dirección IP pública cambia cada vez que una instancia se detiene y se vuelve a iniciar (no tienen IP elástica). Al momento de las pruebas, la solución respondía en `http://52.91.184.169:8050` (tablero) y `http://52.91.184.169:8000/docs` (API).

### 7.1 Crear la instancia

1. En la consola de AWS → **EC2** → **Launch instance**.
2. Sistema operativo: **Ubuntu Server**.
3. Tipo: **t3.medium** (2 vCPU, 4 GB de RAM). Con 1 GB de RAM la construcción de las imágenes puede fallar por falta de memoria.
4. Seleccionar o crear un par de llaves (`.pem`) y guardarlo en un lugar seguro.

### 7.2 Configurar el grupo de seguridad (los "puertos abiertos")

| Puerto | Uso | Origen recomendado |
|---|---|---|
| 22 | Conexión SSH para administrar la instancia | Solo la IP de quien administra |
| 8050 | Tablero | Público o las IPs del equipo y tutores |
| 8000 | API (para mostrar `/docs` y `/health`) | Las IPs del equipo y tutores |

*[Completar con las reglas reales de la instancia `agropredict-model` — soporte 13.]*

### 7.3 Conectarse e instalar Docker

Conectarse por SSH (reemplazar la ruta de la llave y la IP pública):

```bash
ssh -i ruta/a/llave.pem ubuntu@IP_PUBLICA
```

Instalar Docker con el plugin Compose (una opción en Ubuntu):

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu
```

Cerrar la sesión SSH y volver a entrar para que el último cambio tenga efecto.

### 7.4 Llevar el código, el modelo y los datos

```bash
git clone https://github.com/VicKingo98/agropredict-colombia.git
cd agropredict-colombia
```

El modelo y los datos se traen con `dvc pull` o, si autenticar Google Drive desde el servidor resulta engorroso, copiándolos desde un computador que ya los tenga (desde el computador local):

```bash
scp -i ruta/a/llave.pem models/xgboost_maiz_t1_t2.skops ubuntu@IP_PUBLICA:~/agropredict-colombia/models/
scp -i ruta/a/llave.pem data/processed/features_rezago_1_2.parquet ubuntu@IP_PUBLICA:~/agropredict-colombia/data/processed/
```

### 7.5 Levantar la solución

En la instancia, dentro de `agropredict-colombia`:

```bash
docker compose up --build -d
docker compose ps
```

La API debe quedar **healthy** y el tablero **Up**. Verificar desde el navegador:

- Tablero: `http://IP_PUBLICA:8050`
- API: `http://IP_PUBLICA:8000/health` y `http://IP_PUBLICA:8000/docs`

Gracias a `restart: unless-stopped` en `compose.yaml`, los contenedores vuelven a arrancar solos si la instancia se reinicia.

### 7.6 Apagar para no generar costos

Después de grabar el video y validar la entrega, detener las instancias desde la consola de EC2 (**Estado de la instancia → Detener**).

---

## 8. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `build.sh: line 7: $'\r': command not found` al construir la API | El script quedó con finales de línea de Windows | Confirmar que existe `.gitattributes` y volver a descargar el script (sección 3.1) |
| `COPY failed ... xgboost_maiz_t1_t2.skops: not found` o `Falta ../models/... (ejecutar dvc pull)` | No se descargó el modelo | Ejecutar `dvc pull` y repetir `docker compose up --build -d` |
| `COPY failed ... features_rezago_1_2.parquet: not found` | Faltan los datos procesados | Igual que el anterior |
| Docker Desktop indica que necesita una máquina virtual | Virtualización desactivada o falta la Plataforma de máquina virtual | Ver la nota de la sección 2 |
| `error during connect` o `Cannot connect to the Docker daemon` | Docker Desktop no está abierto | Abrir Docker Desktop y esperar *Engine running* |
| `port is already allocated` | Otro programa usa el puerto 8000 u 8050 | Cerrar ese programa o cambiar el puerto izquierdo en `compose.yaml` (por ejemplo `"8051:8050"`) |
| El tablero no arranca y la API aparece `unhealthy` | La API no pudo cargar el modelo | `docker compose logs api` para ver el error de carga |
| El tablero muestra *"No fue posible conectar con el servicio de predicción"* | La API no está activa o no es alcanzable | `docker compose ps` y `docker compose logs api` |
| `invalid_grant: Token has been expired or revoked` en `dvc pull` | Credenciales de Google vencidas | En cmd: `rmdir /s /q "%LOCALAPPDATA%\pydrive2fs"` y repetir `dvc pull` |
| El tablero no carga desde EC2 | Puerto cerrado en el grupo de seguridad o IP cambiada | Revisar las reglas de entrada y la IP pública actual |
