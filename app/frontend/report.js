// Leer el ID que mandamos por la URL
const urlParams = new URLSearchParams(window.location.search);
const datasetId = urlParams.get('id');

// Hacer el fetch de tu gráfica / estadísticas
fetch(`http://localhost:8000/datasets/${datasetId}/report`)