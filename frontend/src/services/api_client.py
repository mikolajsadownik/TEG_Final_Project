from __future__ import annotations
import logging
import os
from typing import Any, Dict
import requests 
from dotenv import load_dotenv


load_dotenv()
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
SESSION = requests.Session()
LOGGER = logging.getLogger(__name__)



def ask_question(question: str) -> Dict[str, Any]:
    """
    Wysyła zapytanie do endpointu /ask i zwraca odpowiedź w formacie JSON.
    requests.HTTPError - Gdy backend zwróci kod różny od 200.
    """
    url = f"{BACKEND_URL.rstrip('/')}/ask"
    payload = {"question": question}
    LOGGER.debug("POST %s payload=%s", url, payload)

    resp = SESSION.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()  # chce miec: {"answer": "...", "sources": [...]}
