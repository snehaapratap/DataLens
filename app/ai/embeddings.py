from app.config import settings
import logging
logger = logging.getLogger("datalens")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    _HAS_ST = True
except Exception as e:
    _HAS_ST = False
    logger.info("sentence-transformers not available: %s", e)

def generate_embeddings(texts):
    if _HAS_ST:
        vecs = model.encode(texts, show_progress_bar=False).tolist()
        return vecs
    else:
        import hashlib
        import numpy as np
        vecs = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            arr = np.frombuffer(h, dtype="uint8").astype(float)
            v = np.tile(arr, int(384/len(arr))+1)[:384]
            v = v / (np.linalg.norm(v) + 1e-9)
            vecs.append(v.tolist())
        return vecs
