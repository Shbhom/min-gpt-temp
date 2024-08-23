from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.retrievers import BaseRetriever


def getLLM():
    return OllamaLLM(model="llama3.1",temperature=0)


Assist_prompt = ChatPromptTemplate.from_template(
   """
Instructions:
- You Are a helpful assistant. Designed and Developed by TEXMIN.
- Be helpful and answer questions concisely. If you don't know the answer, say 'I don't know'
- Utilize the context provided for accurate and specific information.
- Incorporate your preexisting knowledge to enhance the depth and relevance of your response.
- Cite your sources
Context: {context}

Question: {input}"""
)

def generateAnswer(retriever:BaseRetriever,llm:OllamaLLM,query:str,prompt=Assist_prompt)->str:
    print("fine4")
    print({"llm":llm,"prompt":prompt})
    doc_chain= create_stuff_documents_chain(llm,prompt)
    print("fine5")
    print(doc_chain.get_prompts)
    ret_chain = create_retrieval_chain(retriever,doc_chain)
    print("fine6")
    response= ret_chain.invoke({"input":query})
    return response['answer']

    