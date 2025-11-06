# PDF Kompresor

Aplikácia v Pythone na kompresiu PDF dokumentov zo skenov. Dostupná v **desktop (GUI)** aj **web verzii** s podporou hromadného spracovania PDF súborov.

## Výsledky kompresie

✅ **Overené výsledky**: 100 MB → 0.58 MB (99.4% zmenšenie)

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
- Jednoduchá údržba a aktualizácie

## Funkcie

- **Hromadné spracovanie** - Komprimuje všetky PDF súbory v adresári
- **Nastaviteľná kompresia** - Možnosť nastaviť DPI a JPEG kvalitu
- **Progress indikátor** - Zobrazenie pokroku pre každý súbor
- **Podrobný log** - Zobrazenie výsledkov kompresie
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

3. **Nainštalujte Poppler (automaticky)**
```bash
python install_poppler.py
```

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

### Požiadavky
- Linux server (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- Docker 20.10+
- Docker Compose 2.0+
- 2 GB RAM (minimum), 4 GB odporúčané
- 10 GB voľného diskového priestoru

### Rýchle spustenie

1. **Naklonujte projekt**
```bash
git clone <repository-url>
cd compress-pdf
```

2. **Spustite Docker Compose**
```bash
docker-compose up -d
```

3. **Otvorte v prehliadači**
```
http://vas-server-ip
```

### Konfigurácia

Upravte `docker-compose.yml` pre vlastné nastavenia:
- **MAX_UPLOAD_SIZE**: Maximálna veľkosť nahrávaného súboru (default: 200 MB)
- **CLEANUP_AGE**: Čas po ktorom sa vymažú staré súbory (default: 24 hodín)
- **PORT**: Port na ktorom beží aplikácia (default: 80)

### Produkčný deployment

Pozri `DEPLOYMENT.md` pre podrobné inštrukcie vrátane:
- SSL/HTTPS konfigurácie
- Firewall nastavení
- Backup stratégie
- Monitoring a logy
- Troubleshooting

---

## Odporúčané nastavenia

Pre skenované dokumenty (100 MB → 1-5 MB):
- **DPI**: 150
- **JPEG kvalita**: 75

Pre lepšiu kvalitu (väčšia veľkosť):
- **DPI**: 200
- **JPEG kvalita**: 85

Pre maximálnu kompresiu (menšia kvalita):
- **DPI**: 100
- **JPEG kvalita**: 60

## Ako to funguje

1. PDF súbory sa konvertujú na obrázky (PNG/JPEG)
2. Obrázky sa zmenšia na nastavené DPI
3. Obrázky sa komprimujú pomocou JPEG kompresie
4. Komprimované obrázky sa znovu spojia do PDF súboru

## Riešenie problémov

### Chyba: "poppler not found"
- Uistite sa, že Poppler je nainštalovaný a dostupný v PATH
- Na Windows použite poppler-windows z GitHubu

### Veľká veľkosť výstupného súboru
- Znížte DPI na 100-120
- Znížte JPEG kvalitu na 60-70

### Chyba pri konverzii PDF
- Skontrolujte, či sú PDF súbory nepoškodené
- Skúste otvoriť PDF v inej aplikácii

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



