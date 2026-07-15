import sqlite3
from app.domain.dataset import Dataset
from app.core.db import get_connection
from uuid import UUID
from datetime import datetime
from pathlib import Path
import shutil
import logging

logger = logging.getLogger(__name__)

RAW_BASE = Path("data/raw")
OUTPUTS_BASE = Path("outputs")

class DatasetRepository:
    def __init__(self):
        self._datasets = {}

    def create(
            self, 
            dataset_id: UUID, 
            input_path: str = None, 
            filename: str = None, 
            numerical_missing: str = "mean", 
            categorical_missing: str = "mode", 
            histogram_bins: int = 10
        ):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO datasets (
                id, filename, status, input_path, created_at, numerical_missing, categorical_missing, histogram_bins
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(dataset_id), 
             filename, 
             "uploaded", 
             str(input_path), 
             datetime.now(), 
             numerical_missing, 
             categorical_missing, 
             histogram_bins
            )
        )
        conn.commit()
        conn.close()

    def delete(self, dataset_id: UUID):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM datasets
            WHERE id = ?
            """,
            (str(dataset_id),)
        )
        conn.commit()
        conn.close()

    def delete_all(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM datasets
            """
        )
        conn.commit()
        conn.close()

    def get(self, dataset_id: UUID) -> Dataset:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (str(dataset_id),)
        )
        row = cursor.fetchone()
        conn.close()

        return self._map_row_to_dataset(row)
    
    def update_status(self, dataset_id: UUID, status: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE datasets
            SET status = ?
            WHERE id = ?
            """,
            (status, str(dataset_id))
        )
        conn.commit()
        conn.close()
    
    def save_results(self, dataset_id: UUID, cleaned_path: str, report_path: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE datasets
            SET cleaned_path = ?, report_path = ?
            WHERE id = ?
            """,
            (str(cleaned_path), str(report_path), str(dataset_id))
        )
        conn.commit()
        conn.close()

    def save_error(self, dataset_id: UUID, error_type: str, error_message: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE datasets
            SET error_type = ?, error_message = ?
            WHERE id = ?
            """,
            (error_type, error_message, str(dataset_id))
        )
        conn.commit()
        conn.close()

    def _map_row_to_dataset(self, row) -> Dataset:
        """Función auxiliar para mapear una fila de la base de datos a un objeto Dataset."""
        return Dataset(
            id=row["id"],
            filename=row["filename"],
            status=row["status"],
            numerical_missing=row["numerical_missing"] if row["numerical_missing"] else "mean",
            categorical_missing=row["categorical_missing"] if row["categorical_missing"] else "mode",
            histogram_bins=row["histogram_bins"] if row["histogram_bins"] else 10,
            input_path=Path(row["input_path"]) if row["input_path"] else None,
            cleaned_path=Path(row["cleaned_path"]) if row["cleaned_path"] else None,
            report_path=Path(row["report_path"]) if row["report_path"] else None,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            error_type=row["error_type"],
            error_message=row["error_message"],
        )
    
    def list(self, limit: int = 50, offset: int = 0):
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM datasets
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._map_row_to_dataset(row) for row in rows]
    
    def cleanup_dataset_directories(self, dataset_id):
        dataset_id = str(dataset_id)

        dirs = [
            RAW_BASE / dataset_id,
            OUTPUTS_BASE / dataset_id
        ]

        for directory in dirs:
            try:
                dir_path = directory.resolve()
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    logger.info(f"Directory {directory} deleted successfully.")

            except Exception as e:
                logger.error(f"Error deleting directory {directory}: {e}")
    
    def cleanup_all_artifacts(self):
        for base_dir in [RAW_BASE, OUTPUTS_BASE]:
            try:
                for entry in base_dir.iterdir():
                    try:
                        if entry.is_dir():
                            shutil.rmtree(entry)
                            logger.info(f"Directory {entry} deleted successfully.")
                    except Exception as e:
                        logger.error(f"Error deleting {entry}: {e}")
            except Exception as e:
                logger.error(f"Error scanning {base_dir}: {e}")