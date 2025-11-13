from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import os

client = QdrantClient(url="http://localhost:6333")  
model = SentenceTransformer("all-MiniLM-L6-v2")

def store_embedding(text, metadata):
    vector = model.encode(text).tolist()
    client.upsert(
        collection_name="insightweaver",
        points=[PointStruct(id=None, vector=vector, payload=metadata)]
    )

def search_similar_embeddings(query: str):
    """Searches for similar embeddings in Qdrant based on the query text."""
    vector = model.encode(query).tolist()
    search_result = client.search(
        collection_name="insightweaver",
        query_vector=vector,
        limit=5  
    )
    return [
        {
            "id": result.id,
            "score": result.score,
            "payload": result.payload
        }
        for result in search_result
    ]
