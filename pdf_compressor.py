"""
PDF Kompresor - Logika pre kompresiu PDF dokumentov zo skenov
"""
import os
import tempfile
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple
from pdf2image import convert_from_path
from PIL import Image
try:
    import img2pdf
    IMG2PDF_AVAILABLE = True
except ImportError:
    IMG2PDF_AVAILABLE = False
    import warnings
    warnings.warn("img2pdf nie je nainštalovaný. Nainštalujte ho pomocou: pip install img2pdf")


def find_poppler_path() -> Optional[str]:
    """
    Pokúsi sa nájsť lokálnu inštaláciu Poppler v projekte.
    
    Returns:
        Cesta k poppler bin adresáru alebo None
    """
    # Možné lokácie Poppler v projekte
    possible_paths = [
        Path(__file__).parent / 'poppler' / 'Library' / 'bin',
        Path(__file__).parent / 'poppler' / 'bin',
        Path(__file__).parent.parent / 'poppler' / 'Library' / 'bin',
    ]
    
    for path in possible_paths:
        if path.exists() and (path / 'pdftoppm.exe').exists() if platform.system() == 'Windows' else (path / 'pdftoppm').exists():
            return str(path)
    
    return None


def get_pdf_dpi(pdf_path: str, poppler_path: Optional[str] = None) -> int:
    """
    Detekuje približné DPI originálneho PDF súboru.
    Konvertuje prvú stránku a odhaduje na základe veľkosti obrázka.
    
    Args:
        pdf_path: Cesta k PDF súboru
        poppler_path: Voliteľná cesta k Poppler binárke
    
    Returns:
        Odhadované DPI (72-600)
    """
    try:
        # Konverzia prvej stránky na štandardných 200 DPI
        if poppler_path:
            images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1)
        
        if len(images) == 0:
            return 150  # Default hodnota
        
        # Zistíme veľkosť obrázka pri 200 DPI
        img = images[0]
        width_200, height_200 = img.size
        
        # Pri 200 DPI platí: veľkosť v pixeloch / 200 = veľkosť v palcoch
        # Ak je obrázok napr. 1700x2200px pri 200 DPI, veľkosť papiera je 8.5x11 palcov (A4: ~8.3x11.7)
        
        # Odhad: ak je obrázok približne A4 (8.3 x 11.7 palcov), 
        # potom pri 200 DPI by mal byť ~1660 x 2340 pixelov
        # Ak je väčší/menší, originálne DPI je vyššie/nižšie
        
        # Jednoduchý výpočet: predpokladáme A4 šírku (~8.3 palcov)
        estimated_inches = 8.3  # A4 šírka
        original_dpi = int(width_200 / estimated_inches)
        
        # Obmedzíme na rozumné hodnoty
        if original_dpi < 72:
            return 72
        elif original_dpi > 600:
            return 600
        else:
            # Zaokrúhlime na najbližších 50
            return round(original_dpi / 50) * 50
            
    except Exception as e:
        # Pri chybe vrátime default hodnotu
        return 150


