import os
import pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Załaduj zmienne środowiskowe
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

# Wyczyść stare zmienne środowiskowe (tylko po załadowaniu .env)
os.environ.pop("PINECONE_API_KEY", None)
os.environ.pop("PINECONE_ENVIRONMENT", None)
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("PINECONE_INDEX_NAME", None)
os.environ.pop("PINECONE_NAMESPACE", None)

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

# Klucze API
PINECONE_API_KEY = os.environ.pop("PINECONE_API_KEY", None)
PINECONE_ENVIRONMENT = os.environ.pop("PINECONE_ENVIRONMENT", None)
OPENAI_API_KEY = os.environ.pop("OPENAI_API_KEY", None)
INDEX_NAME = os.environ.pop("PINECONE_INDEX_NAME", "sample-index")
NAMESPACE = os.environ.pop("PINECONE_NAMESPACE", "default")

# Inicjalizacja Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Sprawdzenie, czy indeks istnieje
if INDEX_NAME not in pc.list_indexes().names():
    print(f"❌ Indeks '{INDEX_NAME}' nie istnieje. Sprawdź konfigurację Pinecone.")
    exit(1)

# Połączenie z istniejącym indeksem
index = pc.Index(INDEX_NAME)

# Inicjalizacja modelu embeddingów
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Inicjalizacja ChatGPT
chat = ChatOpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY)


def query_pinecone(query_text):
    """Wykonaj zapytanie do Pinecone i zwróć najlepsze dopasowania."""
    query_embedding = embedding_model.encode([query_text])[0]
    results = index.query(vector=query_embedding.tolist(), top_k=50, namespace=NAMESPACE, include_metadata=True)

    if len(results['matches']) == 0:
        print("❌ Nie znaleziono odpowiednich danych w bazie.")
        return None

    # Łączenie wyników w jeden kontekst
    context = "\n".join([match['metadata']['text'] for match in results['matches']])
    return context


def generate_response(context, user_question):
    """Wykonaj zapytanie do OpenAI GPT z kontekstem."""
    if not context.strip():
        return "Przepraszam, nie znalazłem odpowiednich informacji w bazie danych."

    system_message = "You are helpful personal assistant. While responding use only information from received context."

    response = chat.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Kontekst:\n{context}\n\nPytanie: {user_question}")
    ])

    return response.content.strip()


def main():
    user_question = "Jakie mamy kodeksy w polskim prawie"
    context = query_pinecone(user_question)

    if context:
        response = generate_response(context, user_question)
        print(f"\n🗣️ Odpowiedź GPT:\n{response}")
    else:
        print("Przepraszam, nie znalazłem odpowiednich informacji w bazie danych.")


if __name__ == "__main__":
    main()
