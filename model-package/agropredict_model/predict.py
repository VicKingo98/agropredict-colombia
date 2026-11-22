"""Carga del modelo y generación de predicciones.

Flujo de make_prediction:
1. Convierte la entrada (dict, lista de dicts o DataFrame) en una lista de registros.
2. Valida cada registro con RegistroEntrada; los inválidos se separan con su error.
3. Predice solo los registros válidos con el pipeline (preprocesador + XGBoost).
4. Devuelve una predicción por registro, en el mismo orden de entrada.
"""

from functools import lru_cache
from importlib import resources

import pandas as pd
import skops.io as sio
from pydantic import ValidationError

from agropredict_model.config import ARCHIVO_MODELO, DIR_MODELOS, cargar_metadatos
from agropredict_model.schemas import RegistroEntrada


@lru_cache
def cargar_modelo():
    """Carga el pipeline (preprocesador + XGBoost) una sola vez por proceso.

    skops solo carga tipos que se declaran como confiables. Los de XGBoost
    (Booster y XGBRegressor) se guardaron en el .json desde el notebook 05.1.
    """
    tipos_confiables = cargar_metadatos()["tipos_skops_confiables"]

    # as_file entrega una ruta real en disco al archivo dentro del paquete instalado
    with resources.as_file(DIR_MODELOS / ARCHIVO_MODELO) as ruta:
        return sio.load(ruta, trusted=tipos_confiables)


def _a_registros(datos) -> list[dict]:
    """Unifica los formatos de entrada en una lista de diccionarios."""
    if isinstance(datos, pd.DataFrame):
        return datos.to_dict(orient="records")

    if isinstance(datos, dict):
        return [datos]

    return list(datos)


def make_prediction(datos) -> dict:
    """Valida y predice el rendimiento del maíz (t/ha).

    Parámetros
    ----------
    datos : dict, lista de dicts o DataFrame con las variables del modelo
        (semestre_b, rendimiento_rezago_1, rendimiento_rezago_2,
        departamento, sistema_productivo).

    Retorna
    -------
    dict con:
        predicciones   : una por registro, en el mismo orden; None si el registro es inválido
        unidad         : "t/ha"
        errores        : lista de {indice, detalle} para los registros inválidos
        modelo         : nombre del modelo en el Model Registry de MLflow
        version_modelo : versión registrada
    """
    metadatos = cargar_metadatos()
    variables = metadatos["variables"]
    registros = _a_registros(datos)

    # 1) Validación: se separan los registros válidos de los inválidos
    validos, indices_validos, errores = [], [], []

    for i, registro in enumerate(registros):
        try:
            # model_dump devuelve el registro ya normalizado (p. ej. "bolivar" -> "Bolívar")
            validos.append(RegistroEntrada(**registro).model_dump())
            indices_validos.append(i)
        except ValidationError as error:
            errores.append({
                "indice": i,
                "detalle": [e["msg"] for e in error.errors()],
            })

    # 2) Predicción: solo para los válidos; los inválidos quedan en None
    predicciones = [None] * len(registros)

    if validos:
        # Mismas columnas y en el mismo orden que en el entrenamiento
        entradas = pd.DataFrame(validos)[variables]
        estimaciones = cargar_modelo().predict(entradas)

        for i, valor in zip(indices_validos, estimaciones):
            # El rendimiento no puede ser negativo
            predicciones[i] = round(max(float(valor), 0.0), 4)

    return {
        "predicciones": predicciones,
        "unidad": "t/ha",
        "errores": errores,
        "modelo": metadatos["nombre_registry"],
        "version_modelo": metadatos["version_registry"],
    }