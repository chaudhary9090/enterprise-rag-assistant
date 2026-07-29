# Enterprise RAG Knowledge Assistant

A working Retrieval-Augmented Generation (RAG) chatbot that answers questions grounded in your own uploaded documents — and blends in **live web search** for anything current, the same way ChatGPT/Claude's web-browsing features work.

Built to demonstrate real backend engineering practices: clean layered architecture, provider-agnostic LLM/embedding integrations, JWT authentication, and honest failure handling (a document that can't be read tells you so, instead of silently pretending to succeed).

## What it does

- Sign up, create a workspace, upload documents (PDF/DOCX/TXT/MD)
- Ask questions — the assistant retrieves the most relevant chunks from your documents **and** searches the live web, then answers using whichever is actually relevant, with citations for both
- Multi-tenant: workspaces are private to their owner, enforced on every route
- Swap the underlying LLM (OpenAI, Anthropic Claude, Groq, or a local Ollama model) with a single config change — no code changes required

## Why this exists

Most "RAG chatbot" tutorials wrap a single API call around `ChatGPT + one PDF`. This project instead separates concerns the way a real backend does:

```
API layer (routes) → Service layer (business logic) → Repository layer (database access)
```

Every LLM and embedding provider sits behind an abstract interface, so the app never hardcodes a specific vendor — a genuine "Open/Closed Principle" example, not just a buzzword.

## Architecture

```
frontend/index.html        Plain HTML/JS UI (no build step) — chat, upload, auth
backend/
  app/
    api/          FastAPI routes (auth, workspaces, documents, chat)
    services/     Business logic (auth, workspace ownership, document
                  processing pipeline, RAG chat orchestration, web search)
    repositories/ Direct database queries — the only layer that touches SQL
    llm/          Abstract LLMProvider interface + OpenAI/Anthropic/Ollama
                  adapters + a factory that picks one from config
    vectorstore/  Qdrant wrapper (runs embedded, no separate server needed)
    models/       SQLAlchemy tables: User, Workspace, Document
    core/         Config, database session, JWT/password security, auth
                  dependency
```

**Request flow for a chat message:**
1. `POST /workspaces/{id}/chat` → checks the caller owns the workspace
2. Embeds the question, searches Qdrant for the closest document chunks
3. Calls Tavily for live web results (if configured)
4. Hands both sets of context to the active LLM provider
5. Returns the answer plus citations for every source used

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy (async) |
| Auth | JWT, bcrypt password hashing |
| Database | PostgreSQL |
| Vector store | Qdrant (embedded/local mode — no Docker required) |
| Embeddings | fastembed (`BAAI/bge-small-en-v1.5`) — small, fast, CPU-only |
| LLM | Configurable: OpenAI, Anthropic Claude, Groq, or local Ollama |
| Web search | Tavily (free tier) |
| Frontend | Plain HTML/CSS/JS (no framework/build step) |

## Setup

### 1. Clone and install
```bash
git clone https://github.com/chaudhary9090/enterprise-rag-assistant.git
cd enterprise-rag-assistant/backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in:
```
DATABASE_URL=postgresql+asyncpg://rag_user:rag_pass@localhost:5432/rag_db
LLM_PROVIDER=groq                 # or: openai / anthropic / ollama
GROQ_API_KEY=your-key-here        # groq.com — free, no card required
TAVILY_API_KEY=your-key-here      # tavily.com — free tier, no card required
```

### 3. Create the database
```sql
CREATE USER rag_user WITH PASSWORD 'rag_pass';
CREATE DATABASE rag_db OWNER rag_user;
```

### 4. Run
```bash
python -m uvicorn app.main:app --reload
```
Open `frontend/index.html` directly in a browser, or explore the API at `http://127.0.0.1:8000/docs`.

## What's next (Phase 2)

- Hybrid search (vector + keyword/BM25) and cross-encoder reranking
- RAGAS-based evaluation (faithfulness, answer relevancy, context precision)
- Background/async document processing instead of synchronous upload
- Deployment guide (Docker Compose, single-VM hosting)

## Author

Lucky Chauhan — B.Tech, Artificial Intelligence (Parul University, 2026)
