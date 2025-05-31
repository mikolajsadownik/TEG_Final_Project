import os
from openai import OpenAI
import sys
from ai_errors import BadAiApiRes, BadUserPrompt, AiAgentError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.query_pinecone_with_gpt import query_pinecone, generate_response



client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
code_list = [
    "Kodeks cywilny","Kodeks postępowania cywilnego","Kodeks karny","Kodeks postępowania karnego","Kodeks pracy","Kodeks spółek handlowych","Kodeks rodzinny i opiekuńczy","Kodeks postępowania administracyjnego","Kodeks wykroczeń"
]


def cheack_if_good_prompt(user_prompt):
    system_prompt = (
        f"""Jesteś doświadczonym prawnikiem, który ocenia, czy dana wypowiedź użytkownika może wskazywać na sytuację związaną z potrzebą pomocy prawnej lub rady prawnika.
        Twoim zadaniem jest odpowiedzieć tylko i wyłącznie:
        - `True` — jeśli wypowiedź użytkownika w jakikolwiek sposób wskazuje na możliwe zagadnienie prawne, np. naruszenie prawa, wykroczenie, spór cywilny, problem z umową, odpowiedzialność prawną, prawo pracy, rodzinne, administracyjne lub inne kwestie regulowane prawem,
        - `False` — tylko jeśli wypowiedź jest całkowicie neutralna, nie dotyczy w żadnym aspekcie prawa ani odpowiedzialności prawnej.
        Uwzględnij wszelkie niuanse, nawet jeśli wypowiedź jest nieformalna, żartobliwa, wulgarna czy niepełna. Jeśli masz wątpliwość, odpowiedz `True`.
        Oceń następującą wypowiedź:
        **"{user_prompt}"**""")
            
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
    system_prompt = (
       f""" Jesteś prawnikiem specjalizującym się w prawie karnym.

        Twoim zadaniem jest przekształcenie wypowiedzi użytkownika, która może być nieformalna, w precyzyjne i profesjonalne zapytanie prawne, które można użyć do przeszukiwania dokumentów prawnych.

        WAŻNE: Zachowaj dokładny sens, intencję i kontekst oryginalnej wypowiedzi. Nie interpretuj, nie dodawaj własnych założeń ani rozszerzeń znaczenia. Przekształć wypowiedź jedynie na bardziej formalny i klarowny język prawniczy.

        Oto wypowiedź użytkownika:
        {user_prompt}"""
    )
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
    system_prompt = (
        "Jesteś prawnikiem specjalizującym się w polskich kodeksach prawnych. "
        "Na podstawie pytania użytkownika zdecyduj, który z poniższych kodeksów należy przeszukać. "
        "Zwróć **tylko i wyłącznie** dokładną nazwę jednego z poniższych kodeksów, bez dodatkowych wyjaśnień.\n\n"
        f"Lista kodeksów: {', '.join(code_list)}"
    )
    ref_prompt=refine_user_prompt(user_prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ref_prompt}
        ]
    )
    return response.choices[0].message.content


print(check_pinecone_context("czy mogę nasiakać do automatu z jedzeniem"))