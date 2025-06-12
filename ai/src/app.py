from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.query_pinecone_with_gpt import query_pinecone, generate_response

app = FastAPI(title="TEG AI Service")

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(req: AskRequest):
    try:
        ctx  = query_pinecone(req.question)
        ans  = generate_response(ctx, req.question)
        return {"answer": ans, "sources": []}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

