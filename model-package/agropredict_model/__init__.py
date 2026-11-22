"""Paquete del modelo de rendimiento municipal del maíz (AgroPredict Colombia).

Expone lo necesario para usar el modelo desde la API u otros servicios:

    from agropredict_model import make_prediction, cargar_metadatos, __version__
"""

from importlib.metadata import PackageNotFoundError, version

from agropredict_model.config import cargar_metadatos
from agropredict_model.predict import cargar_modelo, make_prediction

# Versión del paquete instalado, tomada de pyproject.toml (1.0.0).
# Si se ejecuta desde el código fuente sin instalar, no hay metadatos y se usa
# una versión de desarrollo.
try:
    __version__ = version("agropredict-model")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Lo que se importa con "from agropredict_model import *"
__all__ = ["__version__", "cargar_metadatos", "cargar_modelo", "make_prediction"]