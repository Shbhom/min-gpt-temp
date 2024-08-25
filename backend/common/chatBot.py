import requests
from bs4 import BeautifulSoup
import re
from youtube_transcript_api import YouTubeTranscriptApi
from flask import jsonify
from dotenv import load_dotenv
from langchain.memory import MongoDBChatMessageHistory
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from ollama_helper import prompt_get_answer,prompt_search_query
from decouple import config
import pymupdf4llm
from markdownify import markdownify
from langchain_core.retrievers import BaseRetriever

load_dotenv()

class bot:
    def __init__(self,):
        pass

    def scrape_website(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status() 
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()
            text_content_normalized = re.sub(r'\s+', ' \n', text_content)
            return text_content_normalized
        except requests.RequestException as e:
            return jsonify({'error': str(e)})

    def get_video_transcript(self, video_url):
        try:
            if "v=" in video_url:
                video_id = video_url.split("v=")[1]
            else:
                match = re.search(r'/([^/?]+)\?', video_url)
                video_id = match.group(1)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            all_text = [item['text'] for item in transcript]
            text = " \n".join(all_text)
            return text
        except Exception as e:
            print(f"Error retrieving transcript: {e}")
            return None
        
    def get_conversation_chain(self, retriever:BaseRetriever,llm):
        if (retriever is None):
            print("Vector store is not loaded. Cannot create conversation chain.")
            return None
        try:
            retriever_chain = create_history_aware_retriever(llm,retriever,prompt_search_query)
            document_chain = create_stuff_documents_chain(llm,prompt_get_answer)
            retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)
            return document_chain
        except Exception as e:
            return None

    def handle_userinput(self, user_question, conversation,chat_history):
        if conversation is None:
            return ["Error: Conversation chain is not initialized."]
        try:
            response = conversation.invoke({"chat_history":chat_history,"input":user_question})
            print({"response":response})
            return response
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [f"Error: {e}"]
    
    def pdf2MD(self,path:str):
        return pymupdf4llm.to_markdown(path)
    
    def html2MD(self,html:str):
        return markdownify(html=html)

    def getMessageHistory(self,id:str):
        uri = config("MONGO_URI")
        message_history= MongoDBChatMessageHistory(connection_string=uri,session_id=id,database_name="minGPT",collection_name="chat_history")
        return message_history.messages[-10:]
    
    def updateMessageHistory(self,id:str,query:str,response:str):
        uri = config("MONGO_URI")
        message_history= MongoDBChatMessageHistory(connection_string=uri,session_id=id,database_name="minGPT",collection_name="chat_history")
        message_history.add_user_message(query)
        message_history.add_ai_message(response)