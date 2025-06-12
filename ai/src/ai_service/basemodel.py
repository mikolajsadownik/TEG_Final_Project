from openai import OpenAI
import os


class BaseModel:


    #Abstrakcyjna klasa dla modeli

    def __init__(self, name, model):
        self.name=name
        self.model=model
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.promptMemory=[]

