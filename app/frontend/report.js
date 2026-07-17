const API_URL = "http://localhost:8000";

// Extraer el ID del dataset de la URL
const urlParams = new URLSearchParams(window.location.search);
const datasetId = urlParams.get('id');

// Variables de estado global
let currentReportData = null;
let distributionChart = null;
let currentView = 'chart';  // Vista por defecto
let currentVarName = null;
let currentVarType = null;

// Inicialización cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    if (!datasetId) {
        alert("Error: No dataset ID provided.");
        window.location.href = "index.html";
        return;
    }

    loadReportData();
    setupDownloadButtons();
    setupViewToggles();
});

// Traemos los datos del backend
async function loadReportData() {
    try {
        const response = await fetch(`${API_URL}/datasets/${datasetId}/results`, { cache: "no-store" });
        
        if (!response.ok) throw new Error("Failed to fetch report data");
        
        const data = await response.json();
        currentReportData = data;
        
        // Mapear los datos a la interfaz
        renderKPIs(data);
        renderVariables(data);
        renderInsights(data);
        renderHeatmap(data);
        
        let filename;
        try {
            filename = await loadInfoDataset();
        } catch {
            filename = null;
        }

        document.getElementById("reportFilename").innerText =
            filename || `dataset_${datasetId.substring(0,8)}.csv`;

    } catch (error) {
        console.error("Error loading report:", error);
        alert("Could not load the dataset report.");
    }
}

async function loadInfoDataset() {
    try {
        const response = await fetch(`${API_URL}/datasets/${datasetId}`, { cache: "no-store" });

        if (!response.ok) throw new Error("HTTP error: ${response.status}");

        const data = await response.json();

        // Validación explícita del contrato
        if (
            typeof data !== "object" ||
            typeof data.filename !== "string"
        ) {
            throw new Error("Invalid DatasetResponse shape");
        }

        return data.filename;


    } catch (error) {
        console.error("Error loading dataset:", error);
        throw error;
    }
}

// Renderizar los KPIs superiores
function renderKPIs(data) {
    // Dimensiones
    document.getElementById("kpiShape").innerHTML = `<span>${data.rows} <span class="fs-5 text-muted">× ${data.columns}</span></span>`;
    
    // Duplicados eliminados (calculado: before - after)
    const duplicatesRemoved = data.duplicate_rows.before - data.duplicate_rows.after;
    document.getElementById("kpiDuplicates").innerText = duplicatesRemoved;
    
    // Valores nulos resueltos (calculado: before - after)
    const missingResolved = data.missing_values.before - data.missing_values.after;
    document.getElementById("kpiMissing").innerText = missingResolved;
    
    // Estrategias de limpieza
    const numStrategy = data.cleaning_config.numeric_missing;
    const catStrategy = data.cleaning_config.categorical_missing;
    
    document.getElementById("kpiConfigNum").innerText = `Num: ${capitalize(numStrategy)}`;
    document.getElementById("kpiConfigCat").innerText = `Cat: ${capitalize(catStrategy)}`;
}

