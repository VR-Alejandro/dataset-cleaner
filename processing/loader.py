import pandas as pd
import os
from processing.exceptions import DatasetLoadError

def load_dataset(path: str):

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    extension = os.path.splitext(path)[1].lower()

    try:

        if extension == ".csv":
             
            encodings = [
                "utf-8",
                "utf-8-sig",
                "latin1",
                "cp1252",
            ]

            for encoding in encodings:
                try:
                    df = pd.read_csv(path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise DatasetLoadError(
                    "Unable to read CSV. Unsupported file encoding."
                )

        elif extension in [".xlsx", ".xls"]:
            df = pd.read_excel(path)

        else:
            raise ValueError(
                f"Unsupported format '{extension}'. Please use CSV or Excel."
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

