"""Minimal embedding server using sentence-transformers/all-MiniLM-L6-v2.

POST /embed  body {"text": "..."} -> first 8 dims of a 384-dim embedding.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Embedder")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


class EmbedRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ok", "model": "all-MiniLM-L6-v2"}


@app.post("/embed")
def embed(req: EmbedRequest):
    vec = model.encode(req.text).tolist()
    return {
        "text": req.text,
        "dim": len(vec),
        "embedding_preview": vec[:8],
    }
