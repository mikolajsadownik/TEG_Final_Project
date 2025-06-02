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



client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
code_list = [
    "Kodeks_cywilny","Kodeks postępowania cywilnego","Kodeks karny","Kodeks postępowania karnego","Kodeks pracy","Kodeks spółek handlowych","Kodeks rodzinny i opiekuńczy","Kodeks postępowania administracyjnego","Kodeks wykroczeń"
]

key_words_path="key_words.json"




def cheack_if_good_prompt(user_prompt):
    system_prompt = aiP.prompy_cheack_if_good_prompt(user_prompt)
            
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}])
    
    res = response.choices[0].message.content.strip()
    print(res)

    if res =="True":
        return True
    elif res == "False":
        return False
    else:
        raise BadAiApiRes(res)

def refine_user_prompt(user_prompt):
    system_prompt = aiP.prompt_refine_user_prompt(user_prompt)
    try:
        valid_prompt=cheack_if_good_prompt(user_prompt)
    except BadAiApiRes as e:
        print(e)

    if valid_prompt:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
            ]
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    else: raise BadUserPrompt(user_prompt)

def check_pinecone_context(user_prompt):
    try:
        ref_prompt = refine_user_prompt(user_prompt=user_prompt)
    except AiAgentError as e: 
        return e.args[0]
    context = query_pinecone(ref_prompt)
    ans = generate_response(context=context,user_question=ref_prompt)
    return ans



def define_legal_code(user_prompt):
    system_prompt = aiP.prompt_define_legal_code(user_prompt=user_prompt)
    ref_prompt=refine_user_prompt(user_prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
        ]
    )
    return response.choices[0].message.content



def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def create_key_words_from_querry(keywords,prompt):
    matches = []
    for batch in chunk_list(keywords, 100):
        system_prompt = aiP.prompt_create_key_words_from_querry(batch=batch,prompt=prompt)
        
        response = client.chat.completions.create(
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



def extract_json_from_text(text):
    try:
        json_text = re.search(r'\[.*\]', text, re.DOTALL).group(0)
        return json.loads(json_text)
    except Exception as e:
        print("Błąd wyciągania JSON-a:", e)
        print("Pełny tekst:", text)
        return None

def evaluate_keywords_against_query(prompt, keywords, model="gpt-3.5-turbo"):
    keywords_json = json.dumps(keywords, ensure_ascii=False)

    system_message = "Jesteś prawnikiem, który ocenia słowa kluczowe względem pytania użytkownika."
    user_message = aiP.evaluate_keywords_against_query(prompt,keywords_json)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    text_response = response.choices[0].message.content
    print("Odpowiedź modelu:", repr(text_response))  # do debugowania

    result = extract_json_from_text(text_response)
    if result is None:
        return []

    passed_keywords = [r["keyword"] for r in result if r.get("pasuje") is True]
    return passed_keywords


print(check_pinecone_context("Czy można palić marihuana w kościele"))