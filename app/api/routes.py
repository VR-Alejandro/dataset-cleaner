from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.dataset import DatasetCreateResponse, DatasetResponse, DatasetStatus

from app.repositories.dataset_repository import DatasetRepository
from app.services.processor import process_dataset_async

from uuid import uuid4, UUID
from datetime import datetime

repo = DatasetRepository()

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.post("/datasets", response_model=DatasetCreateResponse)
def create_dataset():
    dataset_id = uuid4()
    dataset = repo.create(dataset_id)

    # Lanzamos el procesamiento async
    process_dataset_async(dataset_id, repo)

    return dataset



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