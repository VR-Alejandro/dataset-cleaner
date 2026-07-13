import pandas as pd
import numpy as np

def generate_statistics(df: pd.DataFrame):

    stats = {
        "numeric": {},
        "categorical": {}
    }

    for col in df.columns:

        # numéricas
        if pd.api.types.is_numeric_dtype(df[col]):

            hist_counts, hist_bins = np.histogram(df[col].dropna(), bins=10)

            stats["numeric"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "quartiles": {
                    "q1": float(df[col].quantile(0.25)),
                    "q2": float(df[col].quantile(0.50)),
                    "q3": float(df[col].quantile(0.75))
                },
                "histogram": {
                    "bins": hist_bins.tolist(),
                    "counts": hist_counts.tolist()
                }
            }

        # categóricas
        else:

            stats["categorical"][col] = {
                "unique_values": int(df[col].nunique()),
                "top_value": df[col].mode()[0] if not df[col].mode().empty else None,
                "frequencies": df[col].value_counts().head(10).to_dict()
            }

    return stats