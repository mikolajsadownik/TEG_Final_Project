import json
from ai_service.ai_errors import BadAiApiRes, BadUserPrompt, AiAgentError
import ai_service.ai_prompts as aiP
from services.query_pinecone_with_gpt import query_pinecone_via_namespace, generate_response,query_pinecone
import json

from ai_service.basemodel import BaseModel

#model który pierwszy dostaje wiadmości i ją przetwarza

class TextResiver(BaseModel):
        
    def __init__(self, ai_model="gpt-3.5-turbo"):
        super().__init__(name="TextReceiver", model=ai_model)
        self.CODE_MAP = {
        "Kodeks cywilny": "kodeks_cywilny",
        "Kodeks karny": "kodeks_karny",
        "Kodeks postępowania cywilnego": "kodeks_postepowania_cywilnego",
        "Kodeks pracy": "kodeks_pracy",
        "Kodeks spółek handlowych": "kodeks_spolek_handlowych",
        "Kodeks rodzinny i opiekuńczy": "kodeks_rodzinny_i_opiekunczy",
        "Kodeks postępowania karnego": "kodeks_postepowania_karnego",
        "Kodeks wykroczeń": "kodeks_wykroczen",
        "Kodeks postępowania administracyjnego": "kodeks_postepowania_administracyjnego",
        "Kodeks karny skarbowy": "kodeks_karny_skarbowy",
        "Kodeks wyborczy": "kodeks_wyborczy",
        "Kodeks morski": "kodeks_morski",
    }


    def cheack_if_good_prompt(self, user_prompt):
        system_prompt = aiP.prompy_cheack_if_good_prompt(user_prompt)
                
        response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}])
        
        res = response.choices[0].message.content.strip()
        print(res)

        if res =="True":
            return True
        elif res == "False":
            return False
        else:
            raise BadAiApiRes(res)


    def refine_user_prompt(self,user_prompt):
        system_prompt = aiP.prompt_refine_user_prompt(user_prompt)
        try:
            valid_prompt= self.cheack_if_good_prompt(user_prompt)
        except BadAiApiRes as e:
            print(e)

        if valid_prompt:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                ]
            )
            return response.choices[0].message.content
        else: raise BadUserPrompt(user_prompt)


    def check_pinecone_context(self,user_prompt):
        try:
            ref_prompt = self.refine_user_prompt(user_prompt=user_prompt)
            print(ref_prompt)
        except AiAgentError as e:
            raise BadUserPrompt(user_prompt)
        legal_code=self.define_legal_code(ref_prompt)
        legal_code_json=json.loads(legal_code)
        all_ans=[]
        for code_map in legal_code_json["proposed_codes"]:
            if code_map in self.CODE_MAP.keys():
                code=self.CODE_MAP[code_map]
                context = query_pinecone_via_namespace(code,ref_prompt)
                ans = generate_response(context=context,user_question=ref_prompt)
                g={"code":code,
                   "ans":ans}
                all_ans.append(g)

        context = query_pinecone(ref_prompt)
        ans = generate_response(context=context,user_question=ref_prompt)
        g={"code":"basa", "ans":ans}
        all_ans.append(g)
        return all_ans,ref_prompt


    def define_legal_code(self,user_prompt):
        system_prompt = aiP.prompt_define_legal_code(user_prompt=user_prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
            ]
        )

        return response.choices[0].message.content


# tr=TextResiver()
# odp=tr.check_pinecone_context("Co musze zrobić by dostać obywatelstwo polskie?")