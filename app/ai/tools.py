from langchain.tools import Tool
import pandas as pd
import os
import numpy as np
import json
from app.ai.vision import extract_image_text
from typing import Dict, Any, List
import logging
from app.utils.metrics import compute_key_metrics, detect_trends, compute_correlations

logger = logging.getLogger("datalens")

def csv_metrics_tool(path_or_text: str) -> str:
    try:
        if os.path.exists(path_or_text):
            df = pd.read_csv(path_or_text)
        else:
            # treat as raw CSV content
            from io import StringIO
            df = pd.read_csv(StringIO(path_or_text))
        km = compute_key_metrics(df)
        return json.dumps({"key_metrics": km})
    except Exception as e:
        logger.exception("csv_metrics_tool failed: %s", e)
        return json.dumps({"error": str(e)})

def csv_trends_tool(path_or_text: str) -> str:
    try:
        if os.path.exists(path_or_text):
            df = pd.read_csv(path_or_text)
        else:
            from io import StringIO
            df = pd.read_csv(StringIO(path_or_text))
        trends = detect_trends(df)
        return json.dumps({"trends": trends})
    except Exception as e:
        logger.exception("csv_trends_tool failed: %s", e)
        return json.dumps({"error": str(e)})

def csv_correlations_tool(path_or_text: str) -> str:
    try:
        if os.path.exists(path_or_text):
            df = pd.read_csv(path_or_text)
        else:
            from io import StringIO
            df = pd.read_csv(StringIO(path_or_text))
        corr = compute_correlations(df)
        return json.dumps({"correlations": corr})
    except Exception as e:
        logger.exception("csv_correlations_tool failed: %s", e)
        return json.dumps({"error": str(e)})

def image_caption_tool(path_or_url: str) -> str:
    try:
        cap = extract_image_text(path_or_url)
        return json.dumps({"caption": cap.get("caption","")})
    except Exception as e:
        logger.exception("image_caption_tool failed: %s", e)
        return json.dumps({"error": str(e)})

def format_json_tool(raw_text: str) -> str:
    try:
        parsed = json.loads(raw_text)
        return json.dumps(parsed)
    except Exception:
        return json.dumps({
            "summary":"",
            "key_metrics": {},
            "trends": [],
            "correlations": [],
            "recommendations": []
        })

TOOLS = [
    Tool(
        name="csv_metrics",
        func=csv_metrics_tool,
        description="Given a CSV path or CSV text return key metrics as JSON."
    ),
    Tool(
        name="csv_trends",
        func=csv_trends_tool,
        description="Given a CSV path or CSV text return detected trends as JSON."
    ),
    Tool(
        name="csv_correlations",
        func=csv_correlations_tool,
        description="Given a CSV path or CSV text return correlations as JSON."
    ),
    Tool(
        name="image_caption",
        func=image_caption_tool,
        description="Given a local image path or URL return a caption/ocr as JSON."
    ),
    Tool(
        name="format_json",
        func=format_json_tool,
        description="Validate or return strict JSON in the assignment schema."
    ),
]
