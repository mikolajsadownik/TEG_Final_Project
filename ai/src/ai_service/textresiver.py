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
class TextResiver:
        
    def __init__(self,ai_model="gpt-3.5-turbo"):
        self.model=ai_model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        pass

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
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        else: raise BadUserPrompt(user_prompt)

    def check_pinecone_context(self,user_prompt):
        try:
            ref_prompt = self.refine_user_prompt(user_prompt=user_prompt)
        except AiAgentError as e: 
            return e.args[0]
        context = query_pinecone(ref_prompt)
        ans = generate_response(context=context,user_question=ref_prompt)
        return ans



    def define_legal_code(self,user_prompt):
        system_prompt = aiP.prompt_define_legal_code(user_prompt=user_prompt)
        ref_prompt=self.refine_user_prompt(user_prompt)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
            ]
        )
        return response.choices[0].message.content

