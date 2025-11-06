# Inštalácia Poppler pre Windows

Poppler je potrebný pre konverziu PDF súborov na obrázky. Bez neho aplikácia nebude fungovať.

## Metóda 1: Inštalácia cez PATH (Odporúčané)

### Krok 1: Stiahnutie Poppler
1. Prejdite na: https://github.com/oschwartz10612/poppler-windows/releases/
2. Stiahnite najnovšiu verziu (napr. `Release-23.11.0-0.zip`)
3. Rozbalte ZIP súbor do ľubovoľného adresára (napr. `C:\poppler`)

### Krok 2: Pridanie do PATH
1. Otvorte **Premenné prostredia** (Environment Variables):
   - Stlačte `Win + R`
   - Napíšte `sysdm.cpl` a stlačte Enter
   - Kliknite na záložku **Rozšírené** (Advanced)
   - Kliknite na **Premenné prostredia** (Environment Variables)

2. V sekcii **Systémové premenné** (System variables) nájdite `Path` a kliknite **Upraviť** (Edit)

3. Kliknite **Nový** (New) a pridajte cestu k `bin` adresáru Poppler:
   - Napr: `C:\poppler\Library\bin`
   - Alebo: `C:\poppler\poppler-23.11.0\Library\bin`
   - Presná cesta závisí od toho, kde ste rozbalili ZIP

4. Kliknite **OK** na všetkých oknách

5. **Dôležité**: Reštartujte aplikáciu PDF Kompresor (alebo celý terminál/IDE)

### Krok 3: Overenie
Otvorte PowerShell alebo Command Prompt a spustite:
```bash
pdftoppm -h
```

Ak sa zobrazí pomoc, Poppler je nainštalovaný správne.

## Metóda 2: Lokálna inštalácia (Bez PATH)

Ak nechcete meniť systémové premenné, môžete umiestniť Poppler priamo do projektu:

1. Stiahnite Poppler (rovnako ako v Metóde 1)
2. Rozbalte ho do adresára projektu: `compress-pdf\poppler`
3. Upravte kód v `pdf_compressor.py` - pridajte cestu k poppler pred `convert_from_path`:

```python
from pdf2image import convert_from_path

# Pridajte túto časť pred použitím convert_from_path
POPPLER_PATH = r"C:\cesta\k\projektu\compress-pdf\poppler\Library\bin"
images = convert_from_path(input_path, dpi=dpi, poppler_path=POPPLER_PATH)
```

## Riešenie problémov

### "pdftoppm nie je rozpoznaný ako príkaz"
- Skontrolujte, či ste správne pridali cestu do PATH
- Reštartujte terminál/IDE po zmene PATH
- Skontrolujte, či cesta v PATH obsahuje `bin` adresár

### "Unable to get page count"
- Poppler nie je správne nainštalovaný
- Skúste Metódu 2 (lokálna inštalácia)
- Skontrolujte, či súbor `pdftoppm.exe` existuje v `bin` adresári

### Iné problémy
- Skúste stiahnuť inú verziu Poppler
- Skontrolujte, či máte správne oprávnenia na čítanie/zápis súborov

## Alternatívne riešenie

Ak máte problémy s inštaláciou Poppler, môžete použiť online služby alebo iné nástroje na kompresiu PDF, ale táto aplikácia vyžaduje Poppler.

