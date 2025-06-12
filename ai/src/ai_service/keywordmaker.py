import os
import sys
import json
import re
import pandas as pd
import numpy as np

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import LangChainTracer

from ai_errors import BadAiApiRes, BadUserPrompt, AiAgentError
import ai_prompts as aiP
from basemodel import BaseModel
from services.query_pinecone_with_gpt import query_pinecone, generate_response


src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.append(src_path)


# model do wytworzenia i sprawdzenia czy wytworzone słowa klucz są odpowiednie
class KeyWordMaker(BaseModel):

    def __init__(self, key_words_path, ai_model="gpt-3.5-turbo"):
        super().__init__(name="KeyWordMaker", model=ai_model)
        self.keywords = np.array(pd.read_json(key_words_path, encoding="cp1250")[0])

    def chunk_list(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def create_key_words_from_querry(self, keywords, prompt):
        matches = []
        for batch in self.chunk_list(keywords, 150):
            system_prompt = "Jesteś prawnikiem specjalizującym się w doborze słów kluczowych pod daną sytuację."
            user_message = aiP.prompt_create_key_words_from_querry(batch=batch, prompt=prompt)

            try:
                response = self.client.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ])

                if not response.content.strip():
                    print("Pusta odpowiedź od modelu")
                    continue

                res = json.loads(response.content)
                for r in res:
                    if r not in matches and r in keywords:
                        matches.append(r)
            except json.JSONDecodeError as e:
                print(f"Błąd dekodowania JSON: {e}")
            except Exception as e:
                print(f"Błąd wywołania modelu: {e}")
        return matches

    def extract_json_from_text(self, text):
        try:
            json_text = re.search(r'\[.*\]', text, re.DOTALL).group(0)
            return json.loads(json_text)
        except Exception as e:
            print("Błąd wyciągania JSON-a:", e)
            print("Pełny tekst:", text)
            return None

    def evaluate_keywords_against_query(self, prompt, keywords):
        keywords_json = json.dumps(keywords, ensure_ascii=False)

        system_message = "Jesteś specjalistą od prawa i regulacji. Twoim zadaniem jest ocena, czy dane słowo kluczowe może mieć zastosowanie w kontekście przepisów prawa (karnego, administracyjnego, sanitarnego itp.) względem danego zapytania – nawet jeśli zapytanie jest nietypowe."
        user_message = aiP.evaluate_keywords_against_query(prompt, keywords_json)

        try:
            response = self.client.invoke([
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ])
            text_response = response.content
            result = self.extract_json_from_text(text_response)
            if result is None:
                return []
            passed_keywords = [r["keyword"] for r in result if r.get("pasuje") is True]
            return passed_keywords
        except Exception as e:
            print(f"Błąd oceny słów kluczowych: {e}")
            return []

    def create_keywords_from_prompt(self, prompt):
        new_keywords = self.create_key_words_from_querry(self.keywords, prompt)
        evkeywords = self.evaluate_keywords_against_query(prompt, new_keywords)
        return evkeywords
