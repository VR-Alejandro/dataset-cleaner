from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# --- Configuramos la app para desactivar el almacenamiento en caché ---
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# --- Configuramos la ruta principal para que muestre el frontend --- 
FRONTEND_DIR = BASE_DIR / "frontend"

@app.get("/")
async def serve_home():
    return FileResponse(FRONTEND_DIR / "index.html")


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

# Montamos el directorio del frontend
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")