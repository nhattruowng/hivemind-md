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
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If the port is already in use (for example you see `WinError 10013` or "address already in use"), stop the process that is listening on the port and retry.

Windows (PowerShell):

```powershell
$port = 8000
$pid = (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)
if ($pid) { Stop-Process -Id $pid -Force }
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS / Linux:

```bash
kill -9 "$(lsof -ti :8000)" 2>/dev/null || true
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
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
