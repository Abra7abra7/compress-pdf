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
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 600 * 1024 * 1024))  # 600 MB default
CLEANUP_AGE_HOURS = int(os.environ.get('CLEANUP_AGE', 24))  # 24 hodín default
ALLOWED_EXTENSIONS = {'pdf'}
MAX_BATCH_FILES = 50  # Maximum počet súborov v jednom batchi

# Vytvorenie adresárov
UPLOAD_FOLDER.mkdir(exist_ok=True)
COMPRESSED_FOLDER.mkdir(exist_ok=True)

# Konfigurácia Flask
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

# Progress tracking
compression_progress = {}
batch_progress = {}  # Tracking pre celé batche súborov


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
    """Upload a kompresia PDF súboru/súborov (podporuje batch upload)"""
    # Kontrola, či boli nahraté súbory
    if 'files' not in request.files:
        return jsonify({'error': 'Neboli nahraté žiadne súbory'}), 400
    
    files = request.files.getlist('files')
    
    if len(files) == 0:
        return jsonify({'error': 'Neboli vybrané žiadne súbory'}), 400
    
    # Validácia počtu súborov
    if len(files) > MAX_BATCH_FILES:
        return jsonify({'error': f'Môžete nahrať maximálne {MAX_BATCH_FILES} súborov naraz'}), 400
    
    # Validácia typu súborov
    for file in files:
        if file.filename == '':
            return jsonify({'error': 'Jeden alebo viac súborov nemá názov'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': f'Súbor {file.filename} nie je PDF. Povolené sú len PDF súbory'}), 400
    
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
    
    # Vytvorenie jedinečného batch ID
    batch_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Inicializácia batch progress
    batch_progress[batch_id] = {
        'total_files': len(files),
        'completed': 0,
        'failed': 0,
        'processing': 0,
        'files': {}
    }
    
    # Spracovanie každého súboru
    job_ids = []
    
    for file in files:
        filename = secure_filename(file.filename)
        job_id = str(uuid.uuid4())
        job_ids.append(job_id)
        
        unique_filename = f"{timestamp}_{job_id[:8]}_{filename}"
        input_path = UPLOAD_FOLDER / unique_filename
        
        # Uloženie súboru
        try:
            file.save(input_path)
        except Exception as e:
            return jsonify({'error': f'Chyba pri ukladaní súboru {filename}: {str(e)}'}), 500
        
        # Kontrola veľkosti súboru
        file_size = input_path.stat().st_size
        if file_size > MAX_UPLOAD_SIZE:
            input_path.unlink()
            return jsonify({'error': f'Súbor {filename} je príliš veľký. Maximum: {MAX_UPLOAD_SIZE / (1024*1024):.0f} MB'}), 400
        
        # Output path
        output_filename = f"compressed_{unique_filename}"
        output_path = COMPRESSED_FOLDER / output_filename
        
        # Initialize progress pre tento súbor
        compression_progress[job_id] = {
            'filename': filename,
            'progress': 0,
            'status': 'pending',
            'batch_id': batch_id
        }
        
        batch_progress[batch_id]['files'][job_id] = {
            'filename': filename,
            'status': 'pending',
            'progress': 0
        }
        
        # Spustenie kompresie v samostatnom vlákne
        def compress_task(job_id=job_id, input_path=input_path, output_path=output_path, 
                         filename=filename, output_filename=output_filename, batch_id=batch_id):
            try:
                # Update status
                compression_progress[job_id]['status'] = 'processing'
                batch_progress[batch_id]['files'][job_id]['status'] = 'processing'
                batch_progress[batch_id]['processing'] += 1
                
                # Progress callback wrapper
                def progress_wrapper(fname, prog):
                    compression_progress[job_id]['progress'] = prog
                    batch_progress[batch_id]['files'][job_id]['progress'] = prog
                
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
                        'message': message,
                        'batch_id': batch_id
                    }
                    
                    batch_progress[batch_id]['files'][job_id] = {
                        'filename': filename,
                        'status': 'completed',
                        'progress': 100,
                        'output_file': output_filename,
                        'original_size': original_size,
                        'compressed_size': compressed_size,
                        'compression_ratio': compression_ratio
                    }
                    batch_progress[batch_id]['completed'] += 1
                else:
                    compression_progress[job_id] = {
                        'filename': filename,
                        'progress': 0,
                        'status': 'error',
                        'error': message,
                        'batch_id': batch_id
                    }
                    batch_progress[batch_id]['files'][job_id] = {
                        'filename': filename,
                        'status': 'error',
                        'progress': 0,
                        'error': message
                    }
                    batch_progress[batch_id]['failed'] += 1
                
                batch_progress[batch_id]['processing'] -= 1
                
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
                    'error': str(e),
                    'batch_id': batch_id
                }
                batch_progress[batch_id]['files'][job_id] = {
                    'filename': filename,
                    'status': 'error',
                    'progress': 0,
                    'error': str(e)
                }
                batch_progress[batch_id]['failed'] += 1
                batch_progress[batch_id]['processing'] -= 1
                
                # Vymazanie súborov pri chybe
                try:
                    if input_path.exists():
                        input_path.unlink()
                    if output_path.exists():
                        output_path.unlink()
                except:
                    pass
        
        # Spustenie vlákna pre tento súbor
        thread = threading.Thread(target=compress_task, daemon=True)
        thread.start()
    
    return jsonify({
        'batch_id': batch_id,
        'job_ids': job_ids,
        'total_files': len(files),
        'status': 'started'
    })


@app.route('/progress/<job_id>')
def get_progress(job_id):
    """Získanie pokroku kompresie jedného súboru"""
    if job_id in compression_progress:
        return jsonify(compression_progress[job_id])
    else:
        return jsonify({'error': 'Job ID nenájdené'}), 404


@app.route('/batch_progress/<batch_id>')
def get_batch_progress(batch_id):
    """Získanie pokroku celého batchu súborov"""
    if batch_id in batch_progress:
        return jsonify(batch_progress[batch_id])
    else:
        return jsonify({'error': 'Batch ID nenájdené'}), 404


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

