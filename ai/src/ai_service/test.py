import os
import sys
import json
import pandas as pd

# 🔧 Dodaj katalog "src" (tam, gdzie jest folder services/) do sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 📥 Importy po dołączeniu src/ do ścieżki
from keywordmaker import KeyWordMaker
from textresiver import TextResiver
from actsjson_service import json_context
from ai_errors import AiAgentError
from services.query_pinecone_with_gpt import generate_response

# 🔍 Ustawienia ścieżek
sciezka_pliku = os.path.abspath(__file__)
folder_pliku = os.path.dirname(sciezka_pliku)
keywords_path = os.path.join(folder_pliku, "data", "key_words.json")
pytania_path = os.path.join(folder_pliku, "pytania.txt")

# ⚙️ Inicjalizacja
kwm = KeyWordMaker(key_words_path=keywords_path)
tr = TextResiver()

# 📄 Wczytaj pytania z pliku
with open(pytania_path, "r", encoding="utf-8") as file:
    questions = [line.strip() for line in file.readlines()]
    print(f"📘 Wczytano {len(questions)} pytań.")

# 🔁 Przetwarzanie każdego pytania
for q in questions:
    print(f"\n📥 Pytanie: {q}")
    try:
        odpowiedzi, ref_prompt = tr.check_pinecone_context(q)
    except AiAgentError as e:
        print(f"❌ Błąd AI: {e.args[0]}")
        continue

    print("🔎 Odpowiedzi z Pinecone:")
    for a in odpowiedzi:
        print(f"\n🔸 Kodeks: {a['code']}\n{a['ans']}")

    keywords = kwm.create_keywords_from_prompt(ref_prompt)
    dopasowania = json_context(ref_prompt, keywords)

    if dopasowania:
        print("\n🧠 Odpowiedź na podstawie embeddingów:")
        odpowiedz_embedding = generate_response(dopasowania[0]["text"], ref_prompt)
        print(odpowiedz_embedding)
    else:
        print("\n⚠️ Brak trafnych dopasowań w dokumentach.")
