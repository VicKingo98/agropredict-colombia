FROM python:3.13-slim

# Dependencia del sistema requerida por XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements-dashboard.txt .
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copiar el dashboard y los recursos necesarios
COPY dashboard/ ./dashboard/
COPY models/xgboost_maiz_t1_t2.skops ./models/
COPY data/processed/features_rezago_1_2.parquet ./data/processed/
COPY data/geografica/municipios_dane_2025_plotly.geojson ./data/geografica/

# Puerto del dashboard
EXPOSE 8050

# Iniciar AgroPredict Colombia
CMD ["python", "dashboard/app.py"]
