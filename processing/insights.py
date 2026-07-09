import pandas as pd

def generate_insights(df_raw: pd.DataFrame, df_clean: pd.DataFrame, stats: dict):

    insights = []

    # Nulos
    raw_nulls = df_raw.isnull().sum().sum()
    clean_nulls = df_clean.isnull().sum().sum()

    if raw_nulls == 0:
        insights.append("No missing values detected in the original dataset.")
    elif clean_nulls == 0:
        insights.append(
            f"All {raw_nulls} missing values were successfully removed or imputed."
        )
    else:
        insights.append(
            f"Missing values were reduced from {raw_nulls} to {clean_nulls} after cleaning."
        )

    # Duplicados
    raw_duplicates = df_raw.duplicated().sum()
    clean_duplicates = df_clean.duplicated().sum()

    if raw_duplicates == 0:
        insights.append("No duplicate rows detected in the original dataset.")
    elif clean_duplicates == 0:
        insights.append(
            f"All {raw_duplicates} duplicate rows were successfully removed."
        )
    else:
        insights.append(
            f"{clean_duplicates} duplicate rows remain after cleaning."
        )

    # Variabilidad de columnas numéricas
    numeric_cols = df_clean.select_dtypes(include="number").columns

    for col in numeric_cols:
        std = df_clean[col].std()

        if std == 0:
            insights.append(f"Column '{col}' shows no variability.")
        elif std < df_clean[col].mean() * 0.1:
            insights.append(f"Column '{col}' shows low variability.")
        else:
            insights.append(f"Column '{col}' shows normal variability.")

    return insights