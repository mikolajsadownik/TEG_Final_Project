import requests
import time
import json

def fetch_acts(limit=100, max_retries=3):
    base_url = 'https://api.sejm.gov.pl/eli/acts/search'
    offset = 0
    all_acts = []
    valid_statuses = ["akt objęty tekstem jednolitym", "akt posiada tekst jednolity", "obowiązujący"]

    while True:
        params = {'limit': limit, 'offset': offset}
        
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    if not items:
                        print("Koniec danych. Pobieranie zakończone.")
                        return all_acts
                    
                    # Filtrowanie tylko aktów o odpowiednim statusie
                    valid_acts = [act for act in items if act.get('status') in valid_statuses]
                    all_acts.extend(valid_acts)
                    print(f"Pobrano {len(valid_acts)} aktów (offset: {offset})")

                    # Zapis do pliku co batch
                    with open('acts_backup.json', 'a', encoding='utf-8') as f:
                        for act in valid_acts:
                            f.write(json.dumps(act, ensure_ascii=False) + '\n')

                    offset += limit
                    time.sleep(0.5)  # Mniejsze obciążenie serwera
                    break
                else:
                    print(f"Błąd {response.status_code}, próba {attempt + 1} z {max_retries}")
                    time.sleep(2)
            except requests.RequestException as e:
                print(f"Wystąpił błąd: {e}, próba {attempt + 1} z {max_retries}")
                time.sleep(2)
        
        # Jeśli wszystkie próby się nie powiodą, zakończ
        if attempt == max_retries - 1:
            print("Nie udało się pobrać danych po wielokrotnych próbach.")
            break

    return all_acts

# Uruchomienie skryptu
acts = fetch_acts()
print(f"Pobrano łącznie {len(acts)} aktów prawnych.")
