import pandas as pd
from rapidfuzz import fuzz, process
import json
from keywordmaker import KeyWordMaker
import numpy as np
from textresiver import TextResiver
from actsjson_service import json_context

keywords=r"C:\Users\jarja\Desktop\Studia\teg\TEG_Final_Project\ai\src\ai_service\data\key_words.json"

kwm=KeyWordMaker(keywords)
# Dopasuj najbardziej podobne zestawy (np. top 3)
tr=TextResiver()
pytanie="Czy pracodawca może rozwiązać umowę o pracę bez wypowiedzenia z powodu nieusprawiedliwionej nieobecności pracownika?"
prompt=tr.refine_user_prompt(pytanie)
ans=tr.check_pinecone_context(prompt)

keywords = kwm.create_keywords_from_prompt(prompt)

odp=json_context(prompt,keywords)
# with open(r"C:\Users\jarja\Desktop\Studia\teg\TEG_Final_Project\MOJtest\acts_backup.json", "r", encoding="utf-8") as f:
#     data = [json.loads(line) for line in f]

# print(data["displayAddress"])
