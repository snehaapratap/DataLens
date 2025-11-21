#  **DataLens – Automated Business Insights Platform**

*AI-powered report generation from business datasets*

---

###  Overview

**DataLens** is an AI-driven analytics system that allows users to upload business data (CSV files + charts/images) and automatically generates:


✔ Executive summary
✔ Key Business Metrics
✔ Trend Analysis
✔ Correlation Insights
✔ Actionable Recommendations (LLM)
✔ Optional PDF Report Output

This solution is ideal for marketing, sales, and web analytics teams that need fast insights — without manual analysis.

---

###  Key Features

| Feature                                | Description                                                      |
| -------------------------------------- | ---------------------------------------------------------------- |
| **Multi-File Upload**                  | Upload CSV and PNG/JPG images in a single request                |
| **AI Trend Detection**                 | Numeric column trend extraction (growth %, decline, stability)   |
| **Correlation Insights**               | Auto-detected KPI relationships with significance levels         |
| **Image Captioning**                   | Vision model extracts insights from uploaded charts              |
| **Language Model Insights**            | Groq LLaMA-3.1-8b-Instant agent-written business recommendations |
| **PDF Export**                         | Professional formatted report saved locally or to S3             |
| **Vector Search Support** *(optional)* | Semantic embedding storage using Qdrant                          |

---

### API Usage

####  Upload Files

`POST /upload`

Response includes:

```json
{
  "upload_id": "6686c1c2-5788-4d46-a8e7-bac6e5c2f383",
  "files": [
    {
      "filename": "1763727674511_marketing.csv",
      "content_type": "text/csv",
      "size": 389,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727674511_marketing.csv",
      "checksum": "37ec41fa885236f2ebdebf94135ee954a54044588ddeedbbb6aa2cbd07bd587c"
    },
    {
      "filename": "1763727675800_website_traffic.csv",
      "content_type": "text/csv",
      "size": 168,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727675800_website_traffic.csv",
      "checksum": "1fd805b3e342c2b8bd1b4bd0e31502c03bfae11498fa0f031d72497fef3b8d97"
    },
    {
      "filename": "1763727676922_sales.csv",
      "content_type": "text/csv",
      "size": 305,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727676922_sales.csv",
      "checksum": "4a2522296958ab0c3cabef5c66bd32c34774ccce290a6eef904f9d98c8641e0f"
    },
    {
      "filename": "1763727678049_marketing_chart.png",
      "content_type": "image/png",
      "size": 33021,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727678049_marketing_chart.png",
      "checksum": "f869dd44c1a6719eac91cd1c8996ea9bc7cb8a72ee035ac4ad7535d1fdb50d24"
    },
    {
      "filename": "1763727679489_traffic_chart.png",
      "content_type": "image/png",
      "size": 14557,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727679489_traffic_chart.png",
      "checksum": "979359bb0a9f413f614a627ab6b5601519489fead5607b7cb5241b9642c749e2"
    },
    {
      "filename": "1763727680820_sales_chart.png",
      "content_type": "image/png",
      "size": 28177,
      "s3_path": "s3://datalens11/6686c1c2-5788-4d46-a8e7-bac6e5c2f383/1763727680820_sales_chart.png",
      "checksum": "89d65878b3a4406973913f19399270c8ad77777c76c8fd55f25062279f6a16b0"
    }
  ]
}
```

####  Generate AI Report

`POST /generate-report`

Example request:

```json
{
  "upload_id": "6686c1c2-5788-4d46-a8e7-bac6e5c2f383",
  "include_pdf": false
}
```

Example response:

```json
{
  "report_id": "b29341fa-2c3c-43e8-bc76-4525b6966532",
  "summary": "Business overview and insights",
  "key_metrics": {
    "Revenue Growth %": "8.3%",
    "Marketing ROI %": "44.0%",
    "Conversion Rate %": "6.5%"
  },
  "trends": [
    "Impressions have increased by 8.3% from first to last row.",
    "Visitors have increased by 30.0% from first to last row.",
    "Units_Sold have increased by 8.3% from first to last row.",
    "Bounce_Rate has decreased by 9.6% from first to last row.",
    "Marketing_Spend has decreased by 20.0% from first to last row."
  ],
  "correlations": [
    "Impressions and Clicks are highly correlated (coefficient: 0.9932917659827766)",
    "Visitors and Page_Views are highly correlated (coefficient: 0.9743571218180728)",
    "Units_Sold and Revenue are highly correlated (coefficient: 1.0)",
    "Marketing_Spend and Units_Sold are moderately correlated (coefficient: 0.9321946329251546)",
    "Marketing_Spend and Revenue are moderately correlated (coefficient: 0.9321946329251546)"
  ],
  "recommendations": [
    "Increase marketing spend to capitalize on the positive correlation between marketing spend and units sold.",
    "Optimize website traffic by improving page views and reducing bounce rate, as these metrics are highly correlated.",
    "Analyze the regression of the regression graph to identify areas for improvement in marketing efforts."
  ],
  "pdf_path": null
}
```

---

###  Project Structure

```
app/
├── ai/
│   ├── langchain_agent.py
│   ├── vision.py
├── routes/
│   ├── upload.py
│   ├── report.py
├── utils/
│   ├── metrics.py
│   ├── pdf_generator.py
├── services/
│   ├── s3_client.py
│   ├── qdrant_client.py
├── db/
│   ├── models.py
│   ├── database.py
├── outputs/            → Generated PDFs stored here
└── uploads/            → Local file storage
```

---

### 🧪 Local Development Setup

```bash
git clone https://github.com/snehaapratap/DataLens
cd DataLens
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API Docs:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

### Required Environment Variables

Create `.env`:

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket_name   # leave blank to disable S3
GROQ_API_KEY=your_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```


---

###  PDF Output

| Output Type                                 | When it happens                |
| ------------------------------------------- | ------------------------------ |
| Saved locally `app/outputs/<report_id>.pdf` | Always when `include_pdf=true` |
| Also uploaded to S3                         | Only when bucket name is set   |

PDF includes:

* Title & Summary
* KPI Table
* Trends section
* Correlations section
* Recommendations

###  Video Demo

[link](https://www.loom.com/share/8636b252b40749da884fd12d0ae29967)



