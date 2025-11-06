// PDF Kompresor - JavaScript

let currentJobId = null;
let currentOutputFile = null;

// DOM elementy
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const progressSection = document.getElementById('progressSection');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const autoMode = document.getElementById('autoMode');
const dpiRange = document.getElementById('dpiRange');
const qualityRange = document.getElementById('qualityRange');
const dpiValue = document.getElementById('dpiValue');
const qualityValue = document.getElementById('qualityValue');

// Auto režim handling
autoMode.addEventListener('change', (e) => {
    const isAuto = e.target.checked;
    dpiRange.disabled = isAuto;
    qualityRange.disabled = isAuto;
    
    if (isAuto) {
        dpiRange.parentElement.style.opacity = '0.6';
        qualityRange.parentElement.style.opacity = '0.6';
    } else {
        dpiRange.parentElement.style.opacity = '1';
        qualityRange.parentElement.style.opacity = '1';
    }
});

// Nastavenia range sliderov
dpiRange.addEventListener('input', (e) => {
    dpiValue.textContent = e.target.value;
});

qualityRange.addEventListener('input', (e) => {
    qualityValue.textContent = e.target.value;
});

// Drag & Drop funkcionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Spracovanie vybraného súboru
function handleFileSelect(file) {
    // Validácia typu súboru
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Povolené sú len PDF súbory!');
        return;
    }
    
    // Validácia veľkosti súboru (200 MB)
    const maxSize = 200 * 1024 * 1024;
    if (file.size > maxSize) {
        showError(`Súbor je príliš veľký! Maximum: ${maxSize / (1024*1024)} MB`);
        return;
    }
    
    // Spustenie uploadu
    uploadFile(file);
}

// Upload súboru
async function uploadFile(file) {
    // Skryť upload sekciu, zobraziť progress
    uploadArea.style.display = 'none';
    document.querySelector('.settings').style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Nastavenie progress
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileStatus').textContent = 'Nahráva sa...';
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    
    // Pripravenie FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Ak je zapnutý auto režim, pošleme 0 (čo backend rozpozná ako auto)
    if (autoMode.checked) {
        formData.append('dpi', '0');
        formData.append('quality', '0');
    } else {
        formData.append('dpi', dpiRange.value);
        formData.append('quality', qualityRange.value);
    }
    
    try {
        // Upload request
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Chyba pri nahrávaní súboru');
        }
        
        const data = await response.json();
        currentJobId = data.job_id;
        
        // Sledovanie pokroku
        document.getElementById('fileStatus').textContent = 'Komprimuje sa...';
        pollProgress();
        
    } catch (error) {
        showError(error.message);
    }
}

// Sledovanie pokroku kompresie
async function pollProgress() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/progress/${currentJobId}`);
        
        if (!response.ok) {
            throw new Error('Chyba pri získavaní pokroku');
        }
        
        const data = await response.json();
        
        // Update progress
        const progress = Math.round(data.progress);
        document.getElementById('progressFill').style.width = `${progress}%`;
        document.getElementById('progressText').textContent = `${progress}%`;
        
        if (data.status === 'completed') {
            // Kompresia dokončená
            currentOutputFile = data.output_file;
            showResult(data);
        } else if (data.status === 'error') {
            // Chyba
            showError(data.error || 'Neznáma chyba pri kompresii');
        } else {
            // Pokračovať v sledovaní
            setTimeout(pollProgress, 500);
        }
        
    } catch (error) {
        showError(error.message);
    }
}

// Zobrazenie výsledku
function showResult(data) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // Nastavenie štatistík
    document.getElementById('originalSize').textContent = `${data.original_size.toFixed(2)} MB`;
    document.getElementById('compressedSize').textContent = `${data.compressed_size.toFixed(2)} MB`;
    document.getElementById('compressionRatio').textContent = `${data.compression_ratio.toFixed(1)}%`;
    
    // Download tlačidlo
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.onclick = () => downloadFile(currentOutputFile);
}

// Zobrazenie chyby
function showError(message) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'block';
    
    document.getElementById('errorMessage').textContent = message;
}

// Stiahnutie súboru
function downloadFile(filename) {
    window.location.href = `/download/${filename}`;
}

// Reset uploadu
function resetUpload() {
    currentJobId = null;
    currentOutputFile = null;
    
    // Reset UI
    uploadArea.style.display = 'block';
    document.querySelector('.settings').style.display = 'block';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Reset file input
    fileInput.value = '';
}

// Reset nastavení
function resetSettings() {
    autoMode.checked = true;
    dpiRange.value = 100;
    qualityRange.value = 75;
    dpiValue.textContent = '100';
    qualityValue.textContent = '75';
    dpiRange.disabled = true;
    qualityRange.disabled = true;
    dpiRange.parentElement.style.opacity = '0.6';
    qualityRange.parentElement.style.opacity = '0.6';
}

// Inicializácia
document.addEventListener('DOMContentLoaded', () => {
    console.log('PDF Kompresor initialized');
});

