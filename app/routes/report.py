from __future__ import annotations

import os
import json
from uuid import uuid4
from typing import List
from urllib.parse import urlparse

import boto3
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import ReportRequest, ReportResponse
from app.db.database import get_db
from app.db.models import Upload, FileMeta, Report
from app.utils.metrics import compute_key_metrics, detect_trends, compute_correlations
from app.ai.vision import extract_image_text
from app.ai.langchain_agent import run_langchain_agent
from app.utils.pdf_generator import generate_pdf
from app.services.s3_client import upload_to_s3
from app.services.qdrant_client import QdrantWrapper
from app.services.embeddings import generate_embeddings
from app.logger import logger
from app.config import settings

router = APIRouter()
qdrant = QdrantWrapper()

LOCAL_UPLOAD_DIR = os.path.join("app", "uploads")


# ------------------------
# Helpers for file access
# ------------------------

def download_s3_to_local(s3_uri: str, subdir: str) -> str:
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    local_dir = os.path.join("tmp", subdir)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, os.path.basename(key))

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3.download_file(bucket, key, local_path)
    return local_path


def ensure_local_csv_path(f: FileMeta) -> str | None:
    if f.s3_path and f.s3_path.startswith("s3://"):
        try:
            return download_s3_to_local(f.s3_path, "csv")
        except Exception as e:
            logger.error("CSV S3 download failed: %s", e)

    local_path = os.path.join(LOCAL_UPLOAD_DIR, f.filename)
    return local_path if os.path.exists(local_path) else None


def ensure_local_image_paths(f: FileMeta) -> List[str]:
    paths = []
    if f.s3_path:
        paths.append(f.s3_path)
    paths.append(os.path.join(LOCAL_UPLOAD_DIR, f.filename))
    return list(dict.fromkeys(paths))


def is_csv(f: FileMeta) -> bool:
    return f.filename.lower().endswith(".csv")


def is_image(f: FileMeta) -> bool:
    return f.filename.lower().endswith((".png", ".jpg", ".jpeg"))


# ------------------------
# Generate Report Endpoint
# ------------------------

@router.post("/generate-report", response_model=ReportResponse, tags=["report"])
def generate_report(req: ReportRequest, db: Session = Depends(get_db)):

    upload = db.query(Upload).filter(Upload.id == req.upload_id).first()
    if not upload:
        raise HTTPException(404, "upload_id not found")

    files = db.query(FileMeta).filter(FileMeta.upload_id == req.upload_id).all()
    if not files:
        raise HTTPException(400, "No files found")

    csv_files = [f for f in files if is_csv(f)]
    image_files = [f for f in files if is_image(f)]

    csv_summaries = []
    for f in csv_files:
        path = ensure_local_csv_path(f)
        if not path:
            continue

        try:
            df = pd.read_csv(path)
            km = compute_key_metrics(df)
            tr = detect_trends(df)
            corr = compute_correlations(df)
            summary = f"File: {f.filename}\nKey Metrics: {km}\nTrends: {tr}\nCorrelations: {corr}\n"
            csv_summaries.append(summary)
        except Exception as e:
            logger.error("CSV error: %s", e)

    image_captions = []
    for f in image_files:
        for p in ensure_local_image_paths(f):
            cap = extract_image_text(p).get("caption", "")
            if cap:
                image_captions.append(f"{f.filename}: {cap}")
                break

    logger.info("Groq Agent inputs: %d CSV + %d images", len(csv_summaries), len(image_captions))

    # Generate insights via Groq + LangChain
    agent_out = run_langchain_agent(csv_summaries, image_captions)
    report_id = str(uuid4())
    pdf_path = None

    # Generate PDF if requested
    if req.include_pdf:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "outputs"))
        os.makedirs(pdf_dir, exist_ok=True)
        local_pdf = os.path.join(pdf_dir, f"{report_id}.pdf")

        try:
            generate_pdf(agent_out, local_pdf)
            pdf_path = f"/outputs/{report_id}.pdf"
            logger.info("PDF generated: %s", pdf_path)
        except Exception as e:
            logger.error("PDF generation failed: %s", e)

    # Save report in DB
    rep = Report(id=report_id, upload_id=req.upload_id, report_json=agent_out, pdf_path=pdf_path)
    db.add(rep)
    db.commit()

    # Store vectors in Qdrant
    try:
        texts = [agent_out.get("summary", ""), json.dumps(agent_out.get("key_metrics", {}))]
        vecs = generate_embeddings(texts)
        ids = [f"{report_id}_0", f"{report_id}_1"]
        payloads = [{"report_id": report_id}, {"report_id": report_id}]
        qdrant.upsert("reports", ids, vecs, payloads)
    except Exception as e:
        logger.warning("Qdrant upsert failed: %s", e)

    return {
        "report_id": report_id,
        "summary": agent_out.get("summary", ""),
        "key_metrics": agent_out.get("key_metrics", {}),
        "trends": agent_out.get("trends", []),
        "correlations": agent_out.get("correlations", []),
        "recommendations": agent_out.get("recommendations", []),
        "pdf_path": pdf_path,
    }

