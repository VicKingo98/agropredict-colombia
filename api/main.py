from pathlib import Path

import pandas as pd
import skops.io as sio
from fastapi import FastAPI
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]

VARIABLES_MODELO = [
    "semestre_b",
    "rendimiento_rezago_1",
    "rendimiento_rezago_2",
    "departamento",
    "sistema_productivo",
]

modelo = sio.load(
    ROOT / "models/xgboost_maiz_t1_t2.skops",
    trusted=[
        "xgboost.core.Booster",
        "xgboost.sklearn.XGBRegressor",
    ],
)

app = FastAPI(
    title="AgroPredict Colombia API",
    description="Servicio de inferencia del rendimiento municipal del maíz.",
    version="1.0.0",
)


class RegistroPrediccion(BaseModel):
    semestre_b: int = Field(ge=0, le=1)
    rendimiento_rezago_1: float = Field(ge=0)
    rendimiento_rezago_2: float = Field(ge=0)
    departamento: str = Field(min_length=1)
    sistema_productivo: str = Field(min_length=1)


class SolicitudPrediccion(BaseModel):
    registros: list[RegistroPrediccion] = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok", "modelo": "xgboost_maiz_t1_t2"}


@app.post("/predict")
def predict(solicitud: SolicitudPrediccion):
    entradas = pd.DataFrame(
        [registro.model_dump() for registro in solicitud.registros]
    )[VARIABLES_MODELO]

    estimaciones = modelo.predict(entradas)

    return {
        "predicciones": [float(valor) for valor in estimaciones],
        "unidad": "t/ha",
        "total": len(estimaciones),
    }
