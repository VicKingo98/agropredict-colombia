"""API de inferencia de AgroPredict Colombia.

Sirve el modelo empaquetado en agropredict_model (agropredict-maiz-xgb@champion).

Endpoints:
    GET  /health   Estado del servicio, versiones y métricas del modelo
    GET  /modelo   Variables, categorías válidas, hiperparámetros y métricas
    POST /predict  Predicción del rendimiento (t/ha) para uno o varios registros
    GET  /docs     Documentación interactiva (Swagger), generada por FastAPI
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agropredict_model import __version__ as VERSION_PAQUETE
from agropredict_model import cargar_metadatos, cargar_modelo, make_prediction
from fastapi.responses import RedirectResponse

# Registro de ejemplo que aparece en Swagger (/docs)
EJEMPLO_REGISTRO = {
    "semestre_b": 0,
    "rendimiento_rezago_1": 2.5,
    "rendimiento_rezago_2": 2.3,
    "departamento": "Tolima",
    "sistema_productivo": "tecnificado",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo al arrancar el servicio.

    Si el .skops está dañado o falta, la API falla al iniciar y no en la primera
    predicción. Además, la primera petición no paga el tiempo de carga.
    """
    cargar_modelo()
    yield


app = FastAPI(
    title="AgroPredict Colombia API",
    description="Servicio de inferencia del rendimiento municipal del maíz (t/ha).",
    version=VERSION_PAQUETE,
    lifespan=lifespan,
)

@app.get("/", include_in_schema=False)
def raiz():
    """Redirige la raíz a la documentación interactiva."""
    return RedirectResponse(url="/docs")

# ---------------------------------------------------------------------------
# Esquemas de la API
# ---------------------------------------------------------------------------

class SolicitudPrediccion(BaseModel):
    """Cuerpo de POST /predict: el mismo formato que ya usa el tablero.

    Los registros se reciben como dicts y los valida el paquete (schemas.py),
    para que un registro inválido no rechace todo el lote.
    """

    registros: list[dict[str, Any]] = Field(
        min_length=1,
        max_length=5000,
        json_schema_extra={"example": [EJEMPLO_REGISTRO]},
    )


class ErrorRegistro(BaseModel):
    indice: int
    detalle: list[str]


class RespuestaPrediccion(BaseModel):
    predicciones: list[float | None]
    unidad: str
    errores: list[ErrorRegistro]
    modelo: str
    version_modelo: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Estado del servicio y versión del modelo que está respondiendo."""
    metadatos = cargar_metadatos()
    return {
        "status": "ok",
        "version_paquete": VERSION_PAQUETE,
        "modelo": metadatos["nombre_registry"],
        "version_modelo": metadatos["version_registry"],
        "metricas_test_2025": metadatos["metricas_test_2025"],
    }


@app.get("/modelo")
def modelo():
    """Información del modelo, útil para la pestaña 'Acerca del modelo' del tablero."""
    metadatos = cargar_metadatos()
    campos = [
        "nombre_registry",
        "version_registry",
        "variables",
        "departamentos",
        "sistemas_productivos",
        "hiperparametros",
        "periodo_entrenamiento",
        "metricas_test_2025",
        "metricas_persistencia_2025",
    ]
    return {campo: metadatos[campo] for campo in campos}


@app.post("/predict", response_model=RespuestaPrediccion)
def predict(solicitud: SolicitudPrediccion):
    """Predice el rendimiento de cada registro, en el mismo orden de entrada.

    - Registros válidos: predicción en t/ha.
    - Registros inválidos: None en su posición y el detalle en `errores`.
    - Si ningún registro es válido: 422 con los errores.
    """
    resultado = make_prediction(solicitud.registros)

    if all(prediccion is None for prediccion in resultado["predicciones"]):
        raise HTTPException(status_code=422, detail=resultado["errores"])

    return resultado