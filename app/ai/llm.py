from typing import Optional, List, Mapping, Any
from langchain.llms.base import LLM
from pydantic import BaseModel
import json
import logging
from app.config import settings

logger = logging.getLogger("datalens")

try:
    import groq
except Exception:
    groq = None

class GroqLLM(LLM, BaseModel):
    """Minimal LangChain-compatible LLM wrapper using Groq chat completions."""
    model: str = "llama3-8b-8192"
    temperature: float = 0.0
    api_key: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        if groq is None:
            raise RuntimeError("groq python package not available")
        try:
            client = groq.Groq(api_key=self.api_key or settings.GROQ_API_KEY)
            # Use chat completion API by wrapping prompt as a single user message
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=1500,
            )
            # Robustly extract text
            text = None
            if isinstance(resp, dict):
                choices = resp.get("choices", [])
                if choices:
                    msg = choices[0].get("message") or {}
                    text = msg.get("content") or choices[0].get("text")
            else:
                try:
                    text = resp.choices[0].message.content
                except Exception:
                    try:
                        text = resp.choices[0].text
                    except Exception:
                        text = str(resp)
            return text or ""
        except Exception as e:
            logger.exception("Groq LLM call failed: %s", e)
            raise

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}

    @property
    def _llm_type(self) -> str:
        return "groq"
