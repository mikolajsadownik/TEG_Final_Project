from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks import LangChainTracer
from langchain.schema import HumanMessage, SystemMessage

import os


class BaseModel:
    def __init__(self, name, model):
        self.name = name
        self.model_name = model
        self.tracer = LangChainTracer()
        self.client = ChatOpenAI(
            model_name=model,
            temperature=0,
            callbacks=[self.tracer],
        )
        self.promptMemory = []


