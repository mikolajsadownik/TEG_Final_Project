import os
import re
import fitz  # PyMuPDF
import pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv
from pinecone.exceptions import NotFoundException

# Załaduj zmienne środowiskowe
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sample-index")

PDF_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../kodeksy_prawne"))

# Inicjalizacja Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=pinecone.ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
    )
index = pc.Index(INDEX_NAME)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 🔹 Dziel tekst na artykuły (Art. XX.)
def split_by_article(text: str):
    parts = re.split(r'(Art\. ?\d+[a-zA-Z]*\.)', text)
    articles = []
    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        articles.append(Document(page_content=header + " " + body.strip()))
    return articles

# 🔹 Przetwarzanie PDF-ów
def process_and_index():
    for filename in os.listdir(PDF_DIRECTORY):
        if not filename.endswith(".pdf"):
            continue

        namespace = filename.replace(".pdf", "").lower()
        file_path = os.path.join(PDF_DIRECTORY, filename)
        print(f"\n📄 Przetwarzanie pliku: {filename} → namespace: {namespace}")

        doc = fitz.open(file_path)
        full_text = "\n".join([page.get_text() for page in doc if page.get_text().strip()])

        if not full_text.strip():
            print("⚠️ Brak tekstu do przetworzenia!")
            continue

        chunks = split_by_article(full_text)
        print(f"✂️ Podzielono na {len(chunks)} artykułów.")

        try:
            index.delete(delete_all=True, namespace=namespace)
            print(f"🧹 Usunięto dane z namespace: {namespace}")
        except NotFoundException:
            print(f"ℹ️ Namespace '{namespace}' był pusty – pomijam usuwanie.")

        for i, chunk in enumerate(chunks):
            embedding = embedding_model.embed_documents([chunk.page_content])[0]
            vector = (f"{namespace}-art-{i}", embedding, {"text": chunk.page_content})
            index.upsert(vectors=[vector], namespace=namespace)
            print(f"✅ Wysłano artykuł {i+1}/{len(chunks)}")

    print("\n✅ Wszystkie dokumenty zostały przetworzone i zaindeksowane.")

if __name__ == "__main__":
    process_and_index()
