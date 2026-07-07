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
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)

    return output_path