"""
Wraps Qdrant so the rest of the app never touches the Qdrant client directly.

Uses Qdrant's EMBEDDED mode (path=... instead of url=...) — this runs
Qdrant directly inside our Python process and saves vectors to a local
folder, with no separate server or Docker container needed. Perfect for
low-resource machines.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from fastembed import TextEmbedding
import uuid
from app.core.config import settings

# fastembed's default model: small, fast, CPU-only, ~80MB download on first use.
_embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
EMBEDDING_DIM = 384  # bge-small-en-v1.5 produces 384-dimensional vectors

_client = QdrantClient(path=settings.qdrant_local_path)


def _ensure_collection():
    collections = [c.name for c in _client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        _client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turns a list of text chunks into a list of embedding vectors."""
    return [vec.tolist() for vec in _embedding_model.embed(texts)]


def upsert_chunks(document_id: str, workspace_id: str, chunks: list[str]):
    """Embeds and stores a document's chunks in Qdrant, tagged with workspace_id
    (so retrieval can be scoped to just one workspace's documents)."""
    _ensure_collection()
    vectors = embed_texts(chunks)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "workspace_id": workspace_id,
                "text": chunk,
            },
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    _client.upsert(collection_name=settings.qdrant_collection, points=points)


def search(workspace_id: str, query: str, top_k: int = 4) -> list[dict]:
    """Finds the most relevant chunks for a query, scoped to one workspace."""
    _ensure_collection()
    query_vector = embed_texts([query])[0]

    results = _client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="workspace_id", match=MatchValue(value=workspace_id))]
        ),
        limit=top_k,
    )
    return [
        {"text": point.payload["text"], "document_id": point.payload["document_id"], "score": point.score}
        for point in results.points
    ]
