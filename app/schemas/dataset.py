from pydantic import BaseModel
from enum import Enum
from datetime import datetime

from uuid import UUID

class DatasetStatus(str, Enum):
    """Representa el estado de un dataset en el sistema."""
    
    uploaded = "uploaded"
    processing = "processing"
    done = "done"
    failed = "failed"


class DatasetCreateResponse(BaseModel):
    """Modelo de respuesta para la creación de un dataset en el sistema."""

    id: UUID
    status: DatasetStatus
    created_at: datetime = datetime.now()  # Se establece el timestamp en el momento de la creación del dataset.


class DatasetResponse(BaseModel):
    """Modelo de respuesta para la obtención de un dataset en el sistema."""

    id: UUID
    status: DatasetStatus
    created_at: datetime


class SummaryStats(BaseModel):
    row_count: int
    column_count: int

class DatasetResultsResponse(BaseModel):
    summary: SummaryStats