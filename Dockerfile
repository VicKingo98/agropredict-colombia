FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del dashboard
COPY requirements-dashboard.txt .
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copiar el dashboard y los datos necesarios
COPY dashboard/ ./dashboard/
COPY data/processed/features_rezago_1_2.parquet ./data/processed/
COPY data/geografica/municipios_dane_2025_plotly.geojson ./data/geografica/

# Puerto del dashboard
EXPOSE 8050

# Iniciar AgroPredict Colombia
CMD ["python", "dashboard/app.py"]
