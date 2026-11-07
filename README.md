# AgroPredict Colombia

Prototipo analítico para estimar el rendimiento municipal del cultivo de maíz en Colombia mediante datos EVA de la UPRA.

## Objetivo

Analizar el comportamiento histórico del rendimiento agrícola del maíz y desarrollar un modelo predictivo que apoye la planificación agropecuaria territorial.

## Datos

- Fuente: UPRA - Evaluaciones Agropecuarias Municipales (EVA).
- Periodo: 2019-2025.
- Cobertura: municipios de Colombia.
- Variable objetivo: rendimiento agrícola (toneladas por hectárea).

Los datos originales se gestionan con DVC y se almacenan en Google Drive.

## Estructura

- data/raw: datos originales.
- data/processed: datos procesados.
- notebooks: EDA, preprocesamiento, variables, modelado y optimización.
- src: procesamiento y modelos.
- api: servicio de predicción.
- dashboard: visualizaciones interactivas.
- docs: documentación.
- tests: pruebas.

## Instalación
Crear y activar un ambiente virtual (Windows PowerShell):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Si PowerShell muestra "la ejecución de scripts está deshabilitada", ejecutar una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y volver a activar.

Instalar las dependencias:

    python -m pip install -r requirements.txt

Verificar que DVC tenga soporte para Google Drive:

```bash
python -m pip install "dvc[gdrive]"
```

## Configuración de DVC con Google Drive

Consultar el nombre del remoto configurado:

```bash
dvc remote list
```

En los comandos siguientes, reemplazar `gdrive_remote` por ese nombre.

### Opción 1: autenticación estándar

```bash
dvc pull
```

Se abrirá el navegador para autorizar el acceso con una cuenta de Google que tenga permisos sobre la carpeta de Drive del proyecto.

### Opción 2: cliente OAuth propio (si Google bloquea el acceso)

Si aparece el mensaje *"This app is blocked"* o *"Acceso bloqueado"*, es necesario usar un cliente OAuth propio:

1. En [Google Cloud Console](https://console.cloud.google.com/), crear o seleccionar un proyecto y habilitar la **Google Drive API**.
2. Configurar la pantalla de consentimiento OAuth (tipo *External*) y agregar como **usuarios de prueba** los correos de todos los miembros del equipo.
3. En *Credenciales*, crear un **ID de cliente OAuth** de tipo **Aplicación de escritorio**.
4. Configurar DVC con el ID y el secreto. La opción `--local` guarda las credenciales en `.dvc/config.local`, que no se versiona:

```bash
dvc remote modify gdrive_remote gdrive_client_id "<CLIENT_ID>" --local
dvc remote modify gdrive_remote gdrive_client_secret "<CLIENT_SECRET>" --local
dvc pull
```

### Opción 3: cuenta de servicio

1. En Google Cloud Console, crear una **cuenta de servicio** y descargar su llave en formato JSON.
2. Guardar el archivo en `config/` (carpeta ignorada por Git), por ejemplo `config/gdrive-sa.json`.
3. Compartir la carpeta de Google Drive del proyecto con el correo de la cuenta de servicio.
4. Configurar DVC:

```bash
dvc remote modify gdrive_remote gdrive_use_service_account true --local
dvc remote modify gdrive_remote gdrive_service_account_json_file_path config/gdrive-sa.json --local
dvc pull
```

> **Nota:** las cuentas de servicio no tienen cuota de almacenamiento propia en Google Drive, por lo que `dvc push` puede fallar si la carpeta está en un *Mi unidad* personal. Para subir datos con cuenta de servicio, la carpeta debe estar en una **unidad compartida**; de lo contrario, usar la opción 2.

### Error de token vencido

Si `dvc pull` muestra `invalid_grant: Token has been expired or revoked`, borrar las credenciales guardadas y volver a autenticar (Windows PowerShell):

```bash
Get-ChildItem $env:LOCALAPPDATA -Recurse -Filter default.json -ErrorAction SilentlyContinue | Where-Object FullName -match 'pydrive2fs' | Remove-Item
dvc pull
```

## Configuración de MLflow

Los notebooks leen la configuración desde `config/.env` (no se versiona). Copiar `config/.env.example` como `config/.env` y elegir el servidor:

- **Local:** `MLFLOW_TRACKING_URI=http://localhost:5000`
- **Servidor compartido en AWS EC2:** `MLFLOW_TRACKING_URI=http://IP_DE_LA_EC2:5000`

Para usar el servidor compartido:

1. Obtener la IP pública propia y enviarla al administrador de la instancia para que la agregue al grupo de seguridad (el puerto 5000 solo acepta IPs autorizadas):
   ```bash
   curl.exe -4 https://checkip.amazonaws.com
   ```
2. Pedir la IP actual de la EC2 (cambia cada vez que se reinicia la instancia) y ponerla en `config/.env`.
3. Verificar el acceso abriendo `http://IP_DE_LA_EC2:5000` en el navegador.
4. Reiniciar el kernel del notebook para que lea el `.env` actualizado.
5. Recomendado: agregar a cada corrida un tag `autor` con el nombre de quien la ejecutó.

> No ejecutar las celdas de registro de experimentos sin haber configurado el `.env`.

## Ejecución

Seleccionar el kernel `.venv` y ejecutar los notebooks en orden:

1. `02_preprocesamiento_maiz.ipynb`: limpieza y filtrado de datos.
2. `03_featuring.ipynb`: construcción de variables (estacionales y secuenciales).
3. `04_modelado.ipynb`: modelos iniciales (Ridge, Random Forest, XGBoost).
4. `05_optimizacion_modelos.ipynb`: optimización de hiperparámetros, comparación con baseline y modelo final.


## Estado

- Repositorio GitHub y versionamiento de datos y modelo con DVC.
- Preprocesamiento y construcción de variables completados.
- Modelos Ridge, Random Forest y XGBoost evaluados frente a un baseline de persistencia con validación temporal; XGBoost seleccionado como modelo final.
- Experimentos registrados en MLflow sobre AWS EC2.
- Tablero en desarrollo; API pendiente.
