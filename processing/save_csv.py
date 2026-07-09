from pathlib import Path
import pandas as pd
from processing.exceptions import CleanedDatasetGenerationError


def save_csv(
    df: pd.DataFrame,
    output_directory: Path,
) -> Path:
    """
    Saves the cleaned dataset as a CSV file.

    Parameters
    ----------
    df
        Cleaned dataset.

    output_directory
        Directory where the CSV file will be saved.

    Returns
    -------
    Path
        Full path to the generated file.
    """

    try:
        output_directory.mkdir(parents=True, exist_ok=True)

        file_path = output_directory / "cleaned.csv"

        df.to_csv(file_path, index=False)

        return file_path

    except Exception as e:
        raise CleanedDatasetGenerationError(f"Error saving cleaned dataset: {e}.")