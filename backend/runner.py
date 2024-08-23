from helpers import getRAGModel,getRAGPostIndex,getRetriever,createKnowledgeBase
from ollama_helper import generateAnswer, getLLM


# Rag = getRAGModel()
# print("got Rag Model from ratatouille")

# Rag=createKnowledgeBase(RAGMODEL=Rag,index_name="min-gpt")
# print("knowledgeBase created")
Rag=getRAGPostIndex("/home/shbhom/Ls-texmin-main/backend/.ragatouille/colbert/indexes/min-gpt")

# print(getContext(RAGMODEL=Rag,index_name="min-gpt",query="what are the actions when 20000 cubic meter material is minned per month ?"))
# print("answer generated")
ret = getRetriever(RAGMODEL=Rag,index_name="min-gpt")

llm = getLLM()

Question = 'what happens if material mined exceeds 20000 cubic meter per months?'

print(generateAnswer(retriever=ret,llm=llm,query=Question))