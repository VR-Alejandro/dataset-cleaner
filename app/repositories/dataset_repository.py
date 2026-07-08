from uuid import UUID
from datetime import datetime

class DatasetRepository:
    def __init__(self):
        self._datasets = {}

    def create(self, dataset_id: UUID):
        dataset = {
            "id": dataset_id,
            "status": "uploaded",
            "created_at": datetime.now(),
            "results": None,
            "cleaned_file_path": None
        }
        self._datasets[dataset_id] = dataset
        return dataset

    def get(self, dataset_id: UUID):
        return self._datasets.get(dataset_id)
    
    def update_status(self, dataset_id: UUID, status: str):
        if dataset_id in self._datasets:
            self._datasets[dataset_id]["status"] = status

        return None
    
    def save_results(self, dataset_id: UUID, results):
        if dataset_id in self._datasets:
            self._datasets[dataset_id]["results"] = results

    def save_cleaned_file_path(self, dataset_id: UUID, file_path: str):
        if dataset_id in self._datasets:
            self._datasets[dataset_id]["cleaned_file_path"] = file_path