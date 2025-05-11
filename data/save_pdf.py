import json
import requests
import os

def get_first_act(filename='acts_backup.json'):
    try:
        # Wczytanie pierwszego rekordu z pliku
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                act = json.loads(line.strip())
                return act
    except FileNotFoundError:
        print(f"Plik {filename} nie został znaleziony.")
        return None
    except json.JSONDecodeError as e:
        print(f"Błąd dekodowania JSON: {e}")
        return None

def download_pdf(act):
    # Pobranie podstawowych informacji o akcie
    publisher = act.get("publisher")
    year = act.get("year")
    pos = act.get("pos")

    # Budowanie URL do pobrania pliku PDF
    pdf_url = f"https://api.sejm.gov.pl/eli/acts/{publisher}/{year}/{pos}/text.pdf"

    # Pobranie pliku PDF
    response = requests.get(pdf_url)

    # Sprawdzenie, czy pobieranie się powiodło
    if response.status_code == 200:
        file_name = f"{publisher}_{year}_{pos}.pdf"
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print(f"Pobrano plik: {file_name}")
    else:
        print(f"Błąd podczas pobierania pliku PDF: {response.status_code}")

# Pobranie pierwszego aktu i pobranie jego PDF
act = get_first_act()
if act:
    download_pdf(act)
else:
    print("Nie znaleziono żadnego aktu.")
