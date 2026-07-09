import pandas as pd
import os
from processing.exceptions import DatasetLoadError

def load_dataset(path: str):

    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encuentra el archivo: {path}")

    extension = os.path.splitext(path)[1].lower()

    try:

        if extension == ".csv":
            df = pd.read_csv(path)

        elif extension in [".xlsx", ".xls"]:
            df = pd.read_excel(path)

        else:
            raise ValueError(
                f"Formato '{extension}' no soportado. Usa CSV o Excel."
            )

        # Intentar convertir automáticamente columnas numéricas
        for col in df.columns:

            if df[col].dtype == "object":
                df[col] = (
                    df[col]
                    .str.replace("$", "", regex=False)
                    .str.replace("€", "", regex=False)
                    .str.replace("£", "", regex=False)
                )

            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

    except DatasetLoadError as e:
        raise DatasetLoadError(f"Error loading dataset: {e}.")

    return df

