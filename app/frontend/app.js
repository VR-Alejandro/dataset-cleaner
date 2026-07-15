const API_URL = "http://localhost:8000";

let currentPage = 1;
const ITEMS_PER_PAGE = 5;
const knownIds = new Set();      // Guarda los IDs que ya existen
const activePolls = new Set();   // Evita duplicar bucles de intervalos de escucha
let isInitialLoad = true;        // Flag para el primer encendido de la app

let fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const uploadBtn = document.getElementById("uploadBtn");
const clearBtn = document.getElementById("clearBtn");
const deleteAllBtn = document.getElementById("deleteAllBtn");

// Función para enlazar los eventos del input de archivos
function setupFileInputListeners() {
    fileInput.addEventListener("change", (e) => updateDropzoneText(e.target.files[0]));
}

dropzone.addEventListener("click", () => fileInput.click());
uploadBtn.addEventListener("click", uploadFile);
clearBtn.addEventListener("click", clearDropzone);
deleteAllBtn.addEventListener("click", deleteAllDatasets);

// Inicializar la primera escucha
setupFileInputListeners();
setupBinsRestrictions();

// Control de arrastre visual simple
dropzone.addEventListener("dragover", (e) => { e.preventDefault(); });
dropzone.addEventListener("dragleave", (e) => { e.preventDefault(); });
dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updateDropzoneText(fileInput.files[0]);
    }
});

function updateDropzoneText(file) {
    if (file) {
        dropzone.innerHTML = `
            <p class="mb-1 text-success small fw-bold text-truncate px-3" style="max-width: 100%;">
                📄 ${file.name}
            </p>
            <span class="text-muted" style="font-size: 0.75rem;">Ready to upload</span>
        `;
        // Fijamos el estado verde permanente
        dropzone.classList.add('has-file');
    }
}

function clearDropzone() {
    fileInput.value = ""; // Vaciamos el archivo binario
    dropzone.classList.remove('has-file'); // Quitamos los estilos verdes

    // Restauramos el HTML original de la dropzone
    dropzone.innerHTML = `
        <p class="mb-0 fw-bold text-secondary">Upload dataset</p>
        <div class="drop-text-wrapper small text-muted">
            <span class="drop-text-normal">or drop here</span>
            <span class="drop-text-hover">Drop here!</span>
        </div>
        <input type="file" id="fileInput" class="d-none">
    `;
    
    // Volvemos a capturar y enlazar el nuevo input generado
    fileInput = document.getElementById("fileInput");
    setupFileInputListeners();
}


// Carga inicial al abrir la página
loadDatasets();

async function uploadFile() {
    const numNullInput = document.getElementById("numNullTreatment");
    const catNullInput = document.getElementById("catNullTreatment");
    const binsInput = document.getElementById("histogramBins");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file before submitting.");
        return;
    }

    // Protección ante posibles selección de N grupos fuera de rango
    let binsValue = parseInt(binsInput.value, 10);
    if (isNaN(binsValue) || binsValue < 5) {
        binsValue = 5;
        binsInput.value = 5; // Mostramos 5 en el HTML
    } else if (binsValue > 50) {
        binsValue = 50;
        binsInput.value = 50; // Mostramos 50 en el HTML
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("numerical_missing", numNullInput.value);
    formData.append("categorical_missing", catNullInput.value);
    formData.append("histogram_bins", binsValue);

    try {
        const res = await fetch(`${API_URL}/datasets`, { method: "POST", body: formData });
        if (!res.ok) throw new Error("Failed to upload dataset");
        
        // Quitamos el estado verde permanente de la dropzone
        dropzone.classList.remove('has-file');

        // Restauramos el contenido original de la dropzone
        dropzone.innerHTML = `
            <p class="mb-0 fw-bold text-secondary">Upload dataset</p>
            <div class="drop-text-wrapper small text-muted">
                <span class="drop-text-normal">or drop here</span>
                <span class="drop-text-hover">Drop here!</span>
            </div>
            <input type="file" id="fileInput" class="d-none">
        `;
        
        // Volvemos a capturar el nuevo input del DOM y le re-asignamos los eventos.
        fileInput = document.getElementById("fileInput");
        setupFileInputListeners();
        
        currentPage = 1; 
        loadDatasets();
    } catch (err) {
        alert(err.message);
    }
}

