from app.vectorstore import qdrant_store
from app.llm.factory import get_llm_provider
from app.services.web_search import web_search

RAG_SYSTEM_PROMPT = """You are a helpful assistant. You are given two kinds of context:
1. "Document sources" — content from the user's own uploaded documents.
2. "Web sources" — live, current information from the internet.

Answer using whichever is relevant. If document sources answer the question, prefer them and say so.
If the question needs current/real-time information (news, prices, dates, "latest", "current", etc.),
rely on the web sources instead. If neither has the answer, say you don't know — never make things up.
Be concise, and mention which kind of source (document or web) your answer came from."""


async def answer_question(workspace_id: str, question: str, top_k: int = 4) -> dict:
    doc_chunks = qdrant_store.search(workspace_id, question, top_k=top_k)
    web_results = await web_search(question, max_results=3)

    if not doc_chunks and not web_results:
        return {
            "answer": "I couldn't find anything relevant in your documents or the web for that question.",
            "sources": [],
            "web_sources": [],
        }

    context_parts = []
    if doc_chunks:
        doc_context = "\n\n---\n\n".join(f"[Document Source {i+1}]: {c['text']}" for i, c in enumerate(doc_chunks))
        context_parts.append(f"Document sources:\n{doc_context}")
    if web_results:
        web_context = "\n\n---\n\n".join(
            f"[Web Source {i+1} - {r['title']} ({r['url']})]: {r['content']}" for i, r in enumerate(web_results)
        )
        context_parts.append(f"Web sources:\n{web_context}")

    full_context = "\n\n===\n\n".join(context_parts)
    prompt = f"{full_context}\n\nQuestion: {question}"

    llm = get_llm_provider()
    answer = await llm.generate(prompt=prompt, system=RAG_SYSTEM_PROMPT)

    return {
        "answer": answer,
        "sources": [
            {"document_id": c["document_id"], "excerpt": c["text"][:200], "relevance_score": round(c["score"], 3)}
            for c in doc_chunks
        ],
        "web_sources": [{"title": r["title"], "url": r["url"]} for r in web_results],
    }
