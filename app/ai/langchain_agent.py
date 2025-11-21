import json
from langchain_groq import ChatGroq
from app.config import settings
from app.logger import logger


def run_langchain_agent(csv_summaries, image_captions):
    """
    Use Groq LLM to create a structured AI business analytics report.
    """

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL or "llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=2048,
    )

    prompt = f"""
You are a senior business data analyst.
Analyze the dataset insights & image captions provided below and generate a detailed business intelligence report.

STRICT OUTPUT FORMAT → return ONLY valid JSON:
{{
  "summary": "Business overview and insights",
  "key_metrics": {{
    "Revenue Growth %": "x",
    "Marketing ROI %": "x",
    "Conversion Rate %": "x"
  }},
  "trends": [
    "Important patterns discovered"
  ],
  "correlations": [
    "Meaningful relationships found in data"
  ],
  "recommendations": [
    "Clear, actionable business improvement ideas"
  ]
}}

Guidelines:
- Metrics must be realistic based on insights — DO NOT invent random numbers
- Provide at least 3 **SMART** recommendations (specific & actionable)
- Do not return markdown, additional comments, or code fences

CSV Insights:
{csv_summaries}

Visual Insights:
{image_captions}
"""

    try:
        logger.info("📡 Sending request to Groq")
        response = llm.invoke(prompt)
        text = response.content.strip()

        # Remove code fencing if present
        if text.startswith("```"):
            text = text.strip("```").strip()

        result = json.loads(text)
        logger.info("✅ Groq report parsed successfully")
        return result

    except Exception as e:
        logger.error("❌ Groq parsing failed: %s", e)

        return {
            "summary": "Partial insights extracted. AI failed to fully structure advanced details.",
            "key_metrics": {},
            "trends": [],
            "correlations": [],
            "recommendations": [
                "Use more structured data for stronger insight extraction.",
                "Ensure charts contain readable labels and trends.",
                "Validate column naming consistency across CSV uploads."
            ]
        }

