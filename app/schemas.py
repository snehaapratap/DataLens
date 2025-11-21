from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FileInfo(BaseModel):
    filename: str
    content_type: str
    size: int
    s3_path: Optional[str] = None
    checksum: Optional[str] = None

class UploadResponse(BaseModel):
    upload_id: str
    files: List[FileInfo]

class ReportRequest(BaseModel):
    upload_id: str
    include_pdf: bool = False

class KeyMetric(BaseModel):
    name: str
    value: Any
    note: Optional[str] = None

class TrendItem(BaseModel):
    metric: str
    direction: str
    description: Optional[str] = None

class CorrelationItem(BaseModel):
    a: str
    b: str
    coefficient: float

class ReportResponse(BaseModel):
    report_id: str
    summary: str
    key_metrics: Dict[str, Any]
    trends: List[str]
    correlations: List[str]
    recommendations: List[str]
    pdf_path: Optional[str] = None
