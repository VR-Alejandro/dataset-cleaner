from app.schemas.dataset import DatasetStatus
from processing.pipeline import process_dataset
from processing.exceptions import ProcessingError

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

    input_path = Path(dataset.input_path) 
    output_dir = Path("outputs") / str(dataset_id)

    # Definimos el diccionario que enviaremos a la pipeline
    user_config = {
        "numeric_missing": dataset.numerical_missing,
        "categorical_missing": dataset.categorical_missing
    }

    # Número de grupos a graficar en histogramas
    n_groups = dataset.histogram_bins

    try:
        result = process_dataset(
            input_path=input_path,
            output_directory=output_dir,
            config=user_config,
            histogram_groups=n_groups
        )

        # Guardamos los resultados
        repo.save_results(
            dataset_id,
            cleaned_path=result.cleaned_dataset_path,
            report_path=result.report_path
        )
        repo.update_status(dataset_id, DatasetStatus.done)
    
    except ProcessingError as e:
        repo.update_status(dataset_id, DatasetStatus.failed)
        repo.save_error(dataset_id, 
                        e.__class__.__name__,
                        str(e)
                    )

    except Exception as e:
        # Cualquier otro error inesperado 
        repo.update_status(dataset_id, DatasetStatus.failed)
        repo.save_error(dataset_id, 
                        e.__class__.__name__,
                        str(e)
                    )