from fastapi import FastAPI

from .database import init_db

# Import routers package (we'll create routers/history.py and routers/risk.py)
from .routers import history, risk


app = FastAPI(
    title="Enterprise Risk Intelligence System API",
    version="0.1.0",
    description="API for assessing and monitoring enterprise risks",
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# include routers
app.include_router(risk.router)
app.include_router(history.router)
