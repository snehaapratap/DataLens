from fastapi import APIRouter, Depends
from app.services.agent import generate_report_with_agent
from app.services.pdf_generator import generate_pdf
from app.utils.auth import authenticate
import os

router = APIRouter()

@router.post("/generate-report", dependencies=[Depends(authenticate)])
def generate_report_api(csv_path: str, image_path: str):
    report = generate_report_with_agent(csv_path, image_path)
    return {"report": report}

@router.post("/download-pdf", dependencies=[Depends(authenticate)])
def download_pdf(report_json: str):
    output_path = "outputs/report.pdf"
    os.makedirs("outputs", exist_ok=True)
    pdf_path = generate_pdf(report_json, output_path)
    return {"pdf_path": pdf_path, "message": "PDF generated successfully"}
