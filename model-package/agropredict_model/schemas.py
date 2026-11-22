"""Validación de los registros de entrada del modelo.

Cada registro que llega a make_prediction se valida aquí antes de pasar al modelo:
- semestre_b debe ser 0 (A) o 1 (B), y los rezagos de rendimiento deben estar
  entre 0 y 60 t/ha (el máximo observado en la base EVA es 28 t/ha).
- Departamento y sistema productivo deben ser valores vistos en el entrenamiento.
  Se aceptan variantes sin tildes, en mayúsculas o con espacios extra, y se
  convierten al valor exacto del entrenamiento.
"""

import unicodedata
from functools import lru_cache

from pydantic import BaseModel, Field, field_validator

from agropredict_model.config import cargar_metadatos


def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes y sin espacios sobrantes, para comparar categorías.

    Ejemplo: "  BOLÍVAR ", "bolivar" y "Bolívar" -> "bolivar"
    """
    # NFKD separa la letra de su tilde ("í" -> "i" + "´") y el encode a ASCII
    # descarta la tilde
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

    # casefold: minúsculas; split/join: elimina espacios repetidos o en los extremos
    return " ".join(sin_tildes.casefold().split())


@lru_cache
def _categorias(campo: str) -> dict[str, str]:
    """Mapa {valor normalizado: valor original del entrenamiento}.

    Ejemplo para "departamentos": {"bolivar": "Bolívar", "valle del cauca": "Valle del Cauca", ...}
    Se calcula una sola vez por campo gracias a lru_cache.
    """
    valores = cargar_metadatos()[campo]
    return {_normalizar(v): v for v in valores}


def _validar_categoria(valor: str, campo: str, nombre: str) -> str:
    """Devuelve el valor tal como se usó en el entrenamiento o lanza un error.

    Es necesario porque el OneHotEncoder compara textos exactos: "Bolivar" sin tilde
    no coincide con la columna "Bolívar", y con handle_unknown="ignore" el modelo
    lo codificaría como todo ceros sin avisar, generando una predicción incorrecta.
    """
    canonico = _categorias(campo).get(_normalizar(valor))

    if canonico is None:
        permitidos = ", ".join(sorted(_categorias(campo).values()))
        raise ValueError(f"{nombre} '{valor}' no fue visto en el entrenamiento. Valores válidos: {permitidos}")

    return canonico


class RegistroEntrada(BaseModel):
    """Un municipio-semestre a predecir, con las mismas variables del entrenamiento."""

    # Semestre de la predicción: solo admite 0 (A) o 1 (B)
    semestre_b: int = Field(ge=0, le=1, description="0 = semestre A, 1 = semestre B")

    # Rezagos de rendimiento en t/ha. El máximo observado en la base EVA es 28 t/ha;
    # el límite de 60 deja margen y bloquea valores claramente erróneos
    rendimiento_rezago_1: float = Field(ge=0, le=60, description="Rendimiento del semestre anterior (t/ha)")
    rendimiento_rezago_2: float = Field(ge=0, le=60, description="Rendimiento del mismo semestre del año anterior (t/ha)")

    # Variables categóricas: se validan contra los valores del entrenamiento
    departamento: str = Field(min_length=1)
    sistema_productivo: str = Field(min_length=1)

    # Los field_validator se ejecutan después de validar el tipo (str).
    # El valor que devuelven es el que queda guardado en el registro.
    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        return _validar_categoria(valor, "departamentos", "Departamento")

    @field_validator("sistema_productivo")
    @classmethod
    def validar_sistema(cls, valor: str) -> str:
        return _validar_categoria(valor, "sistemas_productivos", "Sistema productivo")