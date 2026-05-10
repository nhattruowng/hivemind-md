# Contributing

Thanks for taking the time to contribute.

## Quick Start (Local Dev)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Pull Requests

- Keep changes focused and small when possible.
- Add/adjust tests if behavior changes.
- Ensure CI passes (backend tests + frontend build).

## Reporting Issues

- Include steps to reproduce, expected behavior, and actual behavior.
- Attach relevant logs (remove secrets).

