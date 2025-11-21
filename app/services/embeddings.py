import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    model = get_model()
    emb = model.encode(texts, convert_to_numpy=True)

    return emb.tolist()
