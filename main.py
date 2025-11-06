"""
PDF Kompresor - GUI Aplikácia
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import subprocess
import platform
from pathlib import Path
from pdf_compressor import compress_directory


class PDFCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Kompresor")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Premenné
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.dpi = tk.IntVar(value=100)
        self.jpeg_quality = tk.IntVar(value=75)
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Hlavný frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nadpis
        title_label = ttk.Label(
            main_frame,
            text="PDF Kompresor",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Vstupný adresár
        input_frame = ttk.LabelFrame(main_frame, text="Vstupný adresár", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Vybrať", command=self.select_input_dir).pack(side=tk.LEFT)
        
        # Výstupný adresár
        output_frame = ttk.LabelFrame(main_frame, text="Výstupný adresár (voliteľné)", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Vybrať", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # Nastavenia kompresie
        settings_frame = ttk.LabelFrame(main_frame, text="Nastavenia kompresie", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # DPI nastavenie
        dpi_frame = ttk.Frame(settings_frame)
        dpi_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dpi_frame, text="DPI:").pack(side=tk.LEFT, padx=(0, 10))
        dpi_scale = ttk.Scale(
            dpi_frame,
            from_=100,
            to=200,
            variable=self.dpi,
            orient=tk.HORIZONTAL,
            length=300
        )
        dpi_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.dpi_label = ttk.Label(dpi_frame, text="100")
        self.dpi_label.pack(side=tk.LEFT)
        dpi_scale.configure(command=self.update_dpi_label)
        
        # JPEG kvalita
        quality_frame = ttk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="JPEG kvalita:").pack(side=tk.LEFT, padx=(0, 10))
        quality_scale = ttk.Scale(
            quality_frame,
            from_=60,
            to=95,
            variable=self.jpeg_quality,
            orient=tk.HORIZONTAL,
            length=300
        )
        quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.quality_label = ttk.Label(quality_frame, text="75")
        self.quality_label.pack(side=tk.LEFT)
        quality_scale.configure(command=self.update_quality_label)
        
        # Tlačidlá
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.compress_button = ttk.Button(
            button_frame,
            text="Komprimovať PDF súbory",
            command=self.start_compression,
            style="Accent.TButton"
        )
        self.compress_button.pack(side=tk.LEFT, padx=5)
        
        self.open_output_button = ttk.Button(
            button_frame,
            text="Otvoriť výstupný adresár",
            command=self.open_output_directory
        )
        self.open_output_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10, fill=tk.X)
        
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack()
        
        # Log textové pole
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def update_dpi_label(self, value):
        self.dpi_label.config(text=str(int(float(value))))
    
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
    
    def select_input_dir(self):
        directory = filedialog.askdirectory(title="Vyberte vstupný adresár s PDF súbormi")
        if directory:
            self.input_dir.set(directory)
            self.log(f"Vybraný vstupný adresár: {directory}")
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Vyberte výstupný adresár")
        if directory:
            self.output_dir.set(directory)
            self.log(f"Vybraný výstupný adresár: {directory}")
    
    def open_output_directory(self):
        """Otvorenie výstupného adresára v exploreri"""
        output_dir = self.output_dir.get()
        if not output_dir:
            # Ak nie je zadaný výstupný adresár, použijeme automaticky vytvorený
            input_dir = self.input_dir.get()
            if input_dir:
                output_dir = os.path.join(input_dir, 'compressed')
            else:
                messagebox.showwarning("Upozornenie", "Najprv vyberte vstupný adresár alebo zadajte výstupný adresár!")
                return
        
        output_path = Path(output_dir)
        
        # Vytvorenie adresára ak neexistuje
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Otvorenie v exploreri podľa operačného systému
        try:
            if platform.system() == 'Windows':
                os.startfile(str(output_path.absolute()))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(output_path.absolute())])
            else:  # Linux
                subprocess.run(['xdg-open', str(output_path.absolute())])
            self.log(f"Otvorený výstupný adresár: {output_path.absolute()}")
        except Exception as e:
            messagebox.showerror("Chyba", f"Nepodarilo sa otvoriť adresár:\n{str(e)}")
    
    def log(self, message):
        """Pridá správu do log textového poľa"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_progress(self, filename, progress):
        """Aktualizuje progress bar"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"Spracovávam: {filename} ({progress:.0f}%)")
        self.root.update_idletasks()
    
    def start_compression(self):
        """Spustí kompresiu v samostatnom vlákne"""
        if self.is_processing:
            messagebox.showwarning("Upozornenie", "Kompresia už prebieha!")
            return
        
        input_dir = self.input_dir.get()
        if not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("Chyba", "Vyberte platný vstupný adresár!")
            return
        
        output_dir = self.output_dir.get() if self.output_dir.get() else None
        
        # Vymazanie logu
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.log(f"Začínam kompresiu...")
        self.log(f"Vstupný adresár: {input_dir}")
        self.log(f"Výstupný adresár: {output_dir if output_dir else 'Automaticky (compressed)'}")
        self.log(f"DPI: {self.dpi.get()}, JPEG kvalita: {self.jpeg_quality.get()}")
        self.log("")
        
        # Spustenie v samostatnom vlákne
        self.is_processing = True
        self.compress_button.config(state=tk.DISABLED, text="Kompresia prebieha...")
        self.progress_var.set(0)
        
        thread = threading.Thread(
            target=self.run_compression,
            args=(input_dir, output_dir),
            daemon=True
        )
        thread.start()
    
    def run_compression(self, input_dir, output_dir):
        """Spustí kompresiu (volané v samostatnom vlákne)"""
        try:
            results = compress_directory(
                input_dir=input_dir,
                output_dir=output_dir,
                dpi=self.dpi.get(),
                jpeg_quality=self.jpeg_quality.get(),
                progress_callback=self.update_progress,
                log_callback=self.log
            )
            
            # Dokončenie
            self.root.after(0, self.compression_finished, results)
        
        except Exception as e:
            self.root.after(0, self.compression_error, str(e))
    
    def compression_finished(self, results):
        """Volané po dokončení kompresie"""
        self.is_processing = False
        self.compress_button.config(state=tk.NORMAL, text="Komprimovať PDF súbory")
        self.progress_var.set(100)
        self.progress_label.config(text="Hotovo!")
        
        # Zistenie výstupného adresára
        output_dir = self.output_dir.get() if self.output_dir.get() else os.path.join(self.input_dir.get(), 'compressed')
        
        self.log(f"\n{'='*50}")
        self.log(f"Kompresia dokončená!")
        self.log(f"Úspešne: {results['success']}")
        self.log(f"Zlyhalo: {results['failed']}")
        self.log(f"Výstupný adresár: {output_dir}")
        self.log(f"{'='*50}")
        
        # Zobrazenie chýb ak nejaké sú
        if results['failed'] > 0:
            self.log("\nChyby pri spracovaní:")
            for file_info in results['files']:
                if not file_info['success']:
                    self.log(f"  - {file_info['file']}: {file_info['message']}")
        
        message = f"Spracované súbory: {results['success'] + results['failed']}\n"
        message += f"Úspešne: {results['success']}\n"
        message += f"Zlyhalo: {results['failed']}\n\n"
        message += f"Výstupný adresár:\n{output_dir}\n\n"
        message += "Kliknite na 'Otvoriť výstupný adresár' pre zobrazenie súborov."
        
        msg_box = messagebox.showinfo("Kompresia dokončená", message)
    
    def compression_error(self, error_msg):
        """Volané pri chybe kompresie"""
        self.is_processing = False
        self.compress_button.config(state=tk.NORMAL, text="Komprimovať PDF súbory")
        self.log(f"\nChyba: {error_msg}")
        messagebox.showerror("Chyba", f"Chyba pri kompresii:\n{error_msg}")


def main():
    root = tk.Tk()
    app = PDFCompressorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

