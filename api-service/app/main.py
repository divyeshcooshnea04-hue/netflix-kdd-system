from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Netflix KDD — API Service",
    description="Read/query access to the Netflix titles collection.",
    version="1.0.0",
)

app.include_router(router, prefix="/api", tags=["titles"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "api-service"}
