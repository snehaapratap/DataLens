import json
import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger("datalens")

SYSTEM_PROMPT = """
You are a business data analyst. You are given:
1. CSV summaries (numeric metrics, correlations, trends)
2. Image captions extracted using a vision model

Your output MUST follow this STRICT JSON SCHEMA:

{
  "summary": "1–3 sentence overview",
  "key_metrics": { "metric_name": value },
  "trends": [
    {"metric": "", "direction": "up|down|stable", "description": ""}
  ],
  "correlations": [
    {"a": "", "b": "", "coefficient": 0.00}
  ],
  "recommendations": [
    "Provide a clear, data-driven business recommendation."
  ]
}

Rules:
- Return ONLY valid JSON.
- No markdown.
- No commentary.
- No text outside the JSON.
"""


def run_langchain_agent(csv_analysis: list[str], image_analysis: list[str]) -> dict:

    combined = "\n\n".join(
        [f"CSV SUMMARY:\n{c}" for c in csv_analysis] +
        [f"IMAGE CAPTION:\n{i}" for i in image_analysis]
    )
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        resp = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": combined}
            ],
            temperature=0
        )

        text = resp.choices[0].message.content.strip()

        # Parse JSON safely
        return json.loads(text)

    except Exception as e:
        logger.exception("Groq agent failed. Falling back. Error: %s", e)

        # ----------------------------
        # FALLBACK (no Groq)
        # ----------------------------
        return {
            "summary": "Fallback summary. GROQ_API_KEY missing or model failed.",
            "key_metrics": {f"csv_{i}_len": len(x) for i, x in enumerate(csv_analysis)},
            "trends": [
                {"metric": "csv_0_len", "direction": "stable", "description": "Fallback trend."}
            ],
            "correlations": [],
            "recommendations": ["Enable GROQ_API_KEY to activate real LLM reasoning."]
        }
