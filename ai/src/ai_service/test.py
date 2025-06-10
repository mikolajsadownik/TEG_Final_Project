import pandas as pd

from keywordmaker import KeyWordMaker
import numpy as np
from textresiver import TextResiver
from actsjson_service import json_context
import sys
import os
from ai_errors import  AiAgentError

sciezka_pliku = os.path.abspath(__file__)
folder_pliku = os.path.dirname(sciezka_pliku)
keywords=f"{folder_pliku}/data/key_words.json"



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.query_pinecone_with_gpt import query_pinecone_via_namespace, generate_response,query_pinecone



kwm=KeyWordMaker(keywords)
# Dopasuj najbardziej podobne zestawy (np. top 3)
tr=TextResiver()
pytanie="Co grozi za zabójstwo z szczetgólnym okrucieśtwioe"
with open(f"{folder_pliku}\pytania.txt", "r", encoding="utf-8") as file:
    questions = [line.strip() for line in file.readlines()]
    print(questions) 
    for q in questions:
        try:
            ans,ref_prompt=tr.check_pinecone_context(q)
        except AiAgentError as e:
            print(e.args[0])
        for a in ans:
            print("------\n")
            print(a["code"])
            print(a["ans"])

        keywords = kwm.create_keywords_from_prompt(ref_prompt)
        odp=json_context(ref_prompt,keywords)

        if len(odp)>0:
            print("CUHKJFAGSGHASHUHGBAUISNFDJKABGIAJKGBHJIASBGNJASNGJKLNSAJKLGNUIOAW")
            response = generate_response(odp[0]["text"], ref_prompt)
            print(response)
            print("CUHKJFAGSGHASHUHGBAUISNFDJKABGIAJKGBHJIASBGNJASNGJKLNSAJKLGNUIOAW")
            
# with open(r"C:\Users\jarja\Desktop\Studia\teg\TEG_Final_Project\MOJtest\acts_backup.json", "r", encoding="utf-8") as f:
#     data = [json.loads(line) for line in f]

# print(data["displayAddress"])
