const API_URL = "http://localhost:8000";

let currentPage = 1;
const ITEMS_PER_PAGE = 6;
const knownIds = new Set();      // Guarda los IDs que ya existen
const activePolls = new Set();   // Evita duplicar bucles de intervalos de escucha
let isInitialLoad = true;        // Flag para el primer encendido de la app

let fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const uploadBtn = document.getElementById("uploadBtn");
const clearBtn = document.getElementById("clearBtn");

// Función para enlazar los eventos del input de archivos
function setupFileInputListeners() {
    fileInput.addEventListener("change", (e) => updateDropzoneText(e.target.files[0]));
}

uploadBtn.addEventListener("click", uploadFile);
clearBtn.addEventListener("click", clearDropzone);
dropzone.addEventListener("click", () => fileInput.click());

// Inicializar la primera escucha
setupFileInputListeners();

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
    const nullStrategyInput = document.getElementById("nullStrategy");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file before submitting.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("null_strategy", nullStrategyInput.value);

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
        const res = await fetch(`${API_URL}/datasets`);
        const data = await res.json();

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

    // 1. Eliminar del DOM solo las tarjetas que cambiaron de página
    Array.from(container.children).forEach(child => {
        if (!visibleIds.has(child.id)) {
            container.removeChild(child);
        }
    });

    // 2. Reconciliación e inyección
    pagedData.forEach(dataset => {
        const cardId = `card-${dataset.id}`;
        let card = document.getElementById(cardId);

        const isNewUpload = !knownIds.has(dataset.id) && !isInitialLoad;

        if (!card) {
            card = document.createElement("div");
            card.id = cardId;
            
            if (isNewUpload) {
                // Estado inicial de animación
                card.innerHTML = renderDatasetCardTemplate(dataset, true);
                
                // Forzar el inicio de la transición fluida tras montarse en el DOM
                setTimeout(() => {
                    const bar = card.querySelector('.progress-bar');
                    if (dataset.status === "processing") {
                        bar.style.width = "50%";
                        setTimeout(() => {
                            if (bar.style.width === "50%") bar.classList.add('bar-processing');
                        }, 2000);
                    } else {
                        bar.style.width = "100%";
                        setTimeout(() => { finalizeCardUI(card, bar, dataset); }, 2000);
                    }
                }, 50);
            } else {
                card.innerHTML = renderDatasetCardTemplate(dataset, false);
            }
        }

        // Garantizamos que los elementos sigan estrictamente el orden del array, 
        // empujando el nuevo arriba.
        container.appendChild(card);

        // Activamos el polling frecuente si el estado actual es processing
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
            const res = await fetch(`${API_URL}/datasets/${datasetId}`);
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

    bar.className = "progress-bar progress-bar-anim";
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
            bar.classList.add('bar-done');
            finalText.innerText = "Dataset processed!";
            finalText.className = "text-final text-success";
            
            // Habilitar botones de descarga y reporte
            card.querySelectorAll('.btn-actions').forEach(btn => btn.removeAttribute('disabled'));

            card.classList.add('is-done');

        } else {
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

function downloadDataset(id) { window.open(`${API_URL}/datasets/${id}/download`); }
function goToReport(id) { window.location.href = `reporte.html?id=${id}`; }

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