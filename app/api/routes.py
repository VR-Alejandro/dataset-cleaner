from fastapi import APIRouter, HTTPException, UploadFile, File, Response, status
from fastapi.responses import FileResponse
from app.schemas.dataset import DatasetResponse, DatasetStatus

from app.repositories.dataset_repository import DatasetRepository
from app.services.processor import process_dataset_async

from uuid import uuid4, UUID
from pathlib import Path
import shutil
import json

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
        raise HTTPException(
            status_code=400,
            detail="Fichero no soportado. Utiliza un archivo CSV o XLSX."
        )
    

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


@router.delete("/datasets/{id}")
def delete_dataset(id: UUID):
    dataset = repo.get(id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se ha encontrado ningún dataset con el ID proporcionado."
        )
    else:
        # En este endpoint no nos interesa consultar el estado del dataset
        # La eliminación debe estar disponible independientemente de si
        # status = done, processing o failed.
        repo.delete(id)

@router.delete("/all_datasets")
def delete_all_datasets():
    repo.delete_all()


@router.get("/datasets")
def list_datasets(limit: int = 50, offset: int = 0):
    datasets = repo.list(limit=limit, offset=offset)

    return [
        DatasetResponse(
            id=d.id,
            status=d.status,
            created_at=d.created_at,
        )
        for d in datasets
    ]



@router.get("/datasets/{id}", response_model=DatasetResponse)
def get_dataset(id: UUID):
    dataset = repo.get(id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se ha encontrado ningún dataset con el ID proporcionado."
        )
    
    if dataset.status == DatasetStatus.failed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is corrupted."
        )
    
    return dataset


@router.get("/datasets/{id}/results")
def get_dataset_results(id: UUID):
    dataset = repo.get(id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se ha encontrado ningún dataset con el ID proporcionado."
        )
    
    if dataset.status == DatasetStatus.failed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is corrupted."
        )
    
    if dataset.status != DatasetStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El dataset aún no ha terminado de procesarse. Por favor, inténtelo más tarde."
        )
    
    report_path = dataset.report_path
    with open(report_path, "r", encoding="utf-8") as report_file:
        results = report_file.read()
        return Response(
            content=results,
            media_type="application/json"
        )


@router.get("/datasets/{id}/cleaned")
def get_dataset_cleaned(id: UUID):
    dataset = repo.get(id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se ha encontrado ningún dataset con el ID proporcionado."
        )
    
    if dataset.status == DatasetStatus.failed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is corrupted."
        )
    
    if dataset.status != DatasetStatus.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El dataset aún no ha terminado de procesarse. Por favor, inténtelo más tarde."
        )

    if not dataset.cleaned_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se ha encontrado ningún archivo limpio para el dataset con el ID proporcionado."
        )

    return FileResponse(path=dataset.cleaned_path, filename=f"cleaned_{id}.csv")


@router.get("/datasets/{dataset_id}/download")
def download_cleaned(dataset_id: str):
    dataset = repo.get(dataset_id)

    if dataset.status != DatasetStatus.done:
        raise HTTPException(
            status_code=400, 
            detail="Dataset is not ready for download"
        )
    
    if not dataset.cleaned_path:
        raise HTTPException(
            status_code=404, 
            detail="Cleaned file not available"
        )

    return FileResponse(
        path=str(dataset.cleaned_path),
        filename="cleaned.csv",
        media_type="text/csv"
    )


@router.get("/datasets/{dataset_id}/report")
def get_report(dataset_id: str):
    dataset = repo.get(dataset_id)

    if dataset.status != DatasetStatus.done:
        raise HTTPException(
            status_code=400, 
            detail="Report is not ready for download"
        )
    
    if not dataset.report_path:
        raise HTTPException(
            status_code=404, 
            detail="Report not available"
        )

    with open(dataset.report_path) as f:
        return json.load(f)