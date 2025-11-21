from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Boolean
)
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
from sqlalchemy.types import JSON as SQLJSON


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)

class FileMeta(Base):
    __tablename__ = "filemeta"

    id = Column(String, primary_key=True, index=True)
    upload_id = Column(String, ForeignKey("uploads.id"))
    filename = Column(String)
    s3_path = Column(String) 
    file_type = Column(String)
    checksum = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)



class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, index=True)
    upload_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    report_json = Column(SQLJSON, default={})
    pdf_path = Column(String, nullable=True)
    embeddings_indexed = Column(Boolean, default=False)
