import os
from app.config import settings
import logging
logger = logging.getLogger("datalens")

def upload_to_s3(local_path: str, key: str | None = None) -> str:
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET:
        import boto3
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        key = key or os.path.basename(local_path)
        s3.upload_file(local_path, settings.AWS_S3_BUCKET, key)
        url = f"s3://{settings.AWS_S3_BUCKET}/{key}"
        logger.info("Uploaded to S3 %s", url)
        return url
    else:
        logger.info("S3 credentials not present, returning local path")
        return os.path.abspath(local_path)
