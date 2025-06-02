
code_list = [
    "Kodeks_cywilny","Kodeks postępowania cywilnego","Kodeks karny","Kodeks postępowania karnego","Kodeks pracy","Kodeks spółek handlowych","Kodeks rodzinny i opiekuńczy","Kodeks postępowania administracyjnego","Kodeks wykroczeń"
]
def prompy_cheack_if_good_prompt(user_prompt):
    system_prompt = (
        f"""Jesteś doświadczonym prawnikiem, który ocenia, czy dana wypowiedź użytkownika może wskazywać na sytuację związaną z potrzebą pomocy prawnej lub rady prawnika.
        Twoim zadaniem jest odpowiedzieć tylko i wyłącznie:
        - `True` — jeśli wypowiedź użytkownika w jakikolwiek sposób wskazuje na możliwe zagadnienie prawne, np. naruszenie prawa, wykroczenie, spór cywilny, problem z umową, odpowiedzialność prawną, prawo pracy, rodzinne, administracyjne lub inne kwestie regulowane prawem,
        - `False` — tylko jeśli wypowiedź jest całkowicie neutralna, nie dotyczy w żadnym aspekcie prawa ani odpowiedzialności prawnej.
        Uwzględnij wszelkie niuanse, nawet jeśli wypowiedź jest nieformalna, żartobliwa, wulgarna czy niepełna. Jeśli masz wątpliwość, odpowiedz `True`.
        Oceń następującą wypowiedź:
        **"{user_prompt}"**""")
    return system_prompt

def prompt_refine_user_prompt(user_prompt):
    system_prompt = (
       f""" Jesteś prawnikiem specjalizującym się w prawie karnym.

        Twoim zadaniem jest przekształcenie wypowiedzi użytkownika, która może być nieformalna, w precyzyjne i profesjonalne zapytanie prawne, które można użyć do przeszukiwania dokumentów prawnych.

        WAŻNE: Zachowaj dokładny sens, intencję i kontekst oryginalnej wypowiedzi. Nie interpretuj, nie dodawaj własnych założeń ani rozszerzeń znaczenia. Przekształć wypowiedź jedynie na bardziej formalny i klarowny język prawniczy.

        Oto wypowiedź użytkownika:
        {user_prompt}"""
    )
    return system_prompt

def prompt_define_legal_code(user_prompt):
    system_prompt = (
        "Jesteś prawnikiem specjalizującym się w polskich kodeksach prawnych. "
        "Na podstawie pytania użytkownika zdecyduj, który z poniższych kodeksów należy przeszukać. "
        "Zwróć **tylko i wyłącznie** dokładną nazwę jednego z poniższych kodeksów, bez dodatkowych wyjaśnień.\n\n"
        f"Lista kodeksów: {', '.join(code_list)}"
        f"Prompt użytkownika: {user_prompt}"
    )
    return system_prompt