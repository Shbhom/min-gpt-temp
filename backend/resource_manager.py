from helpers import getRetriever,combinedMD
from ollama_helper import getOllama
import os
from ragatouille import RAGPretrainedModel


class ResourceManager:
    def __init__(self):
        self.Rag = None
        self.llm = None
        self.retriever = {}
        self.base_path = ".ragatouille/colbert/indexes/"

    def getRag_and_Retriever(self,index_name):
        self.Rag =RAGPretrainedModel.from_index(f"{self.base_path}{index_name}")
        self.retriever[index_name]=getRetriever(self.Rag,index_name=index_name,k=3)
        return self.retriever[index_name]
    
    def getLLM(self):
        return getOllama()
    
    def createIndex(self,index_name:str):
        md=combinedMD()
        self.Rag.index(collection=[md],index_name=index_name,max_document_length=1024,use_faiss=True)
    
    def updateIndex(self,indexName:str,md:str):
        self.Rag.add_to_index(new_collection=[md],index_name=indexName,use_faiss=True)
        
    def get_resources(self):
        return self.Rag, self.llm