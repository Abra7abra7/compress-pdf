# Užívateľská príručka - PDF Kompresor

## 📋 Obsah
1. [Prístup k aplikácii](#prístup-k-aplikácii)
2. [Ako komprimovať PDF](#ako-komprimovať-pdf)
3. [Auto režim vs Manuálny režim](#auto-režim-vs-manuálny-režim)
4. [Čo robiť, keď sa súbor zväčší](#čo-robiť-keď-sa-súbor-zväčší)
5. [Často kladené otázky](#často-kladené-otázky)
6. [Limity a obmedzenia](#limity-a-obmedzenia)

---

## Prístup k aplikácii

**Webová adresa**: http://compress-pdf.novis.eu

Aplikácia je dostupná z **firemnej siete Novis.eu** cez akýkoľvek webový prehliadač:
- ✅ Google Chrome
- ✅ Mozilla Firefox
- ✅ Microsoft Edge
- ✅ Safari

**Žiadne prihlásenie nie je potrebné** - stačí otvoriť URL a môžete začať.

---

## Ako komprimovať PDF

### Krok za krokom

#### 1. **Nahrajte PDF súbor**

Máte 3 možnosti:

**A) Drag & Drop** (najjednoduchšie)
- Potiahnte PDF súbor z vášho počítača
- Pustite ho na šedú plochu s nápisom "Nahrajte PDF súbor"

**B) Kliknutím**
- Kliknite na tlačidlo "Vybrať súbor"
- V okne vyberte PDF súbor z vášho počítača

**C) Priamo z priečinka**
- Kliknite pravým na PDF súbor
- Vyberte "Otvoriť pomocou" → Váš prehliadač

#### 2. **Počkajte na spracovanie**

- Uvidíte progress bar (modrý prúžok)
- Zobrazí sa "Spracovanie súboru"
- **Nebudete vidieť percentá**, ale súbor sa spracováva na pozadí

**Ako dlho to trvá?**
- Malý súbor (1-10 MB): 10-30 sekúnd
- Stredný súbor (10-50 MB): 30-120 sekúnd  
- Veľký súbor (50-200 MB): 2-5 minút

💡 **Tip**: Počkajte trpezlivo - nezatvárajte okno prehliadača!

#### 3. **Stiahnite skomprimovaný súbor**

Po dokončení uvidíte:
- ✅ Zelená fajka "Kompresia dokončená!"
- **Pôvodná veľkosť**: napr. 10.58 MB
- **Komprimovaná veľkosť**: napr. 3.02 MB
- **Zmenšenie**: napr. 71.4%

Kliknite na zelené tlačidlo **"Stiahnuť komprimovaný PDF"**.

#### 4. **Komprimujte ďalší súbor**

Kliknite na "Komprimovať ďalší súbor" a opakujte proces.

---

## Auto režim vs Manuálny režim

### 🤖 Auto režim (ODPORÚČANÉ)

**Čo to je?**
- Aplikácia **automaticky vyberie** najlepšie nastavenia
- Checkbox "Automatická optimalizácia" je **predvolene zapnutý**

**Výhody:**
- ✅ Nemusíte rozumieť technickým parametrom
- ✅ **Nikdy nezvýši** rozlíšenie (zabráni zväčšeniu súboru)
- ✅ Optimálna rovnováha medzi kvalitou a veľkosťou
- ✅ Funguje pre 95% prípadov

**Kedy použiť:** Vždy, ak si nie ste istí.

---

### ⚙️ Manuálny režim (Pokročilí)

**Kedy použiť:**
- Potrebujete **vyššiu kvalitu** (väčší súbor)
- Potrebujete **maximálnu kompresiu** (menšia kvalita)
- Auto režim vám nevyhovuje

**Ako zapnúť:**
1. Odškrtnite checkbox "🤖 Automatická optimalizácia"
2. Slidery **DPI** a **JPEG Kvalita** sa aktivujú

**Parametre:**

#### **DPI (Rozlíšenie)**
- Rozsah: 100 - 200
- **Nižšie = menší súbor, horšia kvalita**
- **Vyššie = väčší súbor, lepšia kvalita**

**Odporúčané hodnoty:**
- **100**: Maximálna kompresia (na čítanie na obrazovke)
- **150**: Stredná kompresia (tlač A4)
- **200**: Minimálna kompresia (profesionálna tlač)

#### **JPEG Kvalita**
- Rozsah: 60 - 95
- **Nižšie = menší súbor, viac artefaktov**
- **Vyššie = väčší súbor, čistejší obraz**

**Odporúčané hodnoty:**
- **60**: Maximálna kompresia
- **75**: Stredná kompresia (default)
- **85-95**: Vysoká kvalita

---

## Čo robiť, keď sa súbor zväčší

### ⚠️ Červená chybová hláška

Niekedy uvidíte chybu:

```
⚠️ Kompresia by zväčšila súbor! 
Originál: 1.21 MB, Po kompresii: 9.59 MB.
Tento PDF je už pravdepodobne dobre komprimovaný.
Použite originálny súbor.
```

### Prečo sa to stalo?

**Príčina:**
- Váš PDF je **už optimálne komprimovaný**
- Má veľmi nízke rozlíšenie (napr. 50-72 DPI)
- Ďalšia kompresia by ho **zväčšila**, nie zmenšila

### Čo urobiť?

✅ **Použite originálny súbor** - je už dostatočne malý
✅ **Nekomprimujte ho znova** - aplikácia vás chráni pred zväčšením

💡 **Tip**: Ak je PDF napr. 1 MB, už je to malé - kompresia nie je potrebná.

---

## Často kladené otázky

### 1. **Môžem komprimovať viacero súborov naraz?**

❌ **Nie** - web aplikácia podporuje **jeden súbor naraz**.

**Riešenie**: Komprimujte ich postupne, každý samostatne.

---

### 2. **Kde sa ukladajú moje súbory?**

- Súbory sa **dočasne** uložia na server pri nahratí
- Po **24 hodinách** sa automaticky **vymažú**
- **Stiahnutý** súbor je **len na vašom počítači**

🔒 **Bezpečnosť**: Súbory sú dostupné len vo firemnej sieti.

---

### 3. **Prečo mi Chrome blokuje stiahnutie?**

**Dôvod**: Aplikácia beží na HTTP (nie HTTPS).

**Riešenie**:
1. Kliknite na tlačidlo stiahnutia v Chrome
2. Vyberte "**Ponechať nebezpečný súbor**"
3. Alebo použite **Firefox** (menej prísny)

💡 **Tip**: Súbor je bezpečný - ide len o firemné PDF.

---

### 4. **Stratím kvalitu po kompresii?**

**Závisí od nastavení:**
- **Auto režim**: Optimálna rovnováha - neviditeľný rozdiel pre bežné použitie
- **Manuálny režim s DPI 100 a kvalitou 60**: Viditeľné zhoršenie pri približovaní
- **Manuálny režim s DPI 150 a kvalitou 85**: Minimálny rozdiel

📊 **Odporúčanie**: Najprv vyskúšajte Auto režim. Ak kvalita nevyhovuje, skúste manuálne nastavenia.

---

### 5. **Podporuje aplikácia PDF s heslom?**

❌ **Nie** - PDF chránené heslom nemožno komprimovať.

**Riešenie**:
1. Odstráňte heslo z PDF
2. Potom ho skomprimujte

---

### 6. **Čo keď kompresia trvá príliš dlho?**

**Normálne časy:**
- 100 MB PDF: **2-5 minút**
- 200 MB PDF: **5-10 minút**

**Ak trvá dlhšie ako 10 minút:**
1. **Obnovte stránku** (F5)
2. **Skúste znova** s menším súborom
3. **Kontaktujte IT podporu**

---

### 7. **Môžem komprimovať aj iné formáty (Word, Excel)?**

❌ **Nie** - aplikácia podporuje **len PDF súbory**.

**Riešenie**:
1. Preveďte Word/Excel na PDF
2. Potom ho skomprimujte

---

## Limity a obmedzenia

### Maximálna veľkosť súboru
- **200 MB** - väčšie súbory nebudú prijaté

### Podporované formáty
- ✅ **PDF** (.pdf)
- ❌ **Word** (.doc, .docx)
- ❌ **Excel** (.xls, .xlsx)
- ❌ **Obrázky** (.jpg, .png)

### Čas spracovania
- **Maximum**: 10 minút na súbor
- Po 10 minútach sa spracovanie preruší

### Počet súborov
- **1 súbor naraz** (nie batch)

---

## 💬 Kontakt a podpora

Ak máte problémy alebo otázky:

1. **Prečítajte si FAQ** vyššie
2. **Skontrolujte troubleshooting** v `README.md`
3. **Kontaktujte IT podporu** s popisom problému

---

## 📝 Tipy a triky

### ✅ Najlepšie postupy

1. **Používajte Auto režim** - je optimalizovaný pre väčšinu prípadov
2. **Neprekomprimujte** - ak je PDF malé (< 5 MB), nech je
3. **Skontrolujte výsledok** - otvorte PDF a overte kvalitu
4. **Uložte originál** - pre prípad, že kompresia nevyhovuje

### ⚠️ Čomu sa vyhnúť

1. **Nekomprimujte už skomprimované PDF** - dostanete chybu
2. **Nezatvárajte okno** počas spracovania
3. **Nenahrávajte citlivé dokumenty** - ak nie je nutné

---

**Verzia**: 1.0  
**Posledná aktualizácia**: November 2025  
**Aplikácia**: http://compress-pdf.novis.eu

