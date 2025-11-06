"""
Automatická inštalácia Poppler pre Windows
Tento skript automaticky stiahne a nainštaluje Poppler do projektu.
"""
import os
import sys
import zipfile
import urllib.request
import shutil
from pathlib import Path
import platform

# Nastavenie UTF-8 kódovania pre Windows
if platform.system() == 'Windows':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def download_poppler():
    """Stiahne Poppler z GitHub releases"""
    print("Stahujem Poppler...")
    
    # URL najnovšej verzie poppler-windows
    # Použijeme Release-23.11.0-0 ako stabilnú verziu
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip"
    
    poppler_dir = Path(__file__).parent / 'poppler'
    poppler_dir.mkdir(exist_ok=True)
    
    zip_path = poppler_dir / 'poppler.zip'
    
    try:
        print(f"Stahujem z: {poppler_url}")
        print("To môže chvíľu trvať (cca 50 MB)...")
        
        urllib.request.urlretrieve(poppler_url, zip_path)
        print("OK Stiahnute!")
        
        return zip_path, poppler_dir
    except Exception as e:
        print(f"CHYBA pri stahovani: {e}")
        print("\nSkúste stiahnuť manuálne z:")
        print("https://github.com/oschwartz10612/poppler-windows/releases/")
        return None, None

def extract_poppler(zip_path, poppler_dir):
    """Rozbalí Poppler ZIP súbor"""
    print("\nRozbaľujem Poppler...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(poppler_dir)
        print("✓ Rozbalené!")
        
        # Vymazanie ZIP súboru
        zip_path.unlink()
        
        # Nájdenie správnej cesty
        extracted_dirs = list(poppler_dir.glob('*'))
        for dir_path in extracted_dirs:
            if dir_path.is_dir() and (dir_path / 'Library' / 'bin').exists():
                # Presun súborov na správne miesto
                library_bin = dir_path / 'Library' / 'bin'
                target_bin = poppler_dir / 'Library' / 'bin'
                target_bin.parent.mkdir(parents=True, exist_ok=True)
                
                if library_bin.exists():
                    if target_bin.exists():
                        shutil.rmtree(target_bin)
                    shutil.copytree(library_bin, target_bin)
                    print(f"✓ Poppler nainštalovaný do: {target_bin}")
                    return target_bin
        
        # Ak sa nenašla štandardná štruktúra, skúsime nájsť bin adresár
        for dir_path in extracted_dirs:
            if dir_path.is_dir():
                bin_path = dir_path / 'bin'
                if bin_path.exists():
                    target_bin = poppler_dir / 'bin'
                    if target_bin.exists():
                        shutil.rmtree(target_bin)
                    shutil.copytree(bin_path, target_bin)
                    print(f"✓ Poppler nainštalovaný do: {target_bin}")
                    return target_bin
        
        print("⚠ Nenašiel sa štandardný bin adresár, skontrolujte manuálne")
        return None
        
    except Exception as e:
        print(f"✗ Chyba pri rozbaľovaní: {e}")
        return None

def verify_installation(poppler_bin_path):
    """Overí, či je Poppler správne nainštalovaný"""
    if poppler_bin_path is None:
        return False
    
    if platform.system() == 'Windows':
        pdftoppm = poppler_bin_path / 'pdftoppm.exe'
    else:
        pdftoppm = poppler_bin_path / 'pdftoppm'
    
    if pdftoppm.exists():
        print(f"\nOK Poppler je nainstalovany!")
        print(f"  Cesta: {poppler_bin_path.absolute()}")
        return True
    else:
        print(f"\nCHYBA: pdftoppm.exe sa nenasiel v: {poppler_bin_path}")
        return False

def main():
    print("=" * 60)
    print("Automatická inštalácia Poppler pre PDF Kompresor")
    print("=" * 60)
    
    if platform.system() != 'Windows':
        print("Tento skript je určený pre Windows.")
        print("Pre Linux použite: sudo apt-get install poppler-utils")
        print("Pre macOS použite: brew install poppler")
        return
    
    poppler_dir = Path(__file__).parent / 'poppler'
    poppler_bin = poppler_dir / 'Library' / 'bin'
    
    # Kontrola, či už nie je nainštalovaný
    if poppler_bin.exists() and (poppler_bin / 'pdftoppm.exe').exists():
        print("OK Poppler uz je nainstalovany!")
        print(f"  Cesta: {poppler_bin.absolute()}")
        return
    
    # Stiahnutie
    zip_path, poppler_dir = download_poppler()
    if zip_path is None:
        return
    
    # Rozbalenie
    poppler_bin = extract_poppler(zip_path, poppler_dir)
    
    # Overenie
    if verify_installation(poppler_bin):
        print("\n" + "=" * 60)
        print("OK Instalacia dokoncena!")
        print("=" * 60)
        print("\nTeraz mozete spustit aplikaciu: python main.py")
        print("Aplikacia automaticky najde Poppler v projekte.")
    else:
        print("\n" + "=" * 60)
        print("VAROVANIE: Instalacia sa dokoncila, ale overenie zlyhalo.")
        print("Skontrolujte manualne, ci je Poppler spravne nainstalovany.")
        print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInštalácia prerušená používateľom.")
        sys.exit(1)
    except Exception as e:
        print(f"\nCHYBA: Neocekavana chyba: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

