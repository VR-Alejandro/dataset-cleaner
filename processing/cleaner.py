import pandas as pd
import logging
from processing.exceptions import CleaningError

logger = logging.getLogger(__name__)

VALID_NUMERIC_STRATEGIES = {"keep", "drop", "mean"}
VALID_CATEGORICAL_STRATEGIES = {"keep", "drop", "mode"}


def clean_dataset(df, config):

    logger.info("Cleaning dataset...")

    df_clean = df.copy()

    # Eliminar duplicados
    before_dup = df_clean.shape[0]
    df_clean = df_clean.drop_duplicates()
    after_dup = df_clean.shape[0]

    logger.info(f"Duplicates removed: {before_dup - after_dup}")

    # Tratamiento de nulos
    before_nulls = df_clean.isnull().sum().sum()

    numeric_cols = df_clean.select_dtypes(include="number").columns
    categorical_cols = df_clean.select_dtypes(include="object").columns

    numeric_strategy = config.get("numeric_missing", "keep")
    categorical_strategy = config.get("categorical_missing", "keep")

    # Validación de estrategias
    if numeric_strategy not in VALID_NUMERIC_STRATEGIES:
        raise CleaningError(
            f"Invalid numeric strategy: '{numeric_strategy}'. "
            f"Available options: {sorted(VALID_NUMERIC_STRATEGIES)}"
        )

    if categorical_strategy not in VALID_CATEGORICAL_STRATEGIES:
        raise CleaningError(
            f"Invalid categorical strategy: '{categorical_strategy}'. "
            f"Available options: {sorted(VALID_CATEGORICAL_STRATEGIES)}"
        )

    # Columnas numéricas
    if numeric_strategy == "drop":
        df_clean = df_clean.dropna(subset=numeric_cols)

    elif numeric_strategy == "mean":
        for col in numeric_cols:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())

    # Columnas categóricas
    if categorical_strategy == "drop":
        df_clean = df_clean.dropna(subset=categorical_cols)

    elif categorical_strategy == "mode":
        for col in categorical_cols:
            mode_value = df_clean[col].mode()

            if not mode_value.empty:
                df_clean[col] = df_clean[col].fillna(mode_value[0])

    # Resultado
    after_nulls = df_clean.isnull().sum().sum()

    logger.info(f"Missing values before: {before_nulls}")
    logger.info(f"Missing values after: {after_nulls}")
    logger.info(f"Numeric strategy: {numeric_strategy}")
    logger.info(f"Categorical strategy: {categorical_strategy}")

    return df_clean