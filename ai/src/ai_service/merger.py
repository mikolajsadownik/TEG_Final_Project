

from ai_service.keywordmaker import KeyWordMaker
from ai_service.textresiver import TextResiver
from ai_service.actsjson_service import json_context
import os
from ai_service.ai_errors import  AiAgentError, BadUserPrompt
from src.services.query_pinecone_with_gpt import  generate_response
import ai_service.ai_prompts as aiP
from ai_service.basemodel import BaseModel

sciezka_pliku = os.path.abspath(__file__)
folder_pliku = os.path.dirname(sciezka_pliku)
keywords=f"{folder_pliku}/data/key_words.json"
class MergerAI(BaseModel):

    def __init__(self, ai_model="gpt-3.5-turbo"):
        super().__init__(name="MergerAI", model=ai_model)
        self.tr=TextResiver()
        self.kwm=KeyWordMaker(keywords)
    def mange_ai_agents(self,prompt):
        allodp=[]
        try:
            ans,ref_prompt=self.tr.check_pinecone_context(prompt)
        except BadUserPrompt as e:
            return["ERROR - Bledne zapytanie uzytkownika"]
        for a in ans:
            allodp.append(a["ans"])
            print("------\n")
            print(a["code"])
            print(a["ans"])
        system_prompt= aiP.prompt_cheack_if_enough(prompt,allodp)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}])

        
        print("======================================================")
        res = response.choices[0].message.content.strip()
        print(res)
        if res=="True":
            return allodp
        keywords = self.kwm.create_keywords_from_prompt(ref_prompt)
        odp=json_context(ref_prompt,keywords)
        if len(odp)>0:
            response = generate_response(odp[0]["text"], ref_prompt)
            allodp.append(response)
            # print(response)
        return allodp

    def merge_ans(self,prompt):
        allodp=self.mange_ai_agents(prompt)
        system_prompt = aiP.prompt_merger(prompt,allodp)
        
        response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}])
        
        res = response.choices[0].message.content.strip()
        return res
        

# mai=MergerAI()
# print(mai.merge_ans("Czy moge zabrac czekoladę ze sklepu"))

