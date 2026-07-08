import logging

logger = logging.getLogger(__name__)

def validate_dataset(df):

    logger.info("Validando dataset...")

    report = {}

    # filas y columnas
    report["rows"] = int(df.shape[0])
    report["columns"] = int(df.shape[1])

    # duplicados
    report["duplicate_rows"] = int(df.duplicated().sum())

    # nulos totales
    report["missing_values"] = int(df.isnull().sum().sum())

    return report