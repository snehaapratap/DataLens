import os
os.makedirs("uploads", exist_ok=True)
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import os, time, hashlib
from uuid import uuid4
from app.schemas import UploadResponse, FileInfo
from app.db.database import get_db
from app.db.models import Upload, FileMeta
from app.services.s3_client import upload_to_s3
from sqlalchemy.orm import Session
from app.logger import logger

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=UploadResponse, tags=["upload"])
async def upload_files(csv_files: List[UploadFile] = File(None), image_files: List[UploadFile] = File(None), db: Session = Depends(get_db)):
    files = []
    upload_id = str(uuid4())
    db.add(Upload(id=upload_id, metadata={}))
    db.commit()
    for f in (csv_files or []) + (image_files or []):
        ts = str(int(time.time()*1000))
        fname = f"{ts}_{f.filename}"
        out = os.path.join(UPLOAD_DIR, fname)
        contents = await f.read()
        with open(out, "wb") as fh:
            fh.write(contents)
        checksum = hashlib.sha256(contents).hexdigest()
        s3_path = upload_to_s3(out, key=f"{upload_id}/{fname}")
        size = len(contents)
        fm = FileMeta(id=str(uuid4()), upload_id=upload_id, filename=fname, s3_path=s3_path, file_type=f.content_type, checksum=checksum, size=size)
        db.add(fm)
        db.commit()
        files.append(FileInfo(filename=fname, content_type=f.content_type, size=size, s3_path=s3_path, checksum=checksum))
        logger.info("Saved file %s (size=%d)", out, size)
    return {"upload_id": upload_id, "files": files}
