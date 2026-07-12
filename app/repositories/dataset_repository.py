import sqlite3
from app.domain.dataset import Dataset
from app.core.db import get_connection
from uuid import UUID
from datetime import datetime
from pathlib import Path


class DatasetRepository:
    def __init__(self):
        self._datasets = {}

    def create(self, dataset_id: UUID, input_path: str = None, filename: str = None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO datasets (
                id, filename, status, input_path, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(dataset_id), filename, "uploaded", str(input_path), datetime.now())
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