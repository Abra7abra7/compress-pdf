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
    dpi: int = 150,
    jpeg_quality: int = 75,
    progress_callback: Optional[callable] = None
) -> tuple[bool, str]:
    """
    Komprimuje jeden PDF súbor.
    
    Args:
        input_path: Cesta k vstupnému PDF súboru
        output_path: Cesta k výstupnému PDF súboru
        dpi: Výstupné DPI (100-200)
        jpeg_quality: Kvalita JPEG kompresie (1-100)
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
        
        # Konverzia PDF na obrázky
        if progress_callback:
            progress_callback(os.path.basename(input_path), 10)
        
        try:
            # Skúsime použiť lokálnu cestu k Poppler ak existuje
            poppler_check = check_poppler_installed()
            poppler_path = poppler_check[2] if len(poppler_check) > 2 else None
            
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
        
        # Kompresia každého obrázka
        compressed_images = []
        total_pages = len(images)
        
        for i, image in enumerate(images):
            # Konverzia na RGB ak je potrebné
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Vytvorenie dočasného súboru v pamäti
            from io import BytesIO
            img_buffer = BytesIO()
            
            # Uloženie s JPEG kompresiou
            image.save(img_buffer, format='JPEG', quality=jpeg_quality, optimize=True)
            img_buffer.seek(0)
            
            # Načítanie späť do PIL Image
            compressed_img = Image.open(img_buffer)
            compressed_images.append(compressed_img)
            
            if progress_callback:
                progress = 30 + int((i + 1) / total_pages * 50)
                progress_callback(os.path.basename(input_path), progress)
        
        # Vytvorenie výstupného adresára ak neexistuje
        output_dir_path = os.path.dirname(output_path)
        if output_dir_path:
            os.makedirs(output_dir_path, exist_ok=True)
        
        if progress_callback:
            progress_callback(os.path.basename(input_path), 85)
        
        # Konverzia obrázkov späť na PDF
        # Použijeme img2pdf ak je dostupný, inak PIL Image.save()
        temp_files = []
        pdf_created = False
        
        try:
            if IMG2PDF_AVAILABLE:
                # Vytvorenie dočasných JPEG súborov pre img2pdf
                for idx, img in enumerate(compressed_images):
                    try:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        img.save(temp_file.name, 'JPEG', quality=jpeg_quality, optimize=True)
                        temp_files.append(temp_file.name)
                        temp_file.close()
                    except Exception as e:
                        raise Exception(f"Chyba pri vytváraní dočasného súboru pre obrázok {idx+1}: {str(e)}")
                
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
                    if len(compressed_images) == 1:
                        compressed_images[0].save(
                            output_path,
                            'PDF',
                            resolution=dpi,
                            quality=jpeg_quality,
                            optimize=True
                        )
                    else:
                        compressed_images[0].save(
                            output_path,
                            'PDF',
                            resolution=dpi,
                            save_all=True,
                            append_images=compressed_images[1:],
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
            # Vymazanie dočasných súborov
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
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return True, f"Úspešne komprimované: {original_size:.2f} MB → {compressed_size:.2f} MB ({compression_ratio:.1f}% zmenšenie)"
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return False, f"Chyba pri kompresii: {str(e)}\nDetaily: {error_details}"


def compress_directory(
    input_dir: str,
    output_dir: Optional[str] = None,
    dpi: int = 150,
    jpeg_quality: int = 75,
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
                log_callback(f"✓ Poppler je nainštalovaný (lokálne): {poppler_path}")
            else:
                log_callback("✓ Poppler je nainštalovaný (v PATH)")
        else:
            log_callback("✗ KRITICKÁ CHYBA: Poppler nie je nainštalovaný!")
            log_callback("=" * 60)
            for line in poppler_message.split('\n'):
                log_callback(line)
            log_callback("=" * 60)
            log_callback("Kompresia nebude fungovať bez Poppler!")
            log_callback("")
        
        log_callback(f"Vyhľadávanie PDF súborov v: {input_dir}")
        log_callback(f"Našlo sa {len(pdf_files)} PDF súborov:")
        for pdf_file in pdf_files[:10]:  # Zobrazíme prvých 10
            log_callback(f"  - {pdf_file.name} ({pdf_file.parent})")
        if len(pdf_files) > 10:
            log_callback(f"  ... a ďalších {len(pdf_files) - 10} súborov")
        
        # Informácia o img2pdf
        if IMG2PDF_AVAILABLE:
            log_callback(f"✓ img2pdf je dostupný - použije sa pre lepšiu kompresiu")
        else:
            log_callback(f"⚠ UPOZORNENIE: img2pdf nie je nainštalovaný!")
            log_callback(f"  Nainštalujte ho: pip install img2pdf")
            log_callback(f"  Použije sa PIL Image.save() (môže mať problémy)")
    
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
                    log_callback(f"✓ {message}")
                else:
                    log_callback(f"✗ CHYBA: {message}")
        
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
                log_callback(f"✗ VÝNIMKA: {error_msg}")
    
    return results

