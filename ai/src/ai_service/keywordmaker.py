import json
import ai_service.ai_prompts as aiP
import re
import pandas as pd
import numpy as np
from ai_service.basemodel import BaseModel


# model do wytworzenia i sprawdzenia czy wytworzone słowa klucz są odpowiednie

class KeyWordMaker(BaseModel):

       
    def __init__(self, key_words_path, ai_model="gpt-3.5-turbo"):
        super().__init__(name="KeyWordMaker", model=ai_model)
        self.keywords = np.array(pd.read_json(key_words_path, encoding="cp1250")[0])
        pass

    
    def chunk_list(self,lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    def create_key_words_from_querry(self,keywords,prompt):
        matches = []
        for batch in self.chunk_list(keywords, 150):
            system_prompt = "Jesteś prawnikiem specjalizującym sie w doborze słów kluczowych pod daną sytuacje"
            user_message = aiP.prompt_create_key_words_from_querry(batch=batch,prompt=prompt)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}]
               
            )

            try:

                if not response.choices or not response.choices[0].message.content.strip():
                    print("Pusta odpowiedź od modelu")
                else:
                    res=json.loads(response.choices[0].message.content)
                    for r in res:
                        if not r in matches and r in keywords:
                            matches.append(r)
            except json.JSONDecodeError as e:
                print(f"Błąd dekodowania JSON: {e}")
            

           
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

        system_message = "Jesteś specjalistą od prawa i regulacji. Twoim zadaniem jest ocena, czy dane słowo kluczowe może mieć zastosowanie w kontekście przepisów prawa (karnego, administracyjnego, sanitarnego itp.) względem danego zapytania – nawet jeśli zapytanie jest nietypowe."
        user_message = aiP.evaluate_keywords_against_query(prompt,keywords_json)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
          
        )

        text_response = response.choices[0].message.content
        # print("Odpowiedź modelu:", repr(text_response))  

        result = self.extract_json_from_text(text_response)
        if result is None:
            return []

        passed_keywords = [r["keyword"] for r in result if r.get("pasuje") is True]
        return passed_keywords


    def create_keywords_from_prompt(self,prompt):
        new_keywords=self.create_key_words_from_querry(self.keywords,prompt)
        evkeywords=self.evaluate_keywords_against_query(prompt,new_keywords)
        return evkeywords
    
