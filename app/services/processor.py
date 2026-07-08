from app.schemas.dataset import DatasetStatus, DatasetResultsResponse, SummaryStats

import time
from threading import Thread
import os

def process_dataset_async(dataset_id, repo):
    thread = Thread(target=_process_dataset, args=(dataset_id, repo))
    thread.start()


def _process_dataset(dataset_id, repo):
    # 1. cambiar a processing
    repo.update_status(dataset_id, DatasetStatus.processing)

    # 2. simular trabajo pesado
    time.sleep(5)

    # Creamos un fichero fake
    file_path = f"cleaned_{dataset_id}.csv"
    with open(file_path, "w") as f:
        f.write("col1,col2\n1,2\n3,4\n")

    repo.save_cleaned_file_path(dataset_id, file_path)
    
    # 3. Insertamos resultados simulados
    results = DatasetResultsResponse(
        summary=SummaryStats(row_count=100, column_count=10)
    )
    repo.save_results(dataset_id, results)

    # 4. terminar
    repo.update_status(dataset_id, "done")