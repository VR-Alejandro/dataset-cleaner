import pandas as pd

def generate_insights(df_raw: pd.DataFrame, df_clean: pd.DataFrame, stats: dict):

    insights = []

    # Nulos
    raw_nulls = df_raw.isnull().sum().sum()
    clean_nulls = df_clean.isnull().sum().sum()

    if raw_nulls == 0:
        insights.append("No se detectaron valores nulos en el dataset original.")
    elif clean_nulls == 0:
        insights.append(
            f"Se eliminaron o imputaron correctamente los {raw_nulls} valores nulos del dataset."
        )
    else:
        insights.append(
            f"El dataset redujo los valores nulos de {raw_nulls} a {clean_nulls} tras la limpieza."
        )

    # Duplicados
    raw_duplicates = df_raw.duplicated().sum()
    clean_duplicates = df_clean.duplicated().sum()

    if raw_duplicates == 0:
        insights.append("No se detectaron filas duplicadas en el dataset original.")
    elif clean_duplicates == 0:
        insights.append(
            f"Se eliminaron correctamente las {raw_duplicates} filas duplicadas."
        )
    else:
        insights.append(
            f"Persisten {clean_duplicates} filas duplicadas tras la limpieza."
        )

    # Variabilidad de columnas numéricas
    numeric_cols = df_clean.select_dtypes(include="number").columns

    for col in numeric_cols:
        std = df_clean[col].std()

        if std == 0:
            insights.append(f"La columna '{col}' no presenta variabilidad.")
        elif std < df_clean[col].mean() * 0.1:
            insights.append(f"La columna '{col}' presenta baja variabilidad.")
        else:
            insights.append(f"La columna '{col}' presenta una variabilidad normal.")

    return insights