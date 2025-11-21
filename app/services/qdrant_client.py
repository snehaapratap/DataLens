from app.config import settings
import logging
logger = logging.getLogger("datalens")

try:
    from qdrant_client import QdrantClient
    _HAS_QDRANT = True
except Exception:
    _HAS_QDRANT = False

class QdrantWrapper:
    def __init__(self):
        if _HAS_QDRANT:
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        else:
            self.client = None
            self._store = {}  

    def upsert(self, collection_name: str, ids, vectors, payloads):
        if self.client:
            self.client.upsert(collection_name=collection_name, points=[{"id": i, "vector": v, "payload": p} for i,v,p in zip(ids,vectors,payloads)])
            logger.info("Upserted to Qdrant collection %s (real)", collection_name)
        else:
            self._store.setdefault(collection_name, []).extend(list(zip(ids,vectors,payloads)))
            logger.info("Upserted to Qdrant collection %s (mock)", collection_name)

    def search(self, collection_name: str, vector, top=5):
        if self.client:
            res = self.client.search(collection_name=collection_name, query_vector=vector, limit=top)
            return res
        else:
            from numpy import dot
            from numpy.linalg import norm
            items = self._store.get(collection_name, [])
            sims = []
            for id_, vec, payload in items:
                import numpy as np
                sim = float(dot(np.array(vec), np.array(vector)) / (norm(vec) * norm(vector) + 1e-9))
                sims.append((id_, sim, payload))
            sims.sort(key=lambda x: x[1], reverse=True)
            return sims[:top]
