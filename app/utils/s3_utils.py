import boto3, os

def upload_to_s3(file_path, bucket_name):
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key or not aws_secret_key or not bucket_name:
        print(f"[Mock S3] File '{file_path}' would be uploaded to bucket '{bucket_name}'.")
        return f"mock-s3://{bucket_name}/{os.path.basename(file_path)}"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )
    file_name = os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name, file_name)
    return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
