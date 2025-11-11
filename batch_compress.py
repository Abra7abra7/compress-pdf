#!/usr/bin/env python3
"""
Batch PDF Kompresor - Pre spracovanie veľkého počtu súborov
Použitie: python batch_compress.py /cesta/k/pdf/suborom /cesta/k/vystupu
"""

import sys
import os
from pathlib import Path
from pdf_compressor import compress_directory

def main():
    if len(sys.argv) < 2:
        print("Použitie: python batch_compress.py <vstupny_priecinok> [vystupny_priecinok]")
        print("\nPríklad:")
        print("  python batch_compress.py C:\\Documents\\PDFs")
        print("  python batch_compress.py C:\\Documents\\PDFs C:\\Documents\\Compressed")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Kontrola existencie adresára
    if not os.path.exists(input_dir):
        print(f"❌ Chyba: Adresár neexistuje: {input_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("PDF BATCH KOMPRESOR")
    print("=" * 60)
    print(f"Vstupny adresar: {input_dir}")
    print(f"Vystupny adresar: {output_dir if output_dir else 'Automaticky (compressed)'}")
    print(f"Rezim: Auto (DPI=150, Kvalita=85) - Optimalizovane pre citatelnost")
    print("=" * 60)
    print()
    
    # Nájdenie všetkých PDF súborov
    pdf_files = list(Path(input_dir).rglob('*.pdf')) + list(Path(input_dir).rglob('*.PDF'))
    pdf_count = len(pdf_files)
    
    print(f"Najdenych {pdf_count} PDF suborov")
    
    if pdf_count == 0:
        print("UPOZORNENIE: Ziadne PDF subory nenajdene!")
        sys.exit(0)
    
    if pdf_count > 100:
        print(f"UPOZORNENIE: Naslo sa {pdf_count} suborov!")
        print(f"   Odhadovany cas: {pdf_count * 0.5:.0f}-{pdf_count * 2:.0f} minut")
        response = input("\n   Pokracovat? (ano/nie): ")
        if response.lower() not in ['ano', 'a', 'yes', 'y']:
            print("Zrusene pouziavtelom")
            sys.exit(0)
    
    print()
    print("Spustam kompresiu...")
    print()
    
    # Spustenie kompresie
    results = compress_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        dpi=0,  # Auto režim
        jpeg_quality=0,  # Auto režim
        progress_callback=None,  # Žiadny progress callback
        log_callback=print  # Výpis do konzoly
    )
    
    # Výsledky
    print()
    print("=" * 60)
    print("KOMPRESIA DOKONCENA")
    print("=" * 60)
    print(f"Celkovo spracovanych: {results['success'] + results['failed']}")
    print(f"Uspesnych: {results['success']}")
    print(f"Zlyhalo: {results['failed']}")
    
    if results['failed'] > 0:
        print()
        print("CHYBNE SUBORY:")
        for file_info in results['files']:
            if not file_info['success']:
                print(f"   - {file_info['file']}")
                print(f"     {file_info['message']}")
    
    print()
    output_path = output_dir if output_dir else os.path.join(input_dir, 'compressed')
    print(f"Vystupny adresar: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()

