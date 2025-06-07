import pandas as pd
import pdfplumber
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
import ai_prompts as aiP
from langchain.text_splitter import RecursiveCharacterTextSplitter

print(os.getcwd())

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

sciezka_pliku = os.path.abspath(__file__)

folder_pliku = os.path.dirname(sciezka_pliku)
actpath=f"{folder_pliku}/data/act_embeded.json"
df = pd.read_json(actpath)
output=f"{folder_pliku}/pobrane_pdf/plik.pdf"

def search_similar_documents(prompt_keywords, eb_model=model, top_k=50,df=df) :
    if isinstance(prompt_keywords, list):
        query_text = " ".join(prompt_keywords)
    else:
        query_text = prompt_keywords

    query_embedding = eb_model.encode([query_text])[0]  
    embeddings_matrix = np.vstack(df["embeded"].values)  

    similarities = cosine_similarity([query_embedding], embeddings_matrix)[0]
    df = df.copy()  
    df["similarity"] = similarities
    return df.sort_values(by="similarity", ascending=False).head(top_k)

def check_title(title,prompt,client=client):
    system_prompt = aiP.prompt_cheack(title,prompt)
                
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}])
    return response.choices[0].message.content

def get_valid_pdf_paths(dataFrame_titles,prompt):
    array=[]
    for i, row in dataFrame_titles.iterrows():
        t=check_title(row["title"],prompt)
        if t=="True":
            path=f"https://isap.sejm.gov.pl/isap.nsf/download.xsp/{row["address"]}/{row["typeFile"]}/{row["fileNames"]}"
            base, ext = os.path.splitext(path)
            if ext.lower() == ".doc":
                path = base + ".pdf"
            array.append(path)
    return array

def download_pdf(url,output=output):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }


    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        with open(output, "wb") as f:
            f.write(r.content)
        return output
    else:
        print("Błąd pobierania", r.status_code)

def extract_text_from_pdf_starting_from_paragraph(pdf_path, start_pattern=r'§\s*1'):
    

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text.strip()


def split_text(text, max_words_=300,chunk_overlap_=75):
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=max_words_,          
    chunk_overlap=chunk_overlap_,         
    separators=[r"\n\n", r"\n", r"Art\. ", r"§ "]      
)
    chunks = splitter.split_text(text)
    return chunks 

def get_text_embeddings(text_chunks, eb_model=model):
    embeddings = eb_model.encode(text_chunks, show_progress_bar=True)
    return embeddings    


def batch_valid_json(prompt,prompt_keywords):
    embeded_chunks=[]
    similaracts=search_similar_documents(prompt_keywords)
    valid_path_pdfs=get_valid_pdf_paths(similaracts,prompt)
    print(valid_path_pdfs)
    print("test")
    for path in valid_path_pdfs:
    
        output_path=download_pdf(path)
        print(output_path)
        print("_________________________")
        pdf_text=extract_text_from_pdf_starting_from_paragraph(output_path)
        chunks=split_text(pdf_text)
        print(chunks)
        embeded_chunk=get_text_embeddings(chunks)
        embeded_chunks.append(embeded_chunk)
prompt="Czy pracodawca może rozwiązać umowę o pracę bez wypowiedzenia z powodu nieusprawiedliwionej nieobecności pracownika?"
toche=['prawo pracy', 'umowa o pracy', 'pracodawca', 'dyscyplina pracy', 'dyscyplinarne postępowanie', 'kodeks pracy']

embeded_chunks=batch_valid_json(prompt,toche)
