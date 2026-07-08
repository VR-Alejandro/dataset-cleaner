from pathlib import Path
import pandas as pd
from processing.exceptions import CleanedDatasetGenerationError


def save_csv(
    df: pd.DataFrame,
    output_directory: Path,
) -> Path:
    """
    Guarda el dataset limpio en formato CSV.

    Parameters
    ----------
    df
        Dataset limpio.

    output_directory
        Directorio donde guardar el CSV.

    Returns
    -------
    Path
        Ruta completa del fichero generado.
    """

    try:
        output_directory.mkdir(parents=True, exist_ok=True)

        file_path = output_directory / "cleaned.csv"

        df.to_csv(file_path, index=False)

        return file_path

    except Exception as e:
        raise CleanedDatasetGenerationError(f"Error saving cleaned dataset: {e}.")