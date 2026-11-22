#!/usr/bin/env bash
# Construye el wheel del paquete con el modelo vigente de models/.
# Requisitos: haber ejecutado `dvc pull` y tener instalado `build` (pip install build).
#
# Uso (desde cualquier carpeta):
#   bash model-package/build.sh

# Detener el script ante cualquier error, variable no definida o fallo en un pipe
set -euo pipefail

# Moverse a la carpeta del script (model-package/), sin importar desde dónde se ejecute
cd "$(dirname "$0")"

ORIGEN=../models
DESTINO=agropredict_model/trained_models

# 1) Copiar el modelo y sus metadatos al paquete
for archivo in xgboost_maiz_t1_t2.skops xgboost_maiz_t1_t2.json; do
    if [[ ! -f "$ORIGEN/$archivo" ]]; then
        echo "Falta $ORIGEN/$archivo (ejecutar dvc pull)" >&2
        exit 1
    fi
    cp "$ORIGEN/$archivo" "$DESTINO/"
    echo "Copiado: $archivo"
done

# 2) Limpiar construcciones anteriores
rm -rf build dist ./*.egg-info

# 3) Construir el wheel en dist/
python -m build --wheel

echo
ls -lh dist/