import pandas as pd

def generate_statistics(df: pd.DataFrame):

    stats = {
        "numeric": {},
        "categorical": {}
    }

    for col in df.columns:

        # numéricas
        if pd.api.types.is_numeric_dtype(df[col]):

            stats["numeric"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max())
            }

        # categóricas
        else:

            stats["categorical"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_value": df[col].mode()[0] if not df[col].mode().empty else None
            }

    return stats