async function loadDatasets() {
    try {
        const res = await fetch(`${API_URL}/datasets`, { cache: "no-store" });
        const data = await res.json();

        const container = document.getElementById("datasetList");

        // Si la API devuelve un array sin elementos...
        if (!data || data.length === 0) {
            // Ocultamos el botón "Delete All"; no hay nada que borrar
            if (deleteAllBtn) deleteAllBtn.style.display = "none";

            // Limpiamos la paginación si el contenedor de paginación existe
            const paginationContainer = document.getElementById("paginationContainer");
            if (paginationContainer) paginationContainer.innerHTML = "";

            // Mensaje al usuario para sugerir la interacción
            container.innerHTML = `
                <div class="empty-state-wrapper">
                    <div class="empty-state-icon">😴</div>
                    <h5 class="fw-bold text-secondary mb-1">No datasets found</h5>
                    <p class="text-muted small mb-0">Your workspace is empty. Drop a file above to start processing!</p>
                </div>
            `;
            return;
        }

        // Si la API devuelve un array con elementos...
        if (deleteAllBtn) deleteAllBtn.style.display = "block"; // Mostramos el botón "Delete All"

        // Funciones de renderizado
        renderPagination(data.length);
        renderPagedDatasets(data);

    } catch (error) {
        console.error("Error loading datasets:", error);
    }
}

function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE) || 1;
    const container = document.getElementById("paginationControls");
    container.innerHTML = "";

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement("button");
        btn.className = `btn btn-outline-dark ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.addEventListener("click", () => {
            currentPage = i;
            loadDatasets();
        });
        container.appendChild(btn);
    }
}

function renderPagedDatasets(allDatasets) {
    const container = document.getElementById("datasetList");

    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pagedData = allDatasets.slice(start, end);

    const visibleIds = new Set(pagedData.map(d => `card-${d.id}`));

    container.style.paddingTop = "20px";

    // Eliminar del DOM solo las tarjetas que cambiaron de página
    Array.from(container.children).forEach(child => {
        if (!visibleIds.has(child.id)) {
            container.removeChild(child);
        }
    });

    // Reconciliación e inyección
    pagedData.forEach(dataset => {
        const cardId = `card-${dataset.id}`;
        let card = document.getElementById(cardId);
        
        const isNewUpload = !knownIds.has(dataset.id) && dataset.status === "processing";
        let needsAnimation = false;

        if (!card) {
            card = document.createElement("div");
            card.id = cardId;
            card.innerHTML = renderDatasetCardTemplate(dataset, isNewUpload);
            needsAnimation = isNewUpload;
        }

        // Insertamos primero la tarjeta en el contenedor
        container.appendChild(card);

        if (needsAnimation) {
            const bar = card.querySelector('.progress-bar');
            
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    if (dataset.status === "processing") {
                        bar.style.width = "50%";
                        setTimeout(() => {
                            if (bar.style.width === "50%") bar.classList.add('bar-processing');
                        }, 2000);
                    } else {
                        bar.style.width = "100%";
                        setTimeout(() => { finalizeCardUI(card, bar, dataset); }, 2000);
                    }
                });
            });
        }

        if (dataset.status === "processing") {
            startPolling(dataset.id);
        }
    });

    // Registramos todos los datasets actuales como conocidos
    allDatasets.forEach(d => knownIds.add(d.id));
    isInitialLoad = false;
}

function startPolling(datasetId) {
    if (activePolls.has(datasetId)) return;
    activePolls.add(datasetId);

    const interval = setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/datasets/${datasetId}`, { cache: "no-store" });
            const data = await res.json();

            if (data.status !== "processing") {
                clearInterval(interval);
                activePolls.delete(datasetId);
                
                advanceProgressBar(datasetId, data);
            }
        } catch (error) {
            clearInterval(interval);
            activePolls.delete(datasetId);
        }
    }, 1500); // Se consulta el estado de los datasets cada 1.5s
}

function advanceProgressBar(id, dataset) {
    const card = document.getElementById(`card-${id}`);
    if (!card) return;

    const bar = card.querySelector('.progress-bar');
    if (!bar) return;

    if (bar.classList.contains('static-processing')) {
        bar.classList.remove('static-processing');
        bar.classList.add('progress-bar-anim', 'bar-processing');
        bar.style.width = "50%"; // Aseguramos que empiece a animar desde la mitad
    }

    bar.style.width = "100%";

    // Esperamos a que la transición de la barra de carga termine para 
    // aplicar color y textos
    setTimeout(() => {
        finalizeCardUI(card, bar, dataset);
    }, 2000);
}

function finalizeCardUI(card, bar, dataset) {
    const loadingText = card.querySelector('.text-loading');
    const finalText = card.querySelector('.text-final');

    if (loadingText) loadingText.style.display = 'none';
    
    if (finalText) {
        finalText.style.display = 'inline';
        
        if (dataset.status === "done") {
            bar.classList.remove('bar-processing');
            bar.classList.add('bar-done');
            finalText.innerText = "Dataset processed!";
            finalText.className = "text-final text-success";
            
            // Habilitar botones de descarga y reporte
            card.querySelectorAll('.btn-actions').forEach(btn => btn.removeAttribute('disabled'));

            card.classList.add('is-done');

        } else {
            bar.classList.remove('bar-processing');
            bar.classList.add('bar-failed');
            finalText.innerText = dataset.error_message || "Failed to process dataset";
            finalText.className = "text-final text-danger";
            
            card.classList.add('is-failed');
        }
    }
}

