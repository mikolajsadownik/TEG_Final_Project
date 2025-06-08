import os
import fitz  # PyMuPDF
import pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

# Pinecone config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sample-index")

# Ścieżka do katalogu z PDF-ami
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

# Model embeddingów
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Splitter tekstu
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
        separators=[r"\n\n", r"\n", r"Art\. ", r"§ ", r"Rozdział ", r"DZIAŁ ", r"Tytuł ", r" "]
    )
    return splitter.split_documents(documents)

# Główna logika przetwarzania
def process_and_index():
    for filename in os.listdir(PDF_DIRECTORY):
        if not filename.endswith(".pdf"):
            continue

        namespace = filename.replace(".pdf", "").lower()
        file_path = os.path.join(PDF_DIRECTORY, filename)
        print(f"\n📄 Przetwarzanie pliku: {filename} → namespace: {namespace}")

        # Wczytaj tekst z każdej strony
        doc = fitz.open(file_path)
        pages = [page.get_text() for page in doc if page.get_text().strip()]
        documents = [Document(page_content=text) for text in pages]

        if not documents:
            print("⚠️ Brak tekstu do przetworzenia!")
            continue

        chunks = split_documents(documents)
        print(f"✂️ Podzielono na {len(chunks)} chunków.")

        for i, chunk in enumerate(chunks):
            embedding = embedding_model.embed_documents([chunk.page_content])[0]
            vector = (f"{namespace}-chunk-{i}", embedding, {"text": chunk.page_content})
            index.upsert(vectors=[vector], namespace=namespace)
            print(f"✅ Wysłano {i+1}/{len(chunks)}")

    print("\n✅ Wszystkie dokumenty zostały przetworzone i zaindeksowane.")

if __name__ == "__main__":
    process_and_index()
