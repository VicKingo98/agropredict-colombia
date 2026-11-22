# agropredict-model

Paquete del modelo XGBoost que estima el rendimiento municipal del maíz (t/ha).
Corresponde a `agropredict-maiz-xgb@champion` del Model Registry de MLflow
(experimento `agropredict-maiz-rezagos-t1-t2`, notebook `05.1_optimizacion_modelos`).

## Variables de entrada

| Variable | Descripción | Valores |
|---|---|---|
| `semestre_b` | Semestre de la predicción | 0 = A, 1 = B |
| `rendimiento_rezago_1` | Rendimiento del semestre anterior | 0 a 60 t/ha |
| `rendimiento_rezago_2` | Rendimiento del mismo semestre del año anterior | 0 a 60 t/ha |
| `departamento` | Departamento | Los 31 del entrenamiento; acepta variantes sin tildes o en mayúsculas |
| `sistema_productivo` | Sistema productivo | `tradicional` o `tecnificado` |

## Construcción

Desde la raíz del repositorio:

```bash
dvc pull
pip install build
bash model-package/build.sh
```

Genera `model-package/dist/agropredict_model-1.0.0-py3-none-any.whl`, con el modelo
(`.skops`) y sus metadatos (`.json`) incluidos.

## Uso

```python
from agropredict_model import make_prediction

make_prediction({
    "semestre_b": 0,
    "rendimiento_rezago_1": 2.5,
    "rendimiento_rezago_2": 2.3,
    "departamento": "Tolima",
    "sistema_productivo": "tecnificado",
})
# {'predicciones': [...], 'unidad': 't/ha', 'errores': [],
#  'modelo': 'agropredict-maiz-xgb', 'version_modelo': 1}
```

`make_prediction` acepta un dict, una lista de dicts o un DataFrame. Los registros
inválidos quedan con predicción `None` y su detalle en `errores`, sin afectar al resto.

## Pruebas

```bash
pip install "model-package/dist/agropredict_model-1.0.0-py3-none-any.whl[test]"
pytest model-package/tests -v
```