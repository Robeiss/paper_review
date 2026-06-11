# Paper Review API

Python backend for the thesis format guide.

## Run

```powershell
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints

- `GET /api/health`
- `GET /api/rule-versions/current`
