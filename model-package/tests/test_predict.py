"""Pruebas del paquete agropredict_model.

Se ejecutan sobre el paquete instalado (wheel), así se verifica también que el
.skops y el .json quedaron incluidos dentro del paquete.

    pytest model-package/tests -v
"""

import pandas as pd
import pytest

from agropredict_model import __version__, cargar_metadatos, cargar_modelo, make_prediction

META = cargar_metadatos()

# Registro válido de referencia, armado con valores que existen en el entrenamiento
REGISTRO = {
    "semestre_b": 0,
    "rendimiento_rezago_1": 2.5,
    "rendimiento_rezago_2": 2.3,
    "departamento": META["departamentos"][0],
    "sistema_productivo": META["sistemas_productivos"][0],
}


def test_metadatos_y_version():
    """El .json viene en el paquete y las variables son las del entrenamiento."""
    assert META["variables"] == [
        "semestre_b", "rendimiento_rezago_1", "rendimiento_rezago_2",
        "departamento", "sistema_productivo",
    ]
    assert __version__ != "0.0.0-dev", "El paquete no está instalado"


def test_modelo_carga():
    """El .skops viene en el paquete y carga con los tipos confiables."""
    assert hasattr(cargar_modelo(), "predict")


def test_prediccion_individual():
    """Un registro válido produce una predicción no negativa y sin errores."""
    resultado = make_prediction(REGISTRO)

    assert resultado["errores"] == []
    assert len(resultado["predicciones"]) == 1
    assert resultado["predicciones"][0] >= 0
    assert resultado["unidad"] == "t/ha"
    assert resultado["version_modelo"] == META["version_registry"]


def test_prediccion_lote_y_dataframe():
    """Lista de dicts y DataFrame dan el mismo resultado y conservan el orden."""
    lote = [REGISTRO, {**REGISTRO, "semestre_b": 1}]

    por_lista = make_prediction(lote)["predicciones"]
    por_df = make_prediction(pd.DataFrame(lote))["predicciones"]

    assert por_lista == por_df
    assert len(por_lista) == 2


def test_categorias_sin_tildes_ni_mayusculas():
    """Variantes de escritura del departamento dan la misma predicción que el valor original."""
    original = make_prediction(REGISTRO)["predicciones"][0]
    variante = {**REGISTRO, "departamento": f"  {REGISTRO['departamento'].upper()} "}

    assert make_prediction(variante)["predicciones"][0] == original


def test_departamento_desconocido_no_afecta_al_lote():
    """Un registro inválido queda en None con su error; los demás se predicen igual."""
    resultado = make_prediction([REGISTRO, {**REGISTRO, "departamento": "Narnia"}])

    assert resultado["predicciones"][0] is not None
    assert resultado["predicciones"][1] is None
    assert resultado["errores"][0]["indice"] == 1


# Se repite la misma prueba para cada valor inválido
@pytest.mark.parametrize("campo, valor", [
    ("semestre_b", 2),                       # solo 0 o 1
    ("rendimiento_rezago_1", -1),            # no puede ser negativo
    ("rendimiento_rezago_2", 100),           # sobre el límite de 60 t/ha
    ("sistema_productivo", "hidropónico"),   # no existe en el entrenamiento
])
def test_valores_invalidos(campo, valor):
    resultado = make_prediction({**REGISTRO, campo: valor})

    assert resultado["predicciones"] == [None]
    assert len(resultado["errores"]) == 1