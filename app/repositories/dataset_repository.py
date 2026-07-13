import sqlite3
from app.domain.dataset import Dataset
from app.core.db import get_connection
from uuid import UUID
from datetime import datetime


class DatasetRepository:
    def __init__(self):
        self._datasets = {}

    def create(self, dataset_id: UUID, input_path: str = None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO datasets (
                id, status, input_path, created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (str(dataset_id), "uploaded", str(input_path), datetime.now())
        )
        conn.commit()
        conn.close()

    def get(self, dataset_id: UUID) -> Dataset:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM datasets WHERE id = ?",
            (str(dataset_id),)
        )
        row = cursor.fetchone()
        conn.close()

        return Dataset(
            id=row[0],
            status=row[1],
            input_path=row[2],
            cleaned_path=row[3],
            report_path=row[4],
            created_at=row[5],
            error_type=row[6],
            error_message=row[7],
        )
    
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