# Technická dokumentácia - PDF Kompresor

## 📋 Obsah
1. [Architektúra aplikácie](#architektúra-aplikácie)
2. [Ako funguje kompresia](#ako-funguje-kompresia)
3. [Správa aplikácie](#správa-aplikácie)
4. [Konfigurácia](#konfigurácia)
5. [Monitoring a logy](#monitoring-a-logy)
6. [Aktualizácia aplikácie](#aktualizácia-aplikácie)
7. [Riešenie problémov](#riešenie-problémov)
8. [Bezpečnosť](#bezpečnosť)

---

## Architektúra aplikácie

### Stack

```
Používateľ (prehliadač)
    ↓ HTTP
Nginx (port 80) - Reverse Proxy
    ↓ HTTP
Flask (port 5000) - Web aplikácia
    ↓
Docker kontajner
    ├─ Python 3.11
    ├─ Flask 3.0
    ├─ Poppler-utils
    ├─ pdf2image
    └─ Pillow + img2pdf
```

### Komponenty

| Komponent | Verzia | Účel |
|-----------|--------|------|
| **Python** | 3.11 | Runtime environment |
| **Flask** | 3.0+ | Web framework |
| **Nginx** | 1.18+ | Reverse proxy, HTTP server |
| **Docker** | 20.10+ | Containerization |
| **Poppler** | 22.02+ | PDF → Image konverzia |
| **pdf2image** | 1.16+ | Python binding pre Poppler |
| **Pillow** | 10.0+ | Image processing (JPEG kompresia) |
| **img2pdf** | 0.5+ | Image → PDF konverzia |

### Tok dát

#### Single File Upload
```
1. Upload PDF (max 600 MB)
   ↓
2. Uloženie do /app/uploads/
   ↓
3. Spracovanie (vlákno na pozadí):
   a) pdf2image: PDF → PNG obrázky (s nastaveným DPI)
   b) Pillow: Kompresia PNG → JPEG (s kvalitou)
   c) img2pdf: JPEG → PDF
   ↓
4. Uloženie do /app/compressed/
   ↓
5. Stiahnutie používateľom
   ↓
6. Cleanup (po 24h): Vymazanie dočasných súborov
```

#### Batch Upload (10-50 súborov)
```
1. Upload viacerých PDF súborov (každý max 600 MB)
   ↓
2. Vytvorenie batch_id pre celý batch
   ↓
3. Pre každý súbor:
   a) Vytvorenie job_id
   b) Uloženie do /app/uploads/
   c) Spustenie kompresie v samostatnom vlákne (paralelne)
   ↓
4. Sledovanie pokroku všetkých súborov cez /batch_progress/<batch_id>
   ↓
5. Uloženie komprimovaných súborov do /app/compressed/
   ↓
6. Zobrazenie výsledkov s možnosťou individuálneho stiahnutia
   ↓
7. Cleanup (po 24h): Vymazanie dočasných súborov
```

---

## Ako funguje kompresia

### Auto režim (dpi=0, quality=0)

```python
# Pseudo-kód
if dpi == 0:  # Auto režim
    dpi = 72  # Konzervatívne nízke DPI
    
if jpeg_quality == 0:  # Auto režim
    jpeg_quality = 60  # Agresívna kompresia
```

### Detaily algoritmu

1. **Konverzia PDF → Obrázky**
   ```python
   images = convert_from_path(pdf_path, dpi=72)  # Poppler
   ```
   - DPI určuje rozlíšenie výstupných obrázkov
   - Nižšie DPI = menší obrázok = menší súbor

2. **Kompresia obrázkov**
   ```python
   image.save(temp_file, 'JPEG', quality=60, optimize=True)
   ```
   - JPEG kvalita: 60 = agresívna kompresia
   - `optimize=True` = ďalšia optimalizácia

3. **Konverzia Obrázky → PDF**
   ```python
   pdf_bytes = img2pdf.convert(temp_jpeg_files)
   ```
   - img2pdf vytvára PDF bez ďalšej rekompresi

### Ochrana proti zväčšeniu

```python
if output_size > input_size:
    os.unlink(output_path)  # Vymazať väčší súbor
    return False, "⚠️ Kompresia by zväčšila súbor!"
```

Aplikácia automaticky detekuje, ak by výstupný súbor bol väčší ako vstupný, a vráti chybu.

---

## Správa aplikácie

### Štart/Stop/Reštart

```bash
# Zobraziť stav
sudo docker ps | grep pdf-compressor

# Zastaviť kontajner
sudo docker stop pdf-compressor-app

# Spustiť kontajner
sudo docker start pdf-compressor-app

# Reštartovať kontajner
sudo docker restart pdf-compressor-app

# Zobraziť logy
sudo docker logs pdf-compressor-app

# Live logy (sledovanie v reálnom čase)
sudo docker logs -f pdf-compressor-app
```

### Kontrola zdravia

```bash
# Health check endpoint
curl http://localhost:5000/health

# Odpoveď:
# {"status":"healthy","timestamp":"2025-11-06T10:23:53.008188"}
```

### Vymazanie dočasných súborov

Automaticky sa vymažú po 24 hodinách. Manuálne vymazanie:

```bash
# Spustiť cleanup manuálne
curl -X POST http://localhost:5000/cleanup

# Alebo priamo v kontajneri
sudo docker exec pdf-compressor-app rm -rf /app/uploads/* /app/compressed/*
```

---

## Konfigurácia

### Environment premenné

```bash
# SECRET_KEY - Flask secret key (32+ znakov)
-e SECRET_KEY=pdf-kompressor-secret-key-2024

# MAX_UPLOAD_SIZE - Max veľkosť uploadovaného súboru (v bajtoch)
-e MAX_UPLOAD_SIZE=629145600  # 600 MB

# CLEANUP_AGE - Vek súborov pred vymazaním (v hodinách)
-e CLEANUP_AGE=24  # 24 hodín
```

### Zmena konfigurácie

1. **Zastaviť kontajner**
   ```bash
   sudo docker stop pdf-compressor-app
   sudo docker rm pdf-compressor-app
   ```

2. **Spustiť s novými nastaveniami**
   ```bash
   sudo docker run -d \
     --name pdf-compressor-app \
     --restart unless-stopped \
     -p 5000:5000 \
     -e SECRET_KEY=novy-secret-key \
     -e MAX_UPLOAD_SIZE=629145600 \  # 600 MB
     -e CLEANUP_AGE=48 \  # 48 hodín
     pdf-compressor-app
   ```

### Nginx konfigurácia

**Súbor**: `/etc/nginx/sites-available/pdf-compressor`

```nginx
server {
    listen 80;
    server_name compress-pdf.novis.eu;

    client_max_body_size 600M;  # ← Pre batch upload

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Timeouts pre veľké batch uploady
        proxy_connect_timeout 1200;  # ← 20 minút
        proxy_send_timeout 1200;
        proxy_read_timeout 1200;
        send_timeout 1200;
    }
}
```

**Po zmene:**
```bash
sudo nginx -t  # Test syntax
sudo systemctl reload nginx  # Reload bez downtime
```

---

## Monitoring a logy

### Logy Flask aplikácie

```bash
# Živé logy (Ctrl+C pre ukončenie)
sudo docker logs -f pdf-compressor-app

# Posledných 100 riadkov
sudo docker logs --tail 100 pdf-compressor-app

# Logy za posledných 1 hodinu
sudo docker logs --since 1h pdf-compressor-app
```

### Logy Nginx

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

### Čo sledovať v logoch

**Normálne správy:**
```
[2025-11-06 10:23:53] INFO: Compress started: test.pdf
[2025-11-06 10:24:15] INFO: Compress completed: 10.5 MB → 3.2 MB (69.5%)
```

**Chyby:**
```
[2025-11-06 10:25:00] ERROR: Poppler nie je nainštalovaný
[2025-11-06 10:26:00] ERROR: Kompresia by zväčšila súbor: 1.21 MB → 9.59 MB
```

### Metriky systému

```bash
# Využitie Docker kontajnera
sudo docker stats pdf-compressor-app

# Využitie disku
df -h /app/uploads /app/compressed

# Počet súborov v adresároch
sudo docker exec pdf-compressor-app sh -c 'ls -1 /app/uploads | wc -l'
sudo docker exec pdf-compressor-app sh -c 'ls -1 /app/compressed | wc -l'
```

---

## Aktualizácia aplikácie

### Postup aktualizácie

1. **Pull nový kód z GitHub**
   ```bash
   cd /opt/pdf-compressor/compress-pdf
   sudo git pull origin main
   ```

2. **Zobraziť zmeny**
   ```bash
   git log --oneline -10  # Posledných 10 commitov
   git diff HEAD~1  # Zmeny v poslednom commite
   ```

3. **Zastaviť a vymazať starý kontajner**
   ```bash
   sudo docker stop pdf-compressor-app
   sudo docker rm pdf-compressor-app
   ```

4. **Rebuild Docker image**
   ```bash
   sudo docker build -t pdf-compressor-app .
   ```
   ⏱️ Trvanie: 2-5 minút

5. **Spustiť nový kontajner**
   ```bash
   sudo docker run -d \
     --name pdf-compressor-app \
     --restart unless-stopped \
     -p 5000:5000 \
     -e SECRET_KEY=pdf-kompressor-secret-key-2024 \
     -e MAX_UPLOAD_SIZE=209715200 \
     -e CLEANUP_AGE=24 \
     pdf-compressor-app
   ```

6. **Overiť funkčnosť**
   ```bash
   # Health check
   curl http://localhost:5000/health
   
   # Logy
   sudo docker logs pdf-compressor-app
   
   # Test v prehliadači
   # http://compress-pdf.novis.eu
   ```

### Rollback (ak niečo nefunguje)

```bash
# Vrátiť na predchádzajúcu verziu kódu
git log --oneline  # Nájsť hash predchádzajúceho commitu
git checkout <hash>

# Rebuild a spustiť
sudo docker build -t pdf-compressor-app .
sudo docker rm -f pdf-compressor-app
sudo docker run -d ... pdf-compressor-app
```

---

## Riešenie problémov

### Aplikácia nereaguje

```bash
# 1. Overiť, či kontajner beží
sudo docker ps | grep pdf-compressor

# 2. Ak nebeží, pozrieť sa na logy
sudo docker logs pdf-compressor-app

# 3. Reštartovať
sudo docker restart pdf-compressor-app

# 4. Ak nepomohlo, vymazať a spustiť znova
sudo docker rm -f pdf-compressor-app
sudo docker run -d ... pdf-compressor-app
```

### Nginx vracia 502 Bad Gateway

**Príčina**: Flask kontajner nebeží alebo nereaguje.

**Riešenie**:
```bash
# Overiť Flask
curl http://localhost:5000/health

# Ak nefunguje, reštartovať Flask
sudo docker restart pdf-compressor-app

# Overiť Nginx
sudo systemctl status nginx
sudo nginx -t
```

### Disk je plný

```bash
# 1. Skontrolovať využitie
df -h

# 2. Vymazať staré Docker images
sudo docker system prune -a

# 3. Vymazať dočasné súbory
sudo docker exec pdf-compressor-app rm -rf /app/uploads/* /app/compressed/*

# 4. Skrátiť cleanup age
# Reštartovať kontajner s -e CLEANUP_AGE=12 (12 hodín)
```

### Kompresia trvá príliš dlho

**Normálne**:
- 100 MB PDF: 2-5 minút
- 200 MB PDF: 5-10 minút

**Ak trvá dlhšie**:
1. Skontrolovať CPU/RAM: `docker stats pdf-compressor-app`
2. Pozrieť sa na logy: `docker logs pdf-compressor-app`
3. Zvýšiť timeouts v Nginx (>600s)

### Poppler not found (v kontajneri)

```bash
# Overiť inštaláciu v kontajneri
sudo docker exec pdf-compressor-app which pdftoppm

# Ak chýba, rebuild image (Poppler sa inštaluje v Dockerfile)
sudo docker build --no-cache -t pdf-compressor-app .
```

---

## Bezpečnosť

### Prístupové práva

```bash
# Kontajner beží ako non-root používateľ
# Súbory v kontajneri:
drwxr-xr-x  app:app  /app
drwxr-xr-x  app:app  /app/uploads
drwxr-xr-x  app:app  /app/compressed
```

### Sieťová izolácia

- Aplikácia je dostupná **len v internej sieti** (10.85.55.26)
- **Žiadne HTTPS** - vhodné len pre internú sieť
- Firewall by mal blokovať prístup z internetu

### Automatické čistenie

- Súbory sa **automaticky mažú po 24 hodinách**
- **Periodický cleanup** beží každých 6 hodín
- Zabezpečuje, že disk sa nezapchá

### Rate limiting (doporučené)

Pre obmedzenie počtu requestov pridajte do Nginx:

```nginx
limit_req_zone $binary_remote_addr zone=pdf_limit:10m rate=10r/m;

server {
    location / {
        limit_req zone=pdf_limit burst=5;
        proxy_pass http://localhost:5000;
    }
}
```

---

## Zálohovanie

### Čo zálohovať

1. **Kód aplikácie** (v Git - už je na GitHub)
2. **Nginx konfigurácia** (`/etc/nginx/sites-available/pdf-compressor`)
3. **Environment premenné** (dokumentované v tomto súbore)

### Čo NEzálohovať

- ❌ `/app/uploads` - dočasné súbory
- ❌ `/app/compressed` - dočasné súbory
- ❌ Docker image - dá sa rebuild z kódu

---

## Kontakt

**GitHub**: https://github.com/Abra7abra7/compress-pdf  
**Živá aplikácia**: http://compress-pdf.novis.eu

**Správa aplikácie**: IT tím Novis.eu

---

**Verzia dokumentácie**: 1.0  
**Posledná aktualizácia**: November 2025

