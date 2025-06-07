import pandas as pd
from rapidfuzz import fuzz, process
import json
from keywordmaker import KeyWordMaker
import numpy as np
from textresiver import TextResiver


keywords=r"C:\Users\jarja\Desktop\Studia\teg\TEG_Final_Project\ai\src\ai_service\key_words.json"

kwm=KeyWordMaker(keywords)
# Dopasuj najbardziej podobne zestawy (np. top 3)
tr=TextResiver()
prompt=tr.refine_user_prompt("Czy pracodawca może rozwiązać umowę o pracę bez wypowiedzenia z powodu nieusprawiedliwionej nieobecności pracownika?")
ans=tr.check_pinecone_context(prompt)

print(ans)
query = kwm.create_keywords_from_prompt(prompt)
print(query)

# with open(r"C:\Users\jarja\Desktop\Studia\teg\TEG_Final_Project\MOJtest\acts_backup.json", "r", encoding="utf-8") as f:
#     data = [json.loads(line) for line in f]

# print(data["displayAddress"])
