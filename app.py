"""
PDF Kompresor - Flask Web Aplikácia
"""
from flask import Flask, render_template, request, send_file, jsonify, session
from werkzeug.utils import secure_filename
import os
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
import threading
import secrets
from pdf_compressor import compress_pdf

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Konfigurácia
UPLOAD_FOLDER = Path('uploads')
COMPRESSED_FOLDER = Path('compressed')
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 200 * 1024 * 1024))  # 200 MB default
CLEANUP_AGE_HOURS = int(os.environ.get('CLEANUP_AGE', 24))  # 24 hodín default
ALLOWED_EXTENSIONS = {'pdf'}

# Vytvorenie adresárov
UPLOAD_FOLDER.mkdir(exist_ok=True)
COMPRESSED_FOLDER.mkdir(exist_ok=True)

# Konfigurácia Flask
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

# Progress tracking
compression_progress = {}


def allowed_file(filename):
    """Kontroluje, či je súbor povolený (PDF)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Vymaže staré súbory staršie ako CLEANUP_AGE_HOURS"""
    cutoff_time = datetime.now() - timedelta(hours=CLEANUP_AGE_HOURS)
    
    for folder in [UPLOAD_FOLDER, COMPRESSED_FOLDER]:
        for file_path in folder.glob('*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    try:
                        file_path.unlink()
                        print(f"Vymazaný starý súbor: {file_path}")
                    except Exception as e:
                        print(f"Chyba pri mazaní {file_path}: {e}")


def progress_callback(filename, progress, job_id):
    """Callback funkcia pre progress reporting"""
    compression_progress[job_id] = {
        'filename': filename,
        'progress': progress,
        'status': 'processing'
    }


@app.route('/')
def index():
    """Hlavná stránka"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a kompresia PDF súboru"""
    # Kontrola, či bol nahraný súbor
    if 'file' not in request.files:
        return jsonify({'error': 'Nebol nahraný žiadny súbor'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nebol vybraný žiadny súbor'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Povolené sú len PDF súbory'}), 400
    
    # Získanie parametrov
    try:
        dpi = int(request.form.get('dpi', 100))
        jpeg_quality = int(request.form.get('quality', 75))
        
        # Validácia parametrov (0 = auto režim)
        if dpi != 0 and not (100 <= dpi <= 200):
            return jsonify({'error': 'DPI musí byť medzi 100 a 200, alebo 0 pre auto'}), 400
        if jpeg_quality != 0 and not (60 <= jpeg_quality <= 95):
            return jsonify({'error': 'JPEG kvalita musí byť medzi 60 a 95, alebo 0 pre auto'}), 400
    except ValueError:
        return jsonify({'error': 'Neplatné parametre DPI alebo kvality'}), 400
    
    # Vytvorenie jedinečného job ID
    job_id = str(uuid.uuid4())
    
    # Uloženie súboru
    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    unique_filename = f"{timestamp}_{job_id[:8]}_{filename}"
    input_path = UPLOAD_FOLDER / unique_filename
    
    try:
        file.save(input_path)
    except Exception as e:
        return jsonify({'error': f'Chyba pri ukladaní súboru: {str(e)}'}), 500
    
    # Kontrola veľkosti súboru
    file_size = input_path.stat().st_size
    if file_size > MAX_UPLOAD_SIZE:
        input_path.unlink()
        return jsonify({'error': f'Súbor je príliš veľký. Maximum: {MAX_UPLOAD_SIZE / (1024*1024):.0f} MB'}), 400
    
    # Output path
    output_filename = f"compressed_{unique_filename}"
    output_path = COMPRESSED_FOLDER / output_filename
    
    # Initialize progress
    compression_progress[job_id] = {
        'filename': filename,
        'progress': 0,
        'status': 'starting'
    }
    
    # Spustenie kompresie v samostatnom vlákne
    def compress_task():
        try:
            # Progress callback wrapper
            def progress_wrapper(fname, prog):
                progress_callback(fname, prog, job_id)
            
            success, message = compress_pdf(
                str(input_path),
                str(output_path),
                dpi=dpi,
                jpeg_quality=jpeg_quality,
                progress_callback=progress_wrapper
            )
            
            if success:
                # Získanie veľkostí súborov
                original_size = input_path.stat().st_size / (1024 * 1024)  # MB
                compressed_size = output_path.stat().st_size / (1024 * 1024)  # MB
                compression_ratio = (1 - compressed_size / original_size) * 100
                
                compression_progress[job_id] = {
                    'filename': filename,
                    'progress': 100,
                    'status': 'completed',
                    'output_file': output_filename,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': compression_ratio,
                    'message': message
                }
            else:
                compression_progress[job_id] = {
                    'filename': filename,
                    'progress': 0,
                    'status': 'error',
                    'error': message
                }
            
            # Vymazanie vstupného súboru
            try:
                input_path.unlink()
            except:
                pass
                
        except Exception as e:
            compression_progress[job_id] = {
                'filename': filename,
                'progress': 0,
                'status': 'error',
                'error': str(e)
            }
            # Vymazanie súborov pri chybe
            try:
                if input_path.exists():
                    input_path.unlink()
                if output_path.exists():
                    output_path.unlink()
            except:
                pass
    
    # Spustenie vlákna
    thread = threading.Thread(target=compress_task, daemon=True)
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'filename': filename,
        'status': 'started'
    })


@app.route('/progress/<job_id>')
def get_progress(job_id):
    """Získanie pokroku kompresie"""
    if job_id in compression_progress:
        return jsonify(compression_progress[job_id])
    else:
        return jsonify({'error': 'Job ID nenájdené'}), 404


@app.route('/download/<filename>')
def download_file(filename):
    """Stiahnutie skomprimovaného súboru"""
    file_path = COMPRESSED_FOLDER / secure_filename(filename)
    
    if not file_path.exists():
        return jsonify({'error': 'Súbor nenájdený'}), 404
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename.replace('compressed_', '').split('_', 2)[-1]  # Odstránenie timestampu
        )
    except Exception as e:
        return jsonify({'error': f'Chyba pri sťahovaní: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manuálne vyčistenie starých súborov (admin endpoint)"""
    # TODO: Pridať autentifikáciu pre produkčné prostredie
    cleanup_old_files()
    return jsonify({'status': 'Vyčistenie dokončené'})


# Automatické čistenie pri štarte
cleanup_old_files()

# Periodické čistenie (každých 6 hodín)
def periodic_cleanup():
    """Periodické čistenie v pozadí"""
    while True:
        time.sleep(6 * 60 * 60)  # 6 hodín
        cleanup_old_files()

# Spustenie cleanup vlákna
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=False)

