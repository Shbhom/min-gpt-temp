from helpers import createKnowledgeBase,getRAGModel

Rag=getRAGModel()
createKnowledgeBase(RAGMODEL=Rag,index_name="min-gpt")