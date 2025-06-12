import os
import fitz  # PyMuPDF
import pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Załaduj zmienne środowiskowe
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

# Ustawienia Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sample-index")

# Inicjalizacja Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Sprawdzenie, czy indeks już istnieje
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=pinecone.ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
    )

# Połączenie z indeksem Pinecone
index = pc.Index(INDEX_NAME)

# Inicjalizacja modelu embeddingów
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Ścieżka do katalogu PDF
PDF_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))


def read_pdfs(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            print(f"Loading {file_path}...")
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            documents.append(Document(page_content=text))
    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        length_function=len,
        separators=[r"\n\n", r"\n", r"Art\. ", r"§ ", r"Rozdział ", r"DZIAŁ ", r"Tytuł ", r" "]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Podzielono dokument na {len(chunks)} fragmentów.")
    return chunks


def embed_and_upsert(chunks, namespace="default"):
    for i, chunk in enumerate(chunks):
        embedding = embedding_model.embed_documents([chunk.page_content])[0]
        vector = (f"doc-{i}", embedding, {"text": chunk.page_content})
        index.upsert(vectors=[vector], namespace=namespace)
        print(f"Upserted chunk {i+1}/{len(chunks)}")


def main():
    documents = read_pdfs(PDF_DIRECTORY)
    chunks = split_documents(documents)
    print(chunks)
    embed_and_upsert(chunks)
    print("Pinecone index updated successfully!")


if __name__ == "__main__":
    main()
