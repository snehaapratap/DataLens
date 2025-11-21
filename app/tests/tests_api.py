from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_upload_minimal():
    files = [
        ("csv_files", ("test.csv", io.BytesIO(b"a,b\n1,2\n3,4"), "text/csv")),
    ]
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "upload_id" in data
