import pymupdf4llm
import torch
from ragatouille import RAGPretrainedModel
import os
from markdownify import markdownify

def combinedMD()->str:
    data_directory="Data"
    if not os.path.isdir(data_directory):
        raise FileNotFoundError(f"Error: The directory '{data_directory}' does not exist.")
    
    # Get all files in the directory
    files = os.listdir(data_directory)
    print(f"no of files inserted:{len(files)}")
    
    # List to hold Markdown content
    markdown_contents = []

    # Process each file in the directory
    for file_name in files:
        file_path = os.path.join(data_directory, file_name)
        
        # Check if it's a file (not a subdirectory) and ends with '.pdf'
        if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):
            # Convert PDF to Markdown
            markdown_content = pdf2MD(file_path)
            # Append the result to the list
            markdown_contents.append(markdown_content)

    # Concatenate all Markdown contents into a single string
    concatenated_md = "\n\n".join(markdown_contents)
    
    return concatenated_md

def getRAGPostIndex(path:str)->RAGPretrainedModel:
    return RAGPretrainedModel.from_index(path)


def pdf2MD(path:str)->str:
    return pymupdf4llm.to_markdown(path)


def getRAGModel():
    return RAGPretrainedModel.from_pretrained("jinaai/jina-colbert-v1-en")

def createIndex(RAGMODEL,markdown:str,name:str,batch_size=16,chunk_size=1024):
    RAGMODEL.index(collection=[markdown],
          index_name=name,
          max_document_length=chunk_size,
          split_documents=True,
          bsize = batch_size,
          use_faiss=True,
          )

def AppendIndex(RAGMODEL,newMD:str,batch_size=16)->RAGPretrainedModel:
    RAGMODEL.add_to_index(new_collection=[newMD],
      index_name="min-gpt",
      split_documents=True,
      bsize = batch_size,
      use_faiss=True
      )
    
def getContext(RAGMODEL:RAGPretrainedModel,index_name:str,query:str,k=2):
    return RAGMODEL.search(query=query,index_name=index_name,k=k)
    
def getRetriever(RAGMODEL:RAGPretrainedModel,index_name:str,k=2):
    return RAGMODEL.as_langchain_retriever(index_name=index_name,k=k)

def html2MD(html:str):
    return markdownify(html=html)

def createKnowledgeBase(RAGMODEL,index_name:str):
   combined_mds= combinedMD()
   createIndex(RAGMODEL=RAGMODEL,markdown=combined_mds,name=index_name)