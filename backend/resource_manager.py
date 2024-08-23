from helpers import getRAGPostIndex,AppendIndex,getRetriever,createKnowledgeBase,getRAGModel
from ollama_helper import getLLM

class ResourceManager:
    def __init__(self):
        self.Rag = None
        self.llm = None
        self.ret = None
        self.rag_path = ".ragatouille/colbert/indexes/min-gpt"

    def initialize(self):
        print("Initializing resources...")
        self.Rag = getRAGPostIndex(self.rag_path)
        self.ret = getRetriever(RAGMODEL=self.Rag, index_name="min-gpt")
        self.llm = getLLM()
        print("Initialization complete.")

    def update_Rag_and_ret(self, new_md):
        AppendIndex(RAGMODEL=self.Rag, newMD=new_md)
        self.Rag=getRAGPostIndex(self.rag_path)
        self.ret = getRetriever(RAGMODEL=self.Rag, index_name="min-gpt")

    def get_resources(self):
        return self.Rag, self.llm, self.ret