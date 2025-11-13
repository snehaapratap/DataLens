from fastapi import APIRouter, UploadFile, File, Depends
import os
from datetime import datetime
from app.utils.qdrant_utils import store_embedding, search_similar_embeddings
from app.utils.auth import authenticate
from app.utils.s3_utils import upload_to_s3

router = APIRouter()

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_files(csv: UploadFile = File(...), image: UploadFile = File(...)):
    csv_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{csv.filename}")
    image_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{image.filename}")

    with open(csv_path, "wb") as f:
        f.write(await csv.read())
    with open(image_path, "wb") as f:
        f.write(await image.read())

    # Upload to S3
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    csv_s3_url = upload_to_s3(csv_path, bucket_name)
    image_s3_url = upload_to_s3(image_path, bucket_name)

    return {
        "csv_path": csv_path,
        "image_path": image_path,
        "csv_s3_url": csv_s3_url,
        "image_s3_url": image_s3_url,
        "message": "Files uploaded successfully"
    }

@router.post("/store-embedding", dependencies=[Depends(authenticate)])
def store_embedding_api(text: str, metadata: dict):
    """Stores embeddings for the given text in Qdrant."""
    store_embedding(text, metadata)
    return {"message": "Embedding stored successfully."}

@router.post("/search-embedding", dependencies=[Depends(authenticate)])
def search_embedding_api(query: str):
    """Searches for similar embeddings in Qdrant."""
    results = search_similar_embeddings(query)
    return {"results": results}
