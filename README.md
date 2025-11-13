# DataLens

## Overview
DataLens is an AI-powered backend system that generates structured business reports from mixed data sources, including tabular data (CSV) and visual data (images such as charts or infographics). The system leverages vision-language models to interpret visuals, LLMs to analyze tabular data, and LangChain agents to synthesize insights.

## Features
- **Data Ingestion**: Accepts multiple CSV and image files via API endpoints.
- **AI Processing Pipeline**: Combines insights from Vision models (e.g., BLIP) and LLMs (e.g., LangChain + Groq).
- **Report Generation**: Outputs structured JSON reports and optionally generates downloadable PDF reports with charts and tables.
- **Embeddings and Similarity Search**: Generates embeddings for documents and performs similarity searches using Qdrant.
- **Authentication**: Secures API access with token-based authentication.
- **Logging and Error Handling**: Includes a logging system and error-handling middleware.

## Tech Stack
- **Backend Framework**: FastAPI
- **AI & Orchestration**: LangChain, LLMs (OpenAI/Gemini/Local), CLIP/BLIP
- **Database**: PostgreSQL
- **Vector Store**: Qdrant
- **Storage**: AWS S3
- **Deployment**: Render/Railway/AWS/Hugging Face Spaces

## Setup Instructions
### Prerequisites
- Python 3.10 or higher
- PostgreSQL database
- Qdrant server
- AWS S3 bucket (or mock equivalent)

### Installation
1. Clone the repository:
   ```bash
   git clone <https://github.com/snehaapratap/DataLens>
   cd DataLens
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory with the following content:
     ```env
     GROQ_API_KEY=<your_groq_api_key>
     API_TOKEN=<your_api_token>
     DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
     AWS_ACCESS_KEY_ID=<your_aws_access_key>
     AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
     AWS_BUCKET_NAME=<your_bucket_name>
     ```

5. Initialize the database:
   ```bash
   python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. Start the Qdrant server (if not hosted):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Example Usage
### Upload Files
Endpoint: `POST /upload`
- Request:
  ```bash
  curl -X POST "http://127.0.0.1:8000/upload" \
       -F "csv=@path/to/file.csv" \
       -F "image=@path/to/image.png"
  ```
- Response:
  ```json
  {
  "csv_path": "uploads/1763065295.998647_sales.csv",
  "image_path": "uploads/1763065295.998662_sales_chart.png",
  "message": "Files uploaded successfully"
    }
  ```

### Generate Report
Endpoint: `POST /generate-report`
- Request:
  ```bash
  curl -X POST "http://127.0.0.1:8000/generate-report" \
       -H "Authorization: Bearer <your_api_token>" \
       -H "Content-Type: application/json" \
       -d '{"csv_path": "uploads/1234567890_file.csv", "image_path": "uploads/1234567890_image.png"}'
  ```
- Response:
  ```json
  {
    "report": {
      "summary": "...",
      "key_metrics": {"metric1": 100},
      "trends": "...",
      "recommendations": "..."
    }
  }
  ```

### Download PDF
Endpoint: `POST /download-pdf`
- Request:
  ```bash
  curl -X POST "http://127.0.0.1:8000/download-pdf" \
       -H "Authorization: Bearer <your_api_token>" \
       -H "Content-Type: application/json" \
       -d '{"report_json": {"summary": "...", "key_metrics": {"metric1": 100}}}'
  ```
- Response:
  ```json
  {
    "pdf_path": "outputs/report.pdf",
    "message": "PDF generated successfully"
  }
  ```

## Deployment
To deploy the application, use any cloud hosting platform (e.g., Render, Railway, AWS). Ensure the `.env` file is configured with production credentials.

## License
This project is licensed under the MIT License.

