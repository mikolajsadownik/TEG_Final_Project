
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
    Twoje zadanie:


    Użytkownik pyta:
    **{prompt}**

    Lista słów kluczowych do oceny:
        **{batch}**

    odpoiwadające słowa kluczowe

    Zwróć **TYLKO** listę słów kluczowych w formacie JSON, **bez żadnych wyjaśnień, komentarzy, dodatkowych tekstów**.

    Zasady oceny:
    - Oceń rzeczywiste, logiczne i kontekstowe powiązanie z treścią zapytania.
    - Potraktuj zapytanie poważnie i rozważ możliwe przepisy lub instytucje, które mogą mieć związek z opisaną sytuacją – również jeśli jest nietypowe, potoczne lub żartobliwe.
    - Jeśli słowo kluczowe może być powiązane z prawem, regulacjami, przestępstwami lub organami państwowymi w danym kontekście dodaj go do listy.
    - Nie uzasadniaj decyzji. Nie dodawaj nowych słów.

    Zasady:
    - Użyj wyłącznie słów z podanej listy — nie wymyślaj nowych.
    - **Nie dodawaj żadnego tekstu przed ani po liście.**
    - **Nie używaj Markdowna, takiego jak ``` lub ```json.**
    - WYNIK MUSI BYĆ CZYSTYM JSONEM typu `list[str]`.
    - Używaj **TYLKO** podwójnych cudzysłowów: ["hasło"]

    Przykład prawidłowego wyniku:
    ["Agencja Bezpieczeństwa Wewnętrznego", "Afganistan"]

    

    """

    return system_prompt

def evaluate_keywords_against_query(prompt,keywords_json):
    system_prompt=f"""
    Twoje zadanie:s
    Na podstawie zapytania użytkownika i podanej listy słów kluczowych, oceń, które z nich mogą być powiązane z sytuacją opisaną w zapytaniu **z punktu widzenia prawa**.


    Użytkownik pyta:
    \"\"\"{prompt}\"\"\"


    Lista słów kluczowych do oceny:
    \"\"\"{keywords_json}\"\"\"

    
    Zasady oceny:
    - Pytanie może być sformułowane potocznie lub niepoważnie, ale Twoja analiza ma być **poważna, prawna i instytucjonalna**.
    - Oceń, czy dane słowo kluczowe może mieć **jakikolwiek związek z przepisami prawa, regulacjami, instytucjami państwowymi, wykroczeniami, lub przestępstwami** – **nawet pośredni**.
    - Odpowiadaj tylko `true` albo `false` dla każdego słowa.
    - Nie dodawaj nowych słów, nie tłumacz niczego, nie komentuj.
    - Wybierz najważnijesze
    Zwróć odpowiedź jako poprawny JSON:
    [
    {{ "keyword": "example", "pasuje": true }},
    ...
    ]

    """
    return system_prompt


def prompt_cheack(title,prompt):
    system_prompt=f"""
    Twoje zadanie to stwierdzenie czy dany tytuł *{title}* pasuje do {prompt}
    masz zwrócić tylko **True** lub **False**
    """
    return system_prompt
