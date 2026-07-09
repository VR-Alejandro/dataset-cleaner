from pathlib import Path
import json
from processing.exceptions import ReportGenerationError

def save_report(
    report: dict, 
    output_path: str
) -> Path:
    """
    Saves the validation report as a JSON file.

    Parameters
    ----------
    report
        Validation report.

    output_path
        Directory where the report will be saved.

    Returns
    -------
    Path
        Full path to the generated file.
    """
    
    try:
        target_dir = Path(output_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        output_path = target_dir / "report.json"

        with open(output_path, "w") as f:
            json.dump(report, f, indent=4)

        return output_path
    
    except Exception as e:
        raise ReportGenerationError(f"Error saving report: {e}.")