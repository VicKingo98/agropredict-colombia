"""Rutas y metadatos del modelo empaquetado."""

import json
from functools import lru_cache
from importlib import resources

DIR_MODELOS = resources.files("agropredict_model") / "trained_models"
ARCHIVO_MODELO = "xgboost_maiz_t1_t2.skops"
ARCHIVO_METADATOS = "xgboost_maiz_t1_t2.json"


@lru_cache
def cargar_metadatos() -> dict:
    """Metadatos generados en 05.1_optimizacion_modelos (registry, variables, categorías y métricas)."""
    contenido = (DIR_MODELOS / ARCHIVO_METADATOS).read_text(encoding="utf-8")
    return json.loads(contenido)