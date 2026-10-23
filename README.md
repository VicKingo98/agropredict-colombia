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

Recuperar los datos (requiere autorización de Google Drive):

    dvc pull

## Estado

- Repositorio GitHub configurado.
- Versionamiento de datos con DVC.
- Análisis exploratorio en desarrollo.
- Modelo predictivo, API y tablero pendientes.
