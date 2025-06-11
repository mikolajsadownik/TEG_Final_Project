# TEG Final Project

Projekt pokazuje kompletny, kontenerowy pipeline do przetwarzania i odpytywania korpusu aktów prawnych z wykorzystaniem wektorowej bazy Pinecone i modelu GPT‑4. Całość składa się z trzech lekkich mikroserwisów (AI → Backend → Frontend) spinanych przez Docker Compose.

## Kluczowe funkcje

* Pobieranie aktów prawnych z publicznego API Sejmu i zapisywanie surowych PDF‑ów
* Ekstrakcja tekstu, dzielenie na fragmenty i generowanie embeddingów (Sentence‑Transformers)
* Składowanie embeddingów w indeksie Pinecone
* Retrieval → GPT‑4 → odpowiedź tworzona wyłącznie w oparciu o znaleziony kontekst
* Prosty interfejs webowy (Streamlit) gotowy do dalszej rozbudowy

## Struktura katalogów (skrót)

* ai – logika NLP, indeksowanie i odpytywanie Pinecone
* backend – szkielet usług biznesowych (REST lub GraphQL)
* frontend – interfejs Streamlit
* data – skrypty do pobierania danych i pliki pomocnicze
* docs, logs, tests – miejsca na dokumentację, logi i testy

## Wymagania wstępne

* Docker >= 20.10
* Docker Compose >= v2
* Klucze API do: OpenAI, Pinecone (umieszczone w pliku .env na poziomie root)

## Szybki start

1. Sklonuj repozytorium.
2. Dodaj plik .env i uzupełnij wymagane zmienne środowiskowe (przykładowe nazwy w plikach config\_manager.py).
3. Z katalogu głównego wykonaj polecenie
   docker‑compose up --build
4. Po zbudowaniu:

   * Frontend: [http://localhost:8501](http://localhost:8501)
   * Pozostałe serwisy komunikują się wewnętrznie w sieci Compose

## Typowy przepływ danych

1. data/api\_json\_creator.py pobiera metadane aktów i zapisuje w acts\_backup.json
2. data/save\_pdf.py ściąga PDF wybranego aktu
3. ai/src/services/pinecone\_service.py parsuje PDF‑y, tworzy embeddingi i wrzuca je do Pinecone
4. ai/src/services/query\_pinecone\_with\_gpt.py odbiera zapytanie użytkownika, pobiera najbardziej pasujące fragmenty i wysyła do GPT‑4, zwracając odpowiedź

## Konfiguracja

Najważniejsze zmienne środowiskowe:

* OPENAI\_API\_KEY
* PINECONE\_API\_KEY
* PINECONE\_ENVIRONMENT
* PINECONE\_INDEX\_NAME
* AI\_MODEL (domyślnie gpt‑4o)


## Licencja

Projekt objęty jest licencją określoną w pliku LICENSE.
