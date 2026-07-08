from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.schemas.dataset import DatasetCreateResponse, DatasetResponse, DatasetStatus

from app.repositories.dataset_repository import DatasetRepository
from app.services.processor import process_dataset_async

from uuid import uuid4, UUID
from datetime import datetime
from pathlib import Path
import shutil

repo = DatasetRepository()

router = APIRouter()

DATA_DIR = Path("data/raw")


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.post("/datasets")
def create_dataset(file: UploadFile = File(...)):
    
    # Validación del tipo de archivo
    allowed_extensions = {"csv", "xlsx"}

    file_extension = file.filename.split(".")[-1]
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Fichero no soportado. Utiliza un archivo CSV o XLSX.")
    

    dataset_id = uuid4()
    
    # Construcción de la ruta destino
    dataset_dir = DATA_DIR / str(dataset_id)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    file_path = dataset_dir / f"input.{file_extension}"

    # Creación del directorio (si no existe)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Guardado del input en crudo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Guardado en repo
    repo.create(dataset_id, input_path=str(file_path))

    # Lanzamos el worker
    process_dataset_async(dataset_id, repo)

    return {"id": str(dataset_id)}



@router.get("/datasets/{id}", response_model=DatasetResponse)
def get_dataset(id: UUID):
    dataset = repo.get(id)
    if not dataset:
        raise HTTPException(status_code=404, detail="No se ha encontrado ningún dataset con el ID proporcionado.")
    
    return dataset


@router.get("/datasets/{id}/results")
def get_dataset_results(id: UUID):
    dataset = repo.get(id)

    if not dataset:
        raise HTTPException(status_code=404, detail="No se ha encontrado ningún dataset con el ID proporcionado.")
    
    if dataset["status"] != DatasetStatus.done:
        raise HTTPException(status_code=400, detail="El dataset aún no ha terminado de procesarse. Por favor, inténtelo más tarde.")
    
    return dataset["results"]


@router.get("/datasets/{id}/cleaned")
def get_dataset_cleaned(id: UUID):
    dataset = repo.get(id)

    if not dataset:
        raise HTTPException(status_code=404, detail="No se ha encontrado ningún dataset con el ID proporcionado.")
    
    if dataset["status"] != DatasetStatus.done:
        raise HTTPException(status_code=400, detail="El dataset aún no ha terminado de procesarse. Por favor, inténtelo más tarde.")

    if not dataset["cleaned_file_path"]:
        raise HTTPException(status_code=404, detail="No se ha encontrado ningún archivo limpio para el dataset con el ID proporcionado.")

    return FileResponse(path=dataset["cleaned_file_path"], filename=f"cleaned_{id}.csv")