// PDF Kompresor - JavaScript

let currentBatchId = null;
let currentJobIds = [];
let selectedFiles = [];

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
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
        handleFileSelect(files);
    }
});

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(Array.from(e.target.files));
    }
});

// Spracovanie vybraných súborov
function handleFileSelect(files) {
    // Validácia počtu súborov
    const maxFiles = 50;
    if (files.length > maxFiles) {
        showError(`Môžete vybrať maximálne ${maxFiles} súborov naraz!`);
        return;
    }
    
    // Validácia typu a veľkosti súborov
    const maxSize = 600 * 1024 * 1024; // 600 MB
    const invalidFiles = [];
    const tooLargeFiles = [];
    
    for (const file of files) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            invalidFiles.push(file.name);
        }
        if (file.size > maxSize) {
            tooLargeFiles.push(file.name);
        }
    }
    
    if (invalidFiles.length > 0) {
        showError(`Neplatné súbory (nie PDF): ${invalidFiles.join(', ')}`);
        return;
    }
    
    if (tooLargeFiles.length > 0) {
        showError(`Príliš veľké súbory (max 600 MB): ${tooLargeFiles.join(', ')}`);
        return;
    }
    
    // Uloženie vybraných súborov
    selectedFiles = files;
    
    // Spustenie uploadu
    uploadFiles(files);
}

// Upload súborov
async function uploadFiles(files) {
    // Skryť upload sekciu, zobraziť progress
    uploadArea.style.display = 'none';
    document.querySelector('.settings').style.display = 'none';
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Pripravenie FormData
    const formData = new FormData();
    
    // Pridanie všetkých súborov
    for (const file of files) {
        formData.append('files', file);
    }
    
    // Ak je zapnutý auto režim, pošleme 0 (čo backend rozpozná ako auto)
    if (autoMode.checked) {
        formData.append('dpi', '0');
        formData.append('quality', '0');
    } else {
        formData.append('dpi', dpiRange.value);
        formData.append('quality', qualityRange.value);
    }
    
    // Vytvorenie progress UI pre každý súbor
    const filesList = document.getElementById('filesList');
    filesList.innerHTML = '';
    
    for (const file of files) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <span class="file-name">${file.name}</span>
                <span class="file-status">Čaká sa...</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="progress-text">0%</div>
        `;
        filesList.appendChild(fileItem);
    }
    
    try {
        // Upload request
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Chyba pri nahrávaní súborov');
        }
        
        const data = await response.json();
        currentBatchId = data.batch_id;
        currentJobIds = data.job_ids;
        
        // Sledovanie pokroku
        pollBatchProgress();
        
    } catch (error) {
        showError(error.message);
    }
}

// Sledovanie pokroku batch kompresie
async function pollBatchProgress() {
    if (!currentBatchId) return;
    
    try {
        const response = await fetch(`/batch_progress/${currentBatchId}`);
        
        if (!response.ok) {
            throw new Error('Chyba pri získavaní pokroku');
        }
        
        const data = await response.json();
        
        // Update batch summary
        const completed = data.completed + data.failed;
        const total = data.total_files;
        document.getElementById('batchProgress').textContent = `${completed} / ${total} súborov dokončených`;
        
        // Update individual file progress
        const filesList = document.getElementById('filesList');
        const fileItems = filesList.querySelectorAll('.file-item');
        
        let index = 0;
        for (const jobId in data.files) {
            const fileData = data.files[jobId];
            const fileItem = fileItems[index];
            
            if (fileItem) {
                const statusSpan = fileItem.querySelector('.file-status');
                const progressFill = fileItem.querySelector('.progress-fill');
                const progressText = fileItem.querySelector('.progress-text');
                
                // Update status text
                if (fileData.status === 'pending') {
                    statusSpan.textContent = 'Čaká sa...';
                    statusSpan.className = 'file-status status-pending';
                } else if (fileData.status === 'processing') {
                    statusSpan.textContent = 'Spracováva sa...';
                    statusSpan.className = 'file-status status-processing';
                } else if (fileData.status === 'completed') {
                    statusSpan.textContent = '✓ Hotovo';
                    statusSpan.className = 'file-status status-completed';
                } else if (fileData.status === 'error') {
                    statusSpan.textContent = '✗ Chyba';
                    statusSpan.className = 'file-status status-error';
                }
                
                // Update progress bar
                const progress = Math.round(fileData.progress);
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `${progress}%`;
            }
            
            index++;
        }
        
        // Check if all files are done
        if (completed >= total) {
            // Všetky súbory dokončené
            showBatchResults(data);
        } else {
            // Pokračovať v sledovaní
            setTimeout(pollBatchProgress, 500);
        }
        
    } catch (error) {
        showError(error.message);
    }
}

// Zobrazenie výsledkov batch kompresie
function showBatchResults(data) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // Nastavenie štatistík
    document.getElementById('totalProcessed').textContent = data.total_files;
    document.getElementById('totalSuccess').textContent = data.completed;
    document.getElementById('totalFailed').textContent = data.failed;
    
    // Vytvorenie zoznamu výsledkov pre každý súbor
    const resultsFilesList = document.getElementById('resultsFilesList');
    resultsFilesList.innerHTML = '';
    
    for (const jobId in data.files) {
        const fileData = data.files[jobId];
        const resultItem = document.createElement('div');
        resultItem.className = 'result-file-item';
        
        if (fileData.status === 'completed') {
            resultItem.innerHTML = `
                <div class="result-file-header">
                    <span class="result-file-icon">✓</span>
                    <span class="result-file-name">${fileData.filename}</span>
                </div>
                <div class="result-file-stats">
                    <span>${fileData.original_size.toFixed(2)} MB → ${fileData.compressed_size.toFixed(2)} MB</span>
                    <span class="compression-badge">${fileData.compression_ratio.toFixed(1)}% zmenšenie</span>
                </div>
                <button class="btn-download" onclick="downloadFile('${fileData.output_file}')">
                    Stiahnuť
                </button>
            `;
            resultItem.classList.add('result-success');
        } else if (fileData.status === 'error') {
            resultItem.innerHTML = `
                <div class="result-file-header">
                    <span class="result-file-icon">✗</span>
                    <span class="result-file-name">${fileData.filename}</span>
                </div>
                <div class="result-file-error">
                    <span>${fileData.error || 'Neznáma chyba'}</span>
                </div>
            `;
            resultItem.classList.add('result-error');
        }
        
        resultsFilesList.appendChild(resultItem);
    }
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
    currentBatchId = null;
    currentJobIds = [];
    selectedFiles = [];
    
    // Reset UI
    uploadArea.style.display = 'block';
    document.querySelector('.settings').style.display = 'block';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Reset file input
    fileInput.value = '';
    
    // Clear files list
    document.getElementById('filesList').innerHTML = '';
    document.getElementById('resultsFilesList').innerHTML = '';
}

// Reset nastavení (predvolené: DPI=150, Kvalita=85)
function resetSettings() {
    autoMode.checked = true;
    dpiRange.value = 150;
    qualityRange.value = 85;
    dpiValue.textContent = '150';
    qualityValue.textContent = '85';
    dpiRange.disabled = true;
    qualityRange.disabled = true;
    dpiRange.parentElement.style.opacity = '0.6';
    qualityRange.parentElement.style.opacity = '0.6';
}

// Inicializácia
document.addEventListener('DOMContentLoaded', () => {
    console.log('PDF Kompresor initialized');
});

