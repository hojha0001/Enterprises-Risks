# ERIS — Enterprise Risk Intelligence System

MVP: FastAPI service with health check and CI.

## Run locally
```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/health