async function deleteDataset(id) {
    if (!confirm("Are you sure you want to PERMANENTLY delete this dataset?")) return;

    try {
        const res = await fetch(`${API_URL}/datasets/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to delete dataset.");

        knownIds.delete(id);
        loadDatasets();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteAllDatasets(e) {
    if (e) e.preventDefault();

    const confirmDelete = confirm("Are you absolutely sure you want to delete ALL listed datasets? This action cannot be undone.");
    if (!confirmDelete) return;

    try {
        const res = await fetch(`${API_URL}/all_datasets`, { method: "DELETE" });
        if (!res.ok) throw new Error("Failed to clear datasets workspace");
        
        deleteAllBtn.classList.add('success');
        
        // Botón de eliminado masivo
        setTimeout(() => {
            // Reiniciamos a la página 1 y recargamos la interfaz
            currentPage = 1;
            knownIds.clear(); // Limpiamos la caché de IDs animados
            loadDatasets();

            // Eliminamos la flag de éxito para "reiniciar" el estado
            deleteAllBtn.classList.remove('success');
        }, 500);
        
    } catch (err) {
        alert("Error: " + err.message);
    }
}

function downloadDataset(id) { window.open(`${API_URL}/datasets/${id}/download`); }
function goToReport(id) { window.location.href = `report.html?id=${id}`; }

function renderDatasetCardTemplate(dataset, isAnimating) {
    const disabled = dataset.status !== "done" ? "disabled" : "";
    
    let textClass = "text-muted";
    let finalText = "";
    let barClass = "progress-bar-anim";
    let inlineStyle = "width: 0%;";

    // Configuración inicial estática para registros viejos
    if (!isAnimating) {
        if (dataset.status === "done") {
            textClass = "text-success";
            finalText = "Dataset processed!";
            barClass = "static-done";
        } else if (dataset.status === "failed") {
            textClass = "text-danger";
            finalText = dataset.error_message || "Failed to process dataset";
            barClass = "static-failed";
        } else {
            textClass = "text-warning";
            barClass = "static-processing";
        }
    }

    return `
    <div class="glass-card p-3 d-flex align-items-center justify-content-between" style="background-color: #ffffff; border-color: #e2e8f0;">
        <div class="d-flex align-items-center gap-4 flex-grow-1">
            <div class="mac-preview-box">
                <table class="mini-sheet">
                    <tr><td><div class="mini-data-line"></div></td><td><div class="mini-data-line"></div></td></tr>
                    <tr><td><div class="mini-data-line"></div></td><td><div class="mini-data-line"></div></td></tr>
                    <tr><td><div class="mini-data-line"></div></td><td><div class="mini-data-line"></div></td></tr>
                    <tr><td><div class="mini-data-line"></div></td><td><div class="mini-data-line"></div></td></tr>
                </table>
            </div>

            <div class="flex-grow-1 px-md-3">
                <div class="text-truncate fw-bold text-dark mb-1" style="font-size: 0.95rem; max-width: 250px;">
                    ${dataset.filename || 'Untitled dataset'}
                </div>
                <div class="status-text-container fw-bold">
                    <span class="text-loading text-secondary" style="display: ${isAnimating || dataset.status === 'processing' ? 'inline' : 'none'};">
                        Processing<span class="ticker-dots"></span>
                    </span>
                    <span class="text-final ${textClass}" style="display: ${!isAnimating && dataset.status !== 'processing' ? 'inline' : 'none'};">
                        ${finalText}
                    </span>
                </div>
                <div class="progress progress-thin">
                    <div class="progress-bar ${barClass}" style="${isAnimating ? inlineStyle : ''}"></div>
                </div>
            </div>
        </div>

        <div class="d-flex flex-column gap-2 ms-3" style="min-width: 115px;">
            <button class="btn btn-sm btn-outline-dark rounded-pill py-1 fw-medium btn-actions" style="font-size: 11px;"
                onclick="downloadDataset('${dataset.id}')" ${disabled}>
                Download
            </button>
            <button class="btn btn-sm btn-outline-dark rounded-pill py-1 fw-medium btn-actions" style="font-size: 11px;"
                onclick="goToReport('${dataset.id}')" ${disabled}>
                View report
            </button>
            <button class="btn btn-sm btn-outline-danger rounded-pill py-1 fw-medium" style="font-size: 11px;"
                onclick="deleteDataset('${dataset.id}')">
                Delete
            </button>
        </div>
    </div>
    `;
}

function setupBinsRestrictions() {
    const binsInput = document.getElementById("histogramBins");
    
    if (binsInput) {
        binsInput.addEventListener("change", () => {
            let value = parseInt(binsInput.value, 10);
            
            // Si no es un número válido o es menor que 5, forzamos el mínimo (5)
            if (isNaN(value) || value < 5) {
                binsInput.value = 5;
            } 
            // Si es mayor que 50, forzamos el máximo (50)
            else if (value > 50) {
                binsInput.value = 50;
            }
        });
    }
}