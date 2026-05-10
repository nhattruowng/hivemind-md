# HiveMind MD Backend

FastAPI backend cho workflow local-first: crawl web, tao Markdown knowledge, index vector va chat RAG qua Ollama.

Mac dinh backend dung JSON vector fallback de cai dat nhe va tranh loi build `tokenizers`/Rust tren Windows. Neu muon dung ChromaDB, cai them `requirements-chroma.txt` bang Python 3.11-3.12.

## Chay local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tren Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Neu can ChromaDB:

```powershell
pip install -r requirements-chroma.txt
```

## API chinh

- `GET /api/health`
- `GET /api/health/ollama`
- `GET /api/agent-framework/profiles`
- `POST /api/agent-framework/run`
- `POST /api/agents/build-knowledge`
- `POST /api/knowledge/refresh`
- `GET /api/knowledge/map`
- `GET /api/knowledge`
- `GET /api/knowledge/read?file_path=...`
- `DELETE /api/knowledge/delete`
- `POST /api/chat`
