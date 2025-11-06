# PDF Kompresor - Rýchly štart

## Pre Linux server (Produkčné prostredie)

```bash
# 1. Klonujte projekt
git clone <repository-url> pdf-compressor
cd pdf-compressor

# 2. Vytvorte .env súbor
cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
MAX_UPLOAD_SIZE=209715200
CLEANUP_AGE=24
EOF

# 3. Spustite Docker
docker compose up -d

# 4. Otvorte v prehliadači
# http://your-server-ip
```

## Pre lokálne testovanie (bez Dockeru)

```bash
# 1. Nainštalujte závislosti
pip install -r requirements.txt

# 2. Spustite aplikáciu
python app.py

# 3. Otvorte prehliadač
# http://localhost:5000
```

## Prvé kroky po spustení

1. Otvorte webové rozhranie
2. Vyberte alebo pretiahnite PDF súbor (max 200 MB)
3. Nastavte DPI a kvalitu (default: 150 DPI, 75 kvalita)
4. Kliknite na tlačidlo pre kompresiu
5. Počkajte na dokončenie a stiahnite výsledok

## Často používané príkazy

```bash
# Zobrazenie logu
docker compose logs -f

# Reštart aplikácie
docker compose restart

# Zastavenie
docker compose down

# Aktualizácia
git pull && docker compose up -d --build

# Vyčistenie starých súborov
find uploads -type f -mtime +1 -delete
find compressed -type f -mtime +1 -delete
```

## Riešenie problémov

**Aplikácia sa nespustí**
```bash
docker compose logs app
```

**Port 80 je obsadený**
```bash
# V docker-compose.yml zmeňte port
ports:
  - "8080:80"
```

**Poppler nie je nainštalovaný (lokálne)**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

## Podrobná dokumentácia

- **Desktop GUI**: Pozri `README.md` sekcia Desktop GUI
- **Web deployment**: Pozri `DEPLOYMENT.md`
- **Inštalácia Poppler**: Pozri `INSTALACIA_POPPLER.md`