// Renderizar la lista del explorador de variables
function renderVariables(data) {
    const listContainer = document.getElementById("variableList");
    listContainer.innerHTML = ""; 
    
    let isFirst = true; // Para saber cuál es la primera variable y graficarla por defecto

    // Función auxiliar para crear botones
    const createButton = (varName, type) => {
        const btn = document.createElement("button");
        const typeClass = type === 'num' ? 'type-num' : 'type-cat';
        const typeLabel = type === 'num' ? 'Num' : 'Cat';
        
        btn.className = `var-btn ${isFirst ? 'active' : ''}`;
        btn.innerHTML = `${varName} <span class="var-type ${typeClass}">${typeLabel}</span>`;
        
        // Cambio de clase activa y actualización de gráfico
        btn.addEventListener("click", () => {
            // Quitar clase activa de todos los botones
            document.querySelectorAll(".var-btn").forEach(b => b.classList.remove("active"));
            // Añadir al botón actual
            btn.classList.add("active");

            currentVarName = varName;
            currentVarType = type;

            // Renderizamos los dos contenedores
            renderChart(varName, type, data);
            renderStats(varName, type, data);
            updateViewVisibility();
        });

        listContainer.appendChild(btn);

        
        if (isFirst) {
            // Inicialización de estados
            currentVarName = varName;
            currentVarType = type;
            renderChart(varName, type, data);
            renderStats(varName, type, data);
            updateViewVisibility();
            isFirst = false;
        }
    };

    // Iterar sobre numéricas
    if (data.basic_statistics.numeric) {
        Object.keys(data.basic_statistics.numeric).forEach(varName => {
            if (isIdVariable(varName)) return;
            createButton(varName, 'num');
        });
    }
    
    // Iterar sobre categóricas
    if (data.basic_statistics.categorical) {
        Object.keys(data.basic_statistics.categorical).forEach(varName => {
            if (isIdVariable(varName)) return;
            createButton(varName, 'cat');
        });
    }
}

// Renderizar los insights automáticos
function renderInsights(data) {
    const insightsContainer = document.getElementById("insightsContainer");
    insightsContainer.innerHTML = ""; // Limpiar estado previo estático
    
    const insights = data.insights || [];

    // Obtenemos todas las columnas que clasifican como IDs
    const idColumns = [];
    if (data.basic_statistics?.numeric) {
        Object.keys(data.basic_statistics.numeric).forEach(col => {
            if (isIdVariable(col)) idColumns.push(col);
        });
    }
    if (data.basic_statistics?.categorical) {
        Object.keys(data.basic_statistics.categorical).forEach(col => {
            if (isIdVariable(col)) idColumns.push(col);
        });
    }

    // Filtramos los insights que hagan mención a columnas de tipo ID
    const filteredInsights = insights.filter(insightText => {
        const mentionsId = idColumns.some(idCol => {
            // Coincidencia si viene entre comillas...
            if (insightText.includes(`'${idCol}'`) || insightText.includes(`"${idCol}"`)) {
                return true;
            }
            
            // Coincidencia por palabra exacta...
            const escapedCol = idCol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const wordBoundaryRegex = new RegExp(`\\b${escapedCol}\\b`, 'i');
            
            return wordBoundaryRegex.test(insightText);
        });

        // Solo nos quedamos con el insight si NO menciona ningún ID
        return !mentionsId;
    });

    if (filteredInsights.length > 0) {
        filteredInsights.forEach(insightText => {
            const item = document.createElement("div");
            item.className = "insight-item";
            item.innerHTML = `
                <div class="insight-icon">✦</div>
                <div>${insightText}</div>
            `;
            insightsContainer.appendChild(item);
        });
    } else {
        insightsContainer.innerHTML = `<div class="text-muted small">No insights available for this dataset.</div>`;
    }
}

// Configurar lógica de descargas
function setupDownloadButtons() {
    const btnJson = document.getElementById("btnDownloadJson");
    const btnCsv = document.getElementById("btnDownloadCsv");

    // Descargar el JSON directamente desde la variable almacenada en memoria
    btnJson.addEventListener("click", () => {
        if (!currentReportData) return;
        
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentReportData, null, 4));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href",     dataStr);
        downloadAnchorNode.setAttribute("download", `report.json`);
        document.body.appendChild(downloadAnchorNode); // Firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    });

    // Descarga del dataset limpio
    btnCsv.addEventListener("click", () => {
        window.open(`${API_URL}/datasets/${datasetId}/download`, '_blank');
    });
}

