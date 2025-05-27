import os
from openai import OpenAI
import query_pinecone_with_gpt as qpg

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def refine_user_prompt(user_prompt):
    system_prompt = (
        "Jesteś prawnikiem specjalizującym się w prawie karnym. "
        "Twoim zadaniem jest przekształcenie wypowiedzi użytkownika w precyzyjne, profesjonalne zapytanie prawne, "
        "które można użyć do przeszukiwania Kodeksu karnego lub orzecznictwa. "
        "Użytkownik może pisać nieformalnie."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content
def check_pinecone_context(user_prompt):
    ref_prompt = refine_user_prompt(user_prompt=user_prompt)
    context = qpg.query_pinecone(ref_prompt)
    ans = qpg.generate_response(context=context,user_question=ref_prompt)
    return ans
code_list = [
    "Kodeks cywilny",
    "Kodeks postępowania cywilnego",
    "Kodeks karny",
    "Kodeks postępowania karnego",
    "Kodeks pracy",
    "Kodeks spółek handlowych",
    "Kodeks rodzinny i opiekuńczy",
    "Kodeks postępowania administracyjnego",
    "Kodeks wykroczeń"
]


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

print(define_legal_code("Ej, a jak to jest z tymi mandatami? Kiedy można kogoś wylegitymować?"))