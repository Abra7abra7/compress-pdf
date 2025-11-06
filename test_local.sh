#!/bin/bash
# Test script pre lokálne spustenie Flask aplikácie bez Dockeru

echo "============================================"
echo "PDF Kompresor - Lokálny test"
echo "============================================"
echo ""

# Kontrola Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 nie je nainštalovaný"
    exit 1
fi

echo "✓ Python3 nájdený: $(python3 --version)"

# Kontrola pip
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 nie je nainštalovaný"
    exit 1
fi

echo "✓ pip3 nájdený"

# Inštalácia závislostí
echo ""
echo "Inštalácia Python závislostí..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "ERROR: Chyba pri inštalácii závislostí"
    exit 1
fi

echo "✓ Závislosti nainštalované"

# Kontrola Poppler
echo ""
echo "Kontrola Poppler..."
if command -v pdftoppm &> /dev/null; then
    echo "✓ Poppler je nainštalovaný"
else
    echo "⚠ WARNING: Poppler nie je nainštalovaný!"
    echo "  Pre Linux: sudo apt-get install poppler-utils"
    echo "  Pre macOS: brew install poppler"
fi

# Vytvorenie adresárov
mkdir -p uploads compressed
echo "✓ Adresáre vytvorené"

# Spustenie Flask aplikácie
echo ""
echo "============================================"
echo "Spúšťam Flask aplikáciu..."
echo "Otvorte prehliadač na: http://localhost:5000"
echo "Stlačte Ctrl+C pre ukončenie"
echo "============================================"
echo ""

export FLASK_APP=app.py
export FLASK_ENV=development
python3 app.py

