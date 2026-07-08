from pathlib import Path
import json

def save_report(
    report: dict, 
    output_path: str
) -> Path:
    """
    Guarda el informe de validación en formato JSON.

    Parameters
    ----------
    report
        Informe de validación.

    output_path
        Ruta donde guardar el informe.

    Returns
    -------
    Path
        Ruta completa del fichero generado.
    """
    
    target_dir = Path(output_path)
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / "report.json"

    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)

    return output_path