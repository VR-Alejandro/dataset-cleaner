from app.schemas.dataset import DatasetStatus
from processing.pipeline import process_dataset

import time
from threading import Thread
import os
from pathlib import Path

def process_dataset_async(dataset_id, repo):
    thread = Thread(target=_process_dataset, args=(dataset_id, repo))
    thread.start()


def _process_dataset(dataset_id, repo):
    
    # Cambio de estado y procesamiento del input
    repo.update_status(dataset_id, DatasetStatus.processing)

    dataset = repo.get(dataset_id)


    input_path = Path(dataset["input_path"]) 
    output_dir = Path("outputs") / str(dataset_id)

    result = process_dataset(
        input_path=input_path,
        output_directory=output_dir,
    )

    # Guardamos los resultados
    repo.save_cleaned_file_path(dataset_id, result.cleaned_dataset_path)
    repo.save_results(dataset_id, result.metrics)
    repo.update_status(dataset_id, "done")