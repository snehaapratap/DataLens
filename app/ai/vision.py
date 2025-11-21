import os
from urllib.parse import urlparse

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

import boto3

from app.config import settings
from app.logger import logger

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def _download_s3_to_local(s3_uri: str) -> str:
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    local_dir = os.path.join("tmp", "images")
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, os.path.basename(key))

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3.download_file(bucket, key, local_path)
    return local_path


def _resolve_image_path(path: str) -> str:
    if path.startswith("s3://"):
        return _download_s3_to_local(path)
    return path


def extract_image_text(path: str) -> dict:
    try:
        local_path = _resolve_image_path(path)
        img = Image.open(local_path).convert("RGB")

        inputs = processor(images=img, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return {"caption": caption}

    except Exception as e:
        logger.exception("BLIP failed: %s", e)
        return {"caption": ""}
