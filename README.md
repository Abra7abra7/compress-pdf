# PDF Kompresor

Aplikácia v Pythone na kompresiu PDF dokumentov zo skenov. Dostupná v **desktop (GUI)** aj **web verzii** s podporou hromadného spracovania PDF súborov.

## Výsledky kompresie

✅ **Overené výsledky** (s Auto režimom):
- **Test 1**: 100 MB → 0.58 MB (99.4% zmenšenie)
- **Test 2**: 10.58 MB → 3.02 MB (71.5% zmenšenie)
- **Test 3**: 5.58 MB → 1.34 MB (76.0% zmenšenie)

**Ochrana**: Aplikácia automaticky zabráni zväčšeniu súborov - ak by kompresia zväčšila PDF, dostanete upozornenie.

Ideálne pre:
- Skenované dokumenty
- Veľké PDF súbory z tladiarne
- Dokumenty s obrázkami
- Archiváciu súborov

## Verzie

### Desktop GUI (Windows)
- Jednoduché GUI rozhranie s drag & drop
- Lokálne spracovanie na vašom počítači
- Žiadne nahrávanie súborov na internet

### Web aplikácia (Docker)
- Prístup cez webový prehliadač (URL)
- Centralizovaný deployment pre firmy/tímy
- Podpora 10-100 simultánnych používateľov
- **Hromadné spracovanie: 10-50 PDF súborov naraz**
- **Maximum 600 MB na súbor**
- Jednoduchá údržba a aktualizácie

## Funkcie

- **📦 Batch Upload** - Nahrajte 10-50 PDF súborov naraz
- **🤖 Auto režim** - Automatická optimalizácia DPI a kvality (odporúčané)
- **🛡️ Ochrana proti zväčšeniu** - Zabráni nechcenému zväčšeniu už komprimovaných PDF
- **Hromadné spracovanie** - Komprimuje všetky PDF súbory súčasne
- **💪 Veľké súbory** - Podpora súborov až do 600 MB
- **Nastaviteľná kompresia** - Manuálne nastavenie DPI (100-200) a JPEG kvality (60-95)
- **Progress indikátor** - Zobrazenie pokroku pre každý súbor samostatne
- **Podrobný log** - Zobrazenie výsledkov kompresie s možnosťou stiahnutia každého súboru
- **Automatická detekcia Poppler** - Lokálna aj systémová inštalácia

---

## 🖥️ Desktop GUI Verzia (Windows)

### Požiadavky
- Python 3.7 alebo novší
- Windows 10/11

### Rýchla inštalácia

1. **Naklonujte projekt**
```bash
git clone <repository-url>
cd compress-pdf
```

2. **Nainštalujte Python závislosti**
```bash
pip install -r requirements.txt
```

3. **Nainštalujte Poppler**

Pozrite si `INSTALACIA_POPPLER.md` pre podrobné inštrukcie.

### Použitie

```bash
python main.py
```

1. Vyberte vstupný adresár obsahujúci PDF súbory
2. (Voliteľné) Vyberte výstupný adresár
3. Nastavte DPI (100-200) a JPEG kvalitu (60-95)
4. Kliknite na "Komprimovať PDF súbory"
5. Po dokončení kliknite na "Otvoriť výstupný adresár"

---

## 🌐 Web Verzia (Docker Deployment)

**Živá demo**: https://compress-pdf.novis.eu (interná sieť Novis.eu)

