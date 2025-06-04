
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

def prompt_create_key_words_from_querry(batch,prompt):
    system_prompt = f"""
    Jesteś prawnikiem.

    Twoje zadanie:
    Na podstawie zapytania:
    \"{prompt}\"

    Zwróć listę słów kluczowych z PODANEJ LISTY, które najlepiej pasują do zapytania. 
    NIE WOLNO dodawać, modyfikować ani wymyślać własnych słów.

    Zwróć wynik jako poprawną listę JSON, np.:
    ["Agencja Bezpieczeństwa Wewnętrznego", "Afganistan"]

    Wynik może zawierać wyłącznie elementy z tej listy:
    ***{batch}***
    """

    return system_prompt

def evaluate_keywords_against_query(prompt,keywords_json):
    system_prompt=f"""
    Twoje zadanie: oceń, czy każde z poniższych słów kluczowych pasuje do zapytania użytkownika.

    Zapytanie użytkownika:
    \"\"\"{prompt}\"\"\"

    Słowa kluczowe do oceny:
    {keywords_json}

    Dla każdego słowa oceń, czy logicznie i tematycznie pasuje do zapytania użytkownika.
    Zwróć wynik jako listę JSON, np.:
    [
    {{"keyword": "Biuro Ochrony Rządu", "pasuje": true}},
    {{"keyword": "defekacja", "pasuje": false}}
    ]

    Nie zmieniaj słów. Nie dodawaj nowych. Tylko oceniaj.
    """
    return system_prompt
