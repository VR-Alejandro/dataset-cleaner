from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Dataset:
    id: str
    filename: str
    status: str
    input_path: str
    cleaned_path: Optional[str]
    report_path: Optional[str]
    created_at: datetime
    error_type: Optional[str]
    error_message: Optional[str]