### Požiadavky
- Linux server (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- Docker 20.10+
- Nginx (pre reverse proxy)
- 4 GB RAM (minimum), 8 GB odporúčané pre batch processing
- 20 GB voľného diskového priestoru

### Rýchle spustenie

1. **Naklonujte projekt**
```bash
git clone https://github.com/Abra7abra7/compress-pdf.git
cd compress-pdf
```

2. **Buildnite Docker image**
```bash
sudo docker build -t pdf-compressor-app .
```

3. **Spustite kontajner**
```bash
sudo docker run -d \
  --name pdf-compressor-app \
  --restart unless-stopped \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e MAX_UPLOAD_SIZE=209715200 \
  -e CLEANUP_AGE=24 \
  pdf-compressor-app
```

4. **Otvorte v prehliadači**
```
http://vas-server-ip:5000
```

Pre produkčné nasadenie s Nginx a vlastnou doménou, pozri `DEPLOYMENT.md`.

### Konfigurácia

Vytvorte `.env` súbor (skopírujte z `.env.example`):
```bash
cp .env.example .env
nano .env
```

Dostupné nastavenia:
- **SECRET_KEY**: Flask secret key (použite silné heslo!)
- **MAX_UPLOAD_SIZE**: Maximálna veľkosť nahrávaného súboru (default: 600 MB)
- **CLEANUP_AGE**: Čas po ktorom sa vymažú staré súbory (default: 24 hodín)

### Produkčný deployment

Pozri `DEPLOYMENT.md` pre podrobné inštrukcie vrátane:
- SSL/HTTPS konfigurácie
- Firewall nastavení
- Backup stratégie
- Monitoring a logy
- Troubleshooting

---

## Odporúčané nastavenia

### 🤖 Auto režim (Odporúčané)
- Zapnite checkbox "Automatická optimalizácia"
- Aplikácia sama vyberie optimálne DPI a kvalitu
- Nikdy nezvýši rozlíšenie (zabráni zväčšeniu súboru)

### Manuálne nastavenia

Pre skenované dokumenty (veľká kompresia):
- **DPI**: 72-100
- **JPEG kvalita**: 60-75

Pre lepšiu kvalitu (stredná kompresia):
- **DPI**: 100-150
- **JPEG kvalita**: 75-85

Pre vysokú kvalitu (minimálna kompresia):
- **DPI**: 150-200
- **JPEG kvalita**: 85-95

## Ako to funguje

1. PDF súbory sa konvertujú na obrázky (PNG/JPEG)
2. Obrázky sa zmenšia na nastavené DPI
3. Obrázky sa komprimujú pomocou JPEG kompresie
4. Komprimované obrázky sa znovu spojia do PDF súboru

## Riešenie problémov

### ⚠️ Kompresia zväčšila súbor
**Príčina**: PDF je už optimálne komprimovaný alebo má veľmi nízke DPI.

**Riešenie**:
- Aplikácia automaticky zobrazí chybu a neprepíše originál
- Použite originálny súbor (už je dobre komprimovaný)
- Alebo skúste manuálne nastavenia s nižším DPI

### Chyba: "poppler not found"
**Riešenie**:
- Desktop: Spustite `python install_poppler.py`
- Linux server: `sudo apt install poppler-utils`
- Alebo pozrite `INSTALACIA_POPPLER.md`

### Veľké súbory trvajú dlho
**Normálne**:
- 100 MB PDF môže trvať 2-5 minút
- Progress indikátor zobrazuje pokrok
- Počkajte, kým sa kompresia dokončí

### Blokované sťahovanie v Chrome
**Príčina**: HTTP namiesto HTTPS.

**Riešenie**:
- Kliknite na "Ponechať nebezpečný súbor"
- Alebo použite Firefox (menej prísny)
- Pre produkciu nastavte HTTPS (pozri DEPLOYMENT.md)

### Chyba pri konverzii PDF
**Riešenie**:
- Skontrolujte, či nie je PDF chránený heslom
- Skúste otvoriť PDF v inom programe
- Overte, že súbor nie je poškodený

## Porovnanie verzií

| Funkcia | Desktop GUI | Web Aplikácia |
|---------|-------------|---------------|
| **Inštalácia** | Jednoduchá (Python + Poppler) | Docker |
| **Prístup** | Lokálny počítač | URL v prehliadači |
| **Používatelia** | 1 | 10-100+ |
| **Údržba** | Každý používateľ samostatne | Centralizovaná |
| **Bezpečnosť** | Offline, lokálne súbory | HTTPS, autentifikácia |
| **Aktualizácie** | Manuálne na každom PC | Jeden deployment |

## Deployment dokumentácia

- **Desktop GUI**: Pozri `INSTALACIA_POPPLER.md`
- **Web aplikácia**: Pozri `DEPLOYMENT.md`
- **Docker image**: Automatický build cez `docker-compose`

## Podpora

Pre problémy alebo otázky:
1. Skontrolujte sekciu "Riešenie problémov" nižšie
2. Pozrite deployment dokumentáciu
3. Vytvorte issue v repozitári

## Licencia

Tento projekt je poskytovaný "ako je" bez záruky.



