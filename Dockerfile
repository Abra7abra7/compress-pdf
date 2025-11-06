# PDF Kompresor - Docker Image
FROM python:3.11-slim

# Nastavenie working directory
WORKDIR /app

# Inštalácia systémových závislostí
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Kopírovanie requirements a inštalácia Python závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírovanie aplikácie
COPY app.py .
COPY pdf_compressor.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Vytvorenie adresárov pre uploads a compressed
RUN mkdir -p uploads compressed

# Environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expozícia portu
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# Spustenie aplikácie
CMD ["python", "app.py"]

