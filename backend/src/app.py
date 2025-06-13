import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

AI_URL = os.getenv("AI_URL", "http://ai:9000")

app = FastAPI(title="TEG Backend")

class Ask(BaseModel):
    question: str

@app.post("/ask")
async def ask(req: Ask):
    try:
        r = requests.post(f"{AI_URL}/ask", json=req.model_dump(), timeout=600)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=r.status_code, detail=r.text) from exc
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
