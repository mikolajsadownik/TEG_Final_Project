import os
import pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings

# Załaduj zmienne środowiskowe
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "sample-index")

# Inicjalizacja Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Inicjalizacja modelu embeddingów
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def test_pinecone_existing_data(query_text, expected_text):
    # Generowanie embeddingu dla zapytania
    query_embedding = embedding_model.embed_documents([query_text])[0]

    # Wykonanie zapytania do Pinecone
    results = index.query(vector=query_embedding, top_k=1, include_metadata=True)

    # Sprawdzenie wyników
    assert len(results.matches) > 0, "Brak wyników w bazie danych!"
    assert expected_text in results.matches[0].metadata["text"], f"Niepoprawny wynik wyszukiwania! Oczekiwano: {expected_text}, znaleziono: {results.matches[0].metadata['text']}"
    print(f"Test zakończony sukcesem! Znaleziono: {results.matches[0].metadata['text']}")


if __name__ == "__main__":
    # Przetestuj istniejace dane z PDF (Art. 1, par. 1)
    test_pinecone_existing_data("Małżeństwo zostaje zawarte", "Małżeństwo zostaje zawarte, gdy mężczyzna i kobieta jednocześnie obecni złożą przed kierownikiem urzędu stanu cywilnego oświadczenia, że wstępują ze sobą w związek małżeński.")





