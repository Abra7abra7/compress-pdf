#!/bin/bash
# Test script pre Docker build a spustenie

echo "============================================"
echo "PDF Kompresor - Docker test"
echo "============================================"
echo ""

# Kontrola Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker nie je nainštalovaný"
    echo "Návod: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker nájdený: $(docker --version)"

# Kontrola Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "ERROR: Docker Compose nie je nainštalovaný"
    exit 1
fi

echo "✓ Docker Compose nájdený"

# Vytvorenie adresárov
mkdir -p uploads compressed ssl

# Build
echo ""
echo "Building Docker image..."
docker compose build

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build zlyhal"
    exit 1
fi

echo "✓ Docker image úspešne vytvorený"

# Spustenie
echo ""
echo "Spúšťam kontajnery..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "ERROR: Spustenie kontajnerov zlyhalo"
    exit 1
fi

echo "✓ Kontajnery spustené"

# Počkanie na startup
echo ""
echo "Čakám na spustenie aplikácie..."
sleep 10

# Health check
echo "Kontrola health..."
HEALTH=$(curl -s http://localhost/health | grep -o "healthy")

if [ "$HEALTH" = "healthy" ]; then
    echo "✓ Aplikácia je funkčná"
else
    echo "⚠ WARNING: Health check zlyhal"
    docker compose logs
fi

# Výpis informácií
echo ""
echo "============================================"
echo "PDF Kompresor je spustený!"
echo "============================================"
echo ""
echo "URL: http://localhost"
echo ""
echo "Príkazy:"
echo "  docker compose logs -f     # Zobrazenie logu"
echo "  docker compose ps          # Stav kontajnerov"
echo "  docker compose stop        # Zastavenie"
echo "  docker compose down        # Zastavenie a vymazanie"
echo ""