// Helper para capitalizar textos
function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function renderChart(varName, type, data) {
    // 1. Actualizamos el título de la sección
    document.getElementById("chartTitle").innerText = `Distribution: ${varName}`;

    let labels = [];
    let values = [];
    let barColor = '';

    // 2. Extraemos los datos según el tipo de variable
    if (type === 'num') {
        const stats = data.basic_statistics.numeric[varName];
        barColor = 'rgba(139, 92, 246, 0.7)'; // Numéricas en morado
        
        // Recuperamos el histograma desde el backend
        if (stats.histogram) {
            const bins = stats.histogram.bins;
            const counts = stats.histogram.counts;
            for (let i = 0; i < counts.length; i++) {
                // Formateo a 2 decimales
                labels.push(`${Number(bins[i]).toFixed(2)} - ${Number(bins[i+1]).toFixed(2)}`);
                values.push(counts[i]);
            }
        } 
    } else {
        const stats = data.basic_statistics.categorical[varName];
        barColor = 'rgba(245, 158, 11, 0.7)'; // Categóricas en naranja
        
        // Recuperamos las frecuencias desde el backend
        if (stats.frequencies) {
            labels = Object.keys(stats.frequencies);
            values = Object.values(stats.frequencies);
        }
    }

    // 3. Destrucción del gráfico anterior si existe
    if (distributionChart) {
        distributionChart.destroy();
    }

    // 4. Creamos la nueva instancia de Chart.js
    const ctx = document.getElementById('distributionChart').getContext('2d');
    distributionChart = new Chart(ctx, {
        type: 'bar', // Gráfico de barras para frecuencias
        data: {
            labels: labels,
            datasets: [{
                label: 'Frecuencia (Nº Filas)',
                data: values,
                backgroundColor: barColor,
                borderRadius: 4,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#f1f5f9'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Renderizar el mapa de calor
function renderHeatmap(data) {
    const wrapper = document.getElementById("heatmapWrapper");
    wrapper.innerHTML = ""; 

    // Extraemos la matriz de su ubicación en basic_statistics
    const corrMatrixData = data.basic_statistics?.correlation_matrix;

    if (!corrMatrixData) {
        wrapper.innerHTML = '<div class="text-muted text-center mt-5">No correlation data available.</div>';
        return;
    }

    // Variables a incluir (filtrando variables identificadoras)
    const variables = Object.keys(corrMatrixData).filter(v => !isIdVariable(v));

    if (variables.length === 0) {
        wrapper.innerHTML = '<div class="text-muted text-center mt-5">No numeric variables available for correlation.</div>';
        return;
    }

    wrapper.style.border = "none";
    wrapper.style.background = "transparent";

    const gridSize = variables.length + 1;
    const grid = document.createElement('div');
    grid.className = 'heatmap-grid';
    grid.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
    grid.style.gridTemplateRows = `repeat(${gridSize}, 1fr)`;

    grid.appendChild(document.createElement('div')); // Espacio vacío esquina

    // Generar cabeceras eje X
    variables.forEach(v => {
        const label = document.createElement('div');
        label.className = 'heatmap-label';
        label.innerText = v.length > 9 ? v.substring(0,7) + '..' : v;
        label.title = v; 
        grid.appendChild(label);
    });

    // Generar filas y celdas
    for (let i = 0; i < variables.length; i++) {
        const varY = variables[i];
        
        const rowLabel = document.createElement('div');
        rowLabel.className = 'heatmap-label';
        rowLabel.innerText = varY.length > 9 ? varY.substring(0,7) + '..' : varY;
        rowLabel.title = varY;
        grid.appendChild(rowLabel);

        for (let j = 0; j < variables.length; j++) {
            const varX = variables[j];
            // Leemos el diccionario cruzando clave Y con clave X
            const value = corrMatrixData[varY][varX]; 
            
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            cell.innerText = value.toFixed(2);
            cell.title = `${varY} vs ${varX}\nCorrelation: ${value.toFixed(2)}`;

            const alpha = Math.abs(value); 
            if (value > 0) {
                cell.style.backgroundColor = `rgba(59, 130, 246, ${alpha})`;
            } else {
                cell.style.backgroundColor = `rgba(239, 68, 68, ${alpha})`;
            }

            cell.style.color = alpha > 0.45 ? '#ffffff' : '#334155';
            grid.appendChild(cell);
        }
    }

    wrapper.appendChild(grid);
}


// Configura los clics de los botones de la esquina superior derecha (Chart / Stats)
function setupViewToggles() {
    const btnChart = document.getElementById("btnViewChart");
    const btnStats = document.getElementById("btnViewStats");

    btnChart.addEventListener("click", () => {
        currentView = 'chart';
        updateViewVisibility();
    });

    btnStats.addEventListener("click", () => {
        currentView = 'stats';
        updateViewVisibility();
    });
}

// Sincroniza la visibilidad en el DOM según el estado seleccionado
function updateViewVisibility() {
    const canvas = document.getElementById("distributionChart");
    const statsContainer = document.getElementById("statsViewContainer");
    const btnChart = document.getElementById("btnViewChart");
    const btnStats = document.getElementById("btnViewStats");

    if (currentView === 'chart') {
        canvas.classList.remove("d-none");
        statsContainer.classList.add("d-none");
        btnChart.classList.add("active");
        btnStats.classList.remove("active");
    } else {
        canvas.classList.add("d-none");
        statsContainer.classList.remove("d-none");
        btnChart.classList.remove("active");
        btnStats.classList.add("active");
        
        // Refrescar los datos tabulados por seguridad
        if (currentVarName && currentVarType && currentReportData) {
            renderStats(currentVarName, currentVarType, currentReportData);
        }
    }
}

// Construye tablas estadísticas limpias a partir de la información del JSON
function renderStats(varName, type, data) {
    const container = document.getElementById("statsViewContainer");
    container.innerHTML = "";
    let htmlContent = "";

    if (type === 'num') {
        const stats = data.basic_statistics.numeric[varName];
        htmlContent = `
            <div class="animate-fade-in">
                <table class="table table-hover align-middle mb-0" style="font-size: 0.95rem;">
                    <tbody>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Mean</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.mean !== undefined ? stats.mean.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Median / Q2</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.median !== undefined ? stats.median.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <!-- 🌟 NUEVO: Cuartiles extraídos del nuevo JSON -->
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Q1</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.quartiles ? stats.quartiles.q1.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Q3</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.quartiles ? stats.quartiles.q3.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Standard deviation (Std)</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.std !== undefined ? stats.std.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Min. value</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.min !== undefined ? stats.min.toFixed(4) : 'N/A'}</td>
                        </tr>
                        <tr style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Max. value</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.max !== undefined ? stats.max.toFixed(4) : 'N/A'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    } else {
        const stats = data.basic_statistics.categorical[varName];
        htmlContent = `
            <div class="animate-fade-in">
                <table class="table table-hover align-middle mb-0" style="font-size: 0.95rem;">
                    <tbody>
                        <tr class="border-bottom" style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Unique Values</td>
                            <td class="text-end py-3 fw-bold text-dark">${stats.unique_values !== undefined ? stats.unique_values : 'N/A'}</td>
                        </tr>
                        <tr style="border-color: rgba(255, 255, 255, 0.6);">
                            <td class="text-muted py-3 fw-semibold">Top Value</td>
                            <td class="text-end py-3 fw-bold text-dark text-truncate" style="max-width: 250px;" title="${stats.top_value}">
                                ${stats.top_value !== undefined ? stats.top_value : 'N/A'}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
    }

    container.innerHTML = htmlContent;
}

function isIdVariable(name) {
    if (!name || typeof name !== 'string') return false;

    // 1. Normalización
    const normalized = name
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, ' ') // cualquier separador → espacio
        .replace(/\s+/g, ' ');

    // 2. Tokenización
    const tokens = normalized.split(' ');

    // 3. Regla semántica principal
    if (tokens.includes('id')) return true;

    // 4. Fallback camelCase / PascalCase
    const camelCaseRegex = /(?:^|[a-z0-9])(id)(?:[A-Z]|$)/i;
    if (camelCaseRegex.test(name)) return true;

    return false;
}