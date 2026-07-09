from dataclasses import dataclass
from pathlib import Path
from typing import Any

from processing.loader import load_dataset
from processing.validation import validate_dataset
from processing.statistics import generate_statistics
from processing.insights import generate_insights
from processing.cleaner import clean_dataset
from processing.save_csv import save_csv
from processing.report import save_report


DEFAULT_CONFIG = {
    "numeric_missing": "mean",
    "categorical_missing": "mode",
}


@dataclass(slots=True)
class ProcessingResult:
    cleaned_dataset_path: Path
    report_path: Path
    metrics: dict[str, Any]


def process_dataset(
    input_path: Path,
    output_directory: Path,
    config: dict[str, str] | None = None,
) -> ProcessingResult:
    """
    Runs the complete dataset processing pipeline.

    Parameters
    ----------
    input_path
        Path to the input file (CSV or Excel).

    output_directory
        Directory where the output files will be saved.

    config
        Optional cleaning configuration.
    """

    if config is None:
        config = DEFAULT_CONFIG

    # --------------------------------------------------------
    # Cargar dataset
    # --------------------------------------------------------

    df = load_dataset(input_path)

    # --------------------------------------------------------
    # Validación
    # --------------------------------------------------------

    report = validate_dataset(df)

    # --------------------------------------------------------
    # Limpieza
    # --------------------------------------------------------

    df_clean = clean_dataset(df, config)

    report["missing_values"] = {
        "before": int(df.isnull().sum().sum()),
        "after": int(df_clean.isnull().sum().sum()),
    }

    report["duplicate_rows"] = {
        "before": int(df.duplicated().sum()),
        "after": int(df_clean.duplicated().sum()),
    }

    report["cleaning_config"] = config

    # --------------------------------------------------------
    # Estadísticas
    # --------------------------------------------------------

    stats = generate_statistics(df_clean)

    report["basic_statistics"] = stats

    # --------------------------------------------------------
    # Insights
    # --------------------------------------------------------

    insights = generate_insights(df, df_clean, stats)

    report["insights"] = insights

    # --------------------------------------------------------
    # Guardado de resultados
    # --------------------------------------------------------

    cleaned_dataset_path = save_csv(
        df_clean,
        output_directory,
    )
    report_path = save_report(
        report,
        output_directory
    )

    return ProcessingResult(
        cleaned_dataset_path=cleaned_dataset_path,
        report_path=report_path,
        metrics=report,
    )