from app.vectorstore import qdrant_store
from app.llm.factory import get_llm_provider

RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the provided context.
If the answer isn't in the context, say "I don't have that information in the uploaded documents" — do not make anything up.
Always be concise. When possible, mention which part of the context supports your answer."""


async def answer_question(workspace_id: str, question: str, top_k: int = 4) -> dict:
    chunks = qdrant_store.search(workspace_id, question, top_k=top_k)

    if not chunks:
        return {
            "answer": "I don't have any indexed documents to answer from yet in this workspace. Upload a document first.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(f"[Source {i+1}]: {c['text']}" for i, c in enumerate(chunks))
    prompt = f"Context:\n{context}\n\nQuestion: {question}"

    llm = get_llm_provider()
    answer = await llm.generate(prompt=prompt, system=RAG_SYSTEM_PROMPT)

    return {
        "answer": answer,
        "sources": [
            {"document_id": c["document_id"], "excerpt": c["text"][:200], "relevance_score": round(c["score"], 3)}
            for c in chunks
        ],
    }
