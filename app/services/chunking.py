"""
Splits long text into overlapping chunks small enough to embed and retrieve
individually. Overlap (default 50 chars) prevents cutting a sentence in half
right at a chunk boundary and losing its meaning.
"""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return [c.strip() for c in chunks if c.strip()]
