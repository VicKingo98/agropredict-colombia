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
- notebooks: análisis exploratorio.
- src: procesamiento y modelos.
- api: servicio de predicción.
- dashboard: visualizaciones interactivas.
- docs: documentación.
- tests: pruebas.

## Instalación

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

## Estado

- Repositorio GitHub configurado.
- Versionamiento de datos con DVC.
- Análisis exploratorio en desarrollo.
- Modelo predictivo, API y tablero pendientes.
