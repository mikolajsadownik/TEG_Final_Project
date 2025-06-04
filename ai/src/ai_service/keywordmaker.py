import os
from openai import OpenAI
import sys
import json
from ai_errors import BadAiApiRes, BadUserPrompt, AiAgentError
import ai_prompts as aiP
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.query_pinecone_with_gpt import query_pinecone, generate_response
import json
import re
import pandas as pd
import numpy as np


class KeyWordMaker:

       
    def __init__(self,ai_model="gpt-3.5-turbo"):
        self.model=ai_model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        pass

    def chunk_list(self,lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
            
    def create_key_words_from_querry(self,keywords,prompt):
        matches = []
        for batch in self.chunk_list(keywords, 50):
            system_prompt = aiP.prompt_create_key_words_from_querry(batch=batch,prompt=prompt)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}]
            )
            if not response.choices or not response.choices[0].message.content.strip():
                print("Pusta odpowiedź od modelu")
            else:
                res=json.loads(response.choices[0].message.content)

                for r in res:
                    if not r in matches and r in keywords:
                        matches.append(r)
        return matches



    def extract_json_from_text(self,text):
        try:
            json_text = re.search(r'\[.*\]', text, re.DOTALL).group(0)
            return json.loads(json_text)
        except Exception as e:
            print("Błąd wyciągania JSON-a:", e)
            print("Pełny tekst:", text)
            return None

    def evaluate_keywords_against_query(self,prompt, keywords, model="gpt-3.5-turbo"):
        keywords_json = json.dumps(keywords, ensure_ascii=False)

        system_message = "Jesteś prawnikiem, który ocenia słowa kluczowe względem pytania użytkownika."
        user_message = aiP.evaluate_keywords_against_query(prompt,keywords_json)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )

        text_response = response.choices[0].message.content
        print("Odpowiedź modelu:", repr(text_response))  # do debugowania

        result = self.extract_json_from_text(text_response)
        if result is None:
            return []

        passed_keywords = [r["keyword"] for r in result if r.get("pasuje") is True]
        return passed_keywords


    def create_keywords_from_prompt(self,prompt, keywords):
        new_keywords=self.create_key_words_from_querry(keywords,prompt)
        evkeywords=self.evaluate_keywords_against_query(new_keywords,prompt)
        return evkeywords