def check_poppler_installed() -> Tuple[bool, str, Optional[str]]:
    """
    Kontroluje, či je Poppler nainštalovaný a dostupný.
    
    Returns:
        Tuple (is_installed: bool, message: str, poppler_path: Optional[str])
    """
    # Najprv skúsime nájsť lokálnu inštaláciu
    local_path = find_poppler_path()
    if local_path:
        return True, f"Poppler nájdený lokálne: {local_path}", local_path
    
    # Potom skúsime systémovú inštaláciu
    try:
        # Skúsiame spustiť pdftoppm
        result = subprocess.run(
            ['pdftoppm', '-h'] if platform.system() != 'Windows' else ['pdftoppm.exe', '-h'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 or 'pdftoppm' in result.stderr or 'pdftoppm' in result.stdout:
            return True, "Poppler je nainštalovaný a dostupný v PATH", None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    except Exception:
        pass
    
    # Windows inštrukcie
    if platform.system() == 'Windows':
        message = (
            "Poppler NIE JE nainštalovaný!\n\n"
            "INŠTALÁCIA POPPLER PRE WINDOWS:\n"
            "1. Stiahnite Poppler z: https://github.com/oschwartz10612/poppler-windows/releases/\n"
            "2. Rozbalte ZIP súbor (napr. do C:\\poppler)\n"
            "3. METÓDA A - Pridajte do PATH:\n"
            "   - Otvorte 'Premenné prostredia' (Environment Variables)\n"
            "   - V 'Systémové premenné' nájdite 'Path'\n"
            "   - Kliknite 'Upraviť' a pridajte cestu k poppler\\Library\\bin\n"
            "   - Napr: C:\\poppler\\Library\\bin\n"
            "   - Reštartujte aplikáciu\n\n"
            "3. METÓDA B - Lokálna inštalácia (jednoduchšie):\n"
            "   - Rozbalte poppler do adresára projektu\n"
            "   - Umiestnite ho do: compress-pdf\\poppler\\Library\\bin\n"
            "   - Aplikácia ho automaticky nájde\n"
            "   - Pozri INSTALACIA_POPPLER.md pre detaily"
        )
    else:
        message = (
            "Poppler NIE JE nainštalovaný!\n\n"
            "Linux: sudo apt-get install poppler-utils\n"
            "macOS: brew install poppler"
        )
    
    return False, message, None


def compress_pdf(
    input_path: str,
    output_path: str,
    dpi: int = 100,
    jpeg_quality: int = 75,
    progress_callback: Optional[callable] = None
) -> tuple[bool, str]:
    """
    Komprimuje jeden PDF súbor.
    
    Args:
        input_path: Cesta k vstupnému PDF súboru
        output_path: Cesta k výstupnému PDF súboru
        dpi: Výstupné DPI (100-200, alebo 0 pre auto)
        jpeg_quality: Kvalita JPEG kompresie (1-100, alebo 0 pre auto)
        progress_callback: Funkcia na volanie s pokrokom (file_name, progress)
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        if progress_callback:
            progress_callback(os.path.basename(input_path), 0)
        
        # Kontrola existencie vstupného súboru
        if not os.path.exists(input_path):
            return False, f"Vstupný súbor neexistuje: {input_path}"
        
        # Skúsime použiť lokálnu cestu k Poppler ak existuje
        poppler_check = check_poppler_installed()
        poppler_path = poppler_check[2] if len(poppler_check) > 2 else None
        
        # AUTO režim - inteligentná kompresia
        if dpi == 0:  # 0 znamená auto
            if progress_callback:
                progress_callback(os.path.basename(input_path), 5)
            
            # Detekujeme originálne DPI
            try:
                original_dpi = get_pdf_dpi(input_path, poppler_path)
                # Použijeme NIŽŠIE z dvoch hodnôt (nikdy nezvyšujeme DPI!)
                target_dpi = 150  # Zvýšené pre lepšiu čitateľnosť (predtým 72)
                dpi = min(original_dpi, target_dpi)
                
                # Minimálne 100 DPI pre čitateľnosť (predtým 50)
                if dpi < 100:
                    dpi = 100
            except:
                # Ak detekcia zlyhá, použijeme 150 DPI pre dobrú čitateľnosť
                dpi = 150
        
        # AUTO režim pre kvalitu
        if jpeg_quality == 0:  # 0 znamená auto
            jpeg_quality = 85  # Vyššia kvalita pre čitateľnosť (predtým 60)
        
        # Konverzia PDF na obrázky
        if progress_callback:
            progress_callback(os.path.basename(input_path), 10)
        
        try:
            if poppler_path:
                images = convert_from_path(input_path, dpi=dpi, poppler_path=poppler_path)
            else:
                images = convert_from_path(input_path, dpi=dpi)
        except Exception as e:
            error_msg = str(e)
            poppler_check = check_poppler_installed()
            if not poppler_check[0]:
                return False, f"CHYBA: Poppler nie je nainštalovaný!\n\n{poppler_check[1]}\n\nPôvodná chyba: {error_msg}"
            return False, f"Chyba pri konverzii PDF na obrázky: {error_msg}\n\n{poppler_check[1]}"
        
        if len(images) == 0:
            return False, f"PDF súbor neobsahuje žiadne stránky: {input_path}"
        
        if progress_callback:
            progress_callback(os.path.basename(input_path), 30)
        
        # Vytvorenie dočasných JPEG súborov
        temp_files = []
        total_pages = len(images)
        
        for i, image in enumerate(images):
            # Konverzia na RGB ak je potrebné
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Vytvorenie dočasného JPEG súboru
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.close()
            
            # Priame uloženie s JPEG kompresiou
            image.save(temp_file.name, 'JPEG', quality=jpeg_quality, optimize=True)
            temp_files.append(temp_file.name)
            
            if progress_callback:
                progress = 30 + int((i + 1) / total_pages * 50)
                progress_callback(os.path.basename(input_path), progress)
        
        # Vytvorenie výstupného adresára ak neexistuje
        output_dir_path = os.path.dirname(output_path)
        if output_dir_path:
            os.makedirs(output_dir_path, exist_ok=True)
        
        if progress_callback:
            progress_callback(os.path.basename(input_path), 85)
        
        # Konverzia JPEG súborov späť na PDF pomocou img2pdf
        pdf_created = False
        
        try:
            if IMG2PDF_AVAILABLE:
                # Konverzia do PDF pomocou img2pdf
                try:
                    pdf_bytes = img2pdf.convert(temp_files)
                    with open(output_path, 'wb') as f:
                        f.write(pdf_bytes)
                    pdf_created = True
                except Exception as e:
                    raise Exception(f"Chyba pri konverzii do PDF pomocou img2pdf: {str(e)}")
            else:
                # Fallback na PIL Image.save() ak img2pdf nie je dostupný
                try:
                    # Načítanie JPEG súborov späť ako obrázky
                    pil_images = [Image.open(f) for f in temp_files]
                    
                    if len(pil_images) == 1:
                        pil_images[0].save(
                            output_path,
                            'PDF',
                            resolution=dpi,
                            quality=jpeg_quality,
                            optimize=True
                        )
                    else:
                        pil_images[0].save(
                            output_path,
                            'PDF',
                            resolution=dpi,
                            save_all=True,
                            append_images=pil_images[1:],
                            quality=jpeg_quality,
                            optimize=True
                        )
                    pdf_created = True
                except Exception as e:
                    raise Exception(f"Chyba pri ukladaní PDF pomocou PIL: {str(e)}\nSkúste nainštalovať img2pdf: pip install img2pdf")
        
        except Exception as e:
            # Vymazanie čiastočne vytvorených súborov
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
            raise e
        
        finally:
            # Vymazanie dočasných JPEG súborov
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass
        
        if not pdf_created:
            return False, "PDF súbor sa nepodarilo vytvoriť"
        
        if progress_callback:
            progress_callback(os.path.basename(input_path), 100)
        
        # Kontrola, či sa výstupný súbor skutočne vytvoril
        if not os.path.exists(output_path):
            return False, f"Výstupný súbor sa nevytvoril: {output_path}"
        
        # Kontrola veľkosti súboru
        output_size = os.path.getsize(output_path)
        if output_size == 0:
            return False, f"Výstupný súbor je prázdny: {output_path}"
        
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        compressed_size = output_size / (1024 * 1024)  # MB
        
        # OCHRANA: Ak je komprimovaný súbor väčší ako originál, vrátime chybu
        if output_size > os.path.getsize(input_path):
            # Vymazanie zbytočne veľkého výstupného súboru
            try:
                os.unlink(output_path)
            except:
                pass
            
            return False, (
                f"[UPOZORNENIE] Kompresia by zvacsila subor! "
                f"Original: {original_size:.2f} MB, "
                f"Po kompresii: {compressed_size:.2f} MB. "
                f"Tento PDF je uz pravdepodobne dobre komprimovany. "
                f"Pouzite originalny subor."
            )
        
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return True, f"Uspesne komprimovane: {original_size:.2f} MB -> {compressed_size:.2f} MB ({compression_ratio:.1f}% zmensenie)"
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, f"Chyba pri kompresii: {str(e)}\nDetaily: {error_details}"


def compress_directory(
    input_dir: str,
    output_dir: Optional[str] = None,
    dpi: int = 150,
    jpeg_quality: int = 85,
    progress_callback: Optional[callable] = None,
    log_callback: Optional[callable] = None
) -> dict:
    """
    Komprimuje všetky PDF súbory v adresári.
    
    Args:
        input_dir: Vstupný adresár
        output_dir: Výstupný adresár (ak None, vytvorí "compressed" v input_dir)
        dpi: Výstupné DPI
        jpeg_quality: Kvalita JPEG kompresie
        progress_callback: Funkcia na volanie s pokrokom (file_name, progress)
        log_callback: Funkcia na volanie s log správami
    
    Returns:
        Dict so štatistikami: {'success': int, 'failed': int, 'files': list}
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        if log_callback:
            log_callback(f"Adresár neexistuje: {input_dir}")
        return {'success': 0, 'failed': 0, 'files': []}
    
    # Nájdenie všetkých PDF súborov (rekurzívne aj v podadresároch)
    pdf_files = list(input_path.rglob('*.pdf')) + list(input_path.rglob('*.PDF'))
    
    # Odstránenie duplikátov (ak existujú)
    pdf_files = list(set(pdf_files))
    
    # Kontrola Poppler na začiatku
    poppler_check = check_poppler_installed()
    poppler_installed = poppler_check[0]
    poppler_message = poppler_check[1]
    poppler_path = poppler_check[2] if len(poppler_check) > 2 else None
    
    if log_callback:
        if poppler_installed:
            if poppler_path:
                log_callback(f"[OK] Poppler je nainstalovany (lokalne): {poppler_path}")
            else:
                log_callback("[OK] Poppler je nainstalovany (v PATH)")
        else:
            log_callback("[CHYBA] KRITICKA CHYBA: Poppler nie je nainstalovany!")
            log_callback("=" * 60)
            for line in poppler_message.split('\n'):
                log_callback(line)
            log_callback("=" * 60)
            log_callback("Kompresia nebude fungovat bez Poppler!")
            log_callback("")
        
        log_callback(f"Vyhladavanie PDF suborov v: {input_dir}")
        log_callback(f"Naslo sa {len(pdf_files)} PDF suborov:")
        for pdf_file in pdf_files[:10]:  # Zobrazíme prvých 10
            log_callback(f"  - {pdf_file.name} ({pdf_file.parent})")
        if len(pdf_files) > 10:
            log_callback(f"  ... a dalsich {len(pdf_files) - 10} suborov")
        
        # Informácia o img2pdf
        if IMG2PDF_AVAILABLE:
            log_callback(f"[OK] img2pdf je dostupny - pouzije sa pre lepsiu kompresiu")
        else:
            log_callback(f"[UPOZORNENIE] img2pdf nie je nainstalovany!")
            log_callback(f"  Nainstalovanie: pip install img2pdf")
            log_callback(f"  Pouzije sa PIL Image.save() (moze mat problemy)")
    
    if len(pdf_files) == 0:
        if log_callback:
            log_callback(f"Nenašli sa žiadne PDF súbory v adresári: {input_dir}")
            log_callback(f"Skontrolujte, či sú PDF súbory prítomné v adresári.")
        return {'success': 0, 'failed': 0, 'files': []}
    
    # Výstupný adresár
    if output_dir is None:
        output_path = input_path / 'compressed'
    else:
        output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    if log_callback:
        log_callback(f"Výstupný adresár: {output_path.absolute()}")
    
    results = {'success': 0, 'failed': 0, 'files': []}
    
    # Spracovanie každého súboru
    for i, pdf_file in enumerate(pdf_files):
        # Zachovanie štruktúry adresárov ak sú PDF súbory v podadresároch
        relative_path = pdf_file.relative_to(input_path)
        output_file = output_path / relative_path.name
        
        if log_callback:
            log_callback(f"\n[{i+1}/{len(pdf_files)}] Spracovávam: {pdf_file.name}")
            log_callback(f"  Vstup: {pdf_file}")
            log_callback(f"  Výstup: {output_file}")
        
        try:
            success, message = compress_pdf(
                str(pdf_file),
                str(output_file),
                dpi=dpi,
                jpeg_quality=jpeg_quality,
                progress_callback=progress_callback
            )
            
            if success:
                results['success'] += 1
                # Kontrola, či sa súbor skutočne vytvoril
                if not os.path.exists(output_file):
                    success = False
                    message = f"CHYBA: Výstupný súbor sa nevytvoril: {output_file}"
                    results['success'] -= 1
                    results['failed'] += 1
            else:
                results['failed'] += 1
            
            results['files'].append({
                'file': pdf_file.name,
                'success': success,
                'message': message
            })
            
            if log_callback:
                if success:
                    log_callback(f"[OK] {message}")
                else:
                    log_callback(f"[CHYBA] {message}")
        
        except Exception as e:
            import traceback
            error_msg = f"Výnimka pri spracovaní {pdf_file.name}: {str(e)}\n{traceback.format_exc()}"
            results['failed'] += 1
            results['files'].append({
                'file': pdf_file.name,
                'success': False,
                'message': error_msg
            })
            if log_callback:
                log_callback(f"[VYNIMKA] {error_msg}")
    
    return results

