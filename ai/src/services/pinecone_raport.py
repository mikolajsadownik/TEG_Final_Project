import os
import fitz  # PyMuPDF
import pinecone
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sample-index")

# Inicjalizacja Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Ścieżka do katalogu z PDF-ami
PDF_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../kodeksy_prawne"))

# Lista namespace’ów / plików PDF
namespace_list = [
    "kodeks_cywilny",
    "kodeks_karny",
    "kodeks_postepowania_cywilnego",
    "kodeks_pracy",
    "kodeks_spolek_handlowych",
    "kodeks_rodzinny_i_opiekunczy",
    "kodeks_postepowania_karnego",
    "kodeks_wykroczen",
    "kodeks_postepowania_administracyjnego",
    "kodeks_karny_skarbowy",
    "kodeks_wyborczy",
    "kodeks_morski"
]

print("📊 Zestawienie: liczba chunków i liczba stron w PDF:\n")

for ns in namespace_list:
    # 🔹 Pobierz liczbę chunków z Pinecone
    stats = index.describe_index_stats(namespace=ns)
    chunk_count = stats["namespaces"].get(ns, {}).get("vector_count", 0)

    # 🔹 Odczytaj liczbę stron w PDF
    pdf_path = os.path.join(PDF_DIRECTORY, f"{ns}.pdf")
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        page_count = len(doc)
    else:
        page_count = "❌ brak pliku"

    print(f"📂 {ns:<40} | 📄 Stron: {str(page_count):>5} | 🧩 Chunków: {chunk_count}")
