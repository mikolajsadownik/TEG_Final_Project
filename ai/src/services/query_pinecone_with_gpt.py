import os
from pinecone import Pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


load_dotenv()

PINECONE_API_KEY       = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT   = os.getenv("PINECONE_ENVIRONMENT")
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY")
INDEX_NAME             = os.getenv("PINECONE_INDEX_NAME", "sample-index")
NAMESPACE              = os.getenv("PINECONE_NAMESPACE", "default")


pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pc.Index(INDEX_NAME)


embedding_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
chat            = ChatOpenAI(
    temperature=0.55,
    model_name="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)

def query_pinecone(query_text: str) -> str:
    emb    = embedding_model.encode([query_text])[0]
    res    = index.query(vector=emb.tolist(),
                         top_k=10,
                         namespace=NAMESPACE,
                         include_metadata=True)
    matches = res["matches"]
    if not matches:
        return ""
    return "\n".join(m["metadata"]["text"] for m in matches)

def query_pinecone_via_namespace(namespace,query_text):
    """Wykonaj zapytanie do Pinecone i zwróć najlepsze dopasowania."""
    query_embedding = embedding_model.encode([query_text])[0]
    results = index.query(vector=query_embedding.tolist(), top_k=10, namespace=namespace, include_metadata=True)
    if len(results['matches']) == 0:
        print("Nie znaleziono odpowiednich danych w bazie.")
        return "Error: Nie znaleziono odpowiednich danych w bazie."

    # Łączenie wyników w jeden kontekst
    context = "\n".join([match['metadata']['text'] for match in results['matches']])
    return context



def generate_response(context: str, user_question: str) -> str:
    if not context.strip():
        return "Przepraszam, nie znalazłem informacji."
    system = SystemMessage(
        content="You are a legal assistant. Use only provided context."
    )
    human  = HumanMessage(
        content=f"Kontekst:\n{context}\n\nPytanie: {user_question}"
    )
    reply  = chat.invoke([system, human])
    return reply.content.strip()


def main():
    user_question = "Czy mogę sprzedawać na ulicy swoje rzeczy?"
    context = query_pinecone(user_question)

    if context:
        response = generate_response(context, user_question)
        print(f"\n Odpowiedź GPT:\n{response}")
    else:
        print("Przepraszam, nie znalazłem odpowiednich informacji w bazie danych.")


if __name__ == "__main__":
    main()
