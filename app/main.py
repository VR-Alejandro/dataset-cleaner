from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.db import init_db


from processing.exceptions import (
    ValidationError,
    DatasetLoadError,
    ProcessingError,
    CleaningError,
    StatisticsError,
    CleanedDatasetGenerationError,
    ReportGenerationError
)

import logging
from pathlib import Path


# Configuración del logging
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "dataset-cleaner.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)


# Inicialización de la BBDD
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


# Mapeo de excepciones a códigos HTTP
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(exc)},
    )

@app.exception_handler(DatasetLoadError)
async def load_exception_handler(request: Request, exc: DatasetLoadError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )

@app.exception_handler(ProcessingError)
async def processing_exception_handler(request: Request, exc: ProcessingError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.exception_handler(CleaningError)
async def cleaning_exception_handler(request: Request, exc: CleaningError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.exception_handler(StatisticsError)
async def statistics_exception_handler(request: Request, exc: StatisticsError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.exception_handler(CleanedDatasetGenerationError)
async def cleaned_dataset_generation_exception_handler(request: Request, exc: CleanedDatasetGenerationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

@app.exception_handler(ReportGenerationError)
async def report_generation_exception_handler(request: Request, exc: ReportGenerationError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )
