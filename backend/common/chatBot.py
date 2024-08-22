import requests
from bs4 import BeautifulSoup
import re
from youtube_transcript_api import YouTubeTranscriptApi
from flask import jsonify
import os
import joblib
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


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
            return transcript
        except Exception as e:
            print(f"Error retrieving transcript: {e}")
            return None

    def extract_text(self, transcript):
        all_text = [item['text'] for item in transcript]
        text = " \n".join(all_text)
        return text

    def text_to_chunk(self, text):
        chunks = [text[i:i+50] for i in range(0, len(text), 50)]
        return '/n'.join(chunks)

    def load_vectorstore(self, id):
        try:
            vector_store = joblib.load(f'vectorstore-{id}.joblib')
            return vector_store
        except Exception as e:
            return None

    def load_vector(self):
        try:
            vector_store = joblib.load(f'vectorstore.joblib')
            print(f"Vector store loaded successfully: {vector_store}")
            return vector_store
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None

    def get_conversation_chain(self, vectorstore):
        if (vectorstore is None):
            print("Vector store is not loaded. Cannot create conversation chain.")
            return None
        try:
            llm = ChatOpenAI()
            memory = ConversationBufferMemory(
                memory_key='chat_history', return_messages=True)
            conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                memory=memory
            )
            return conversation_chain
        except Exception as e:
            return None

    def handle_userinput(self, user_question, conversation, max_history_tokens=2048):
        if conversation is None:
            return ["Error: Conversation chain is not initialized."]
        try:
            response = conversation({'question': user_question})
            chat_history = response['chat_history']
            current_tokens = sum([len(message.content.split()) for message in chat_history])
            while current_tokens > max_history_tokens:
                chat_history.pop(0)  
                current_tokens = sum([len(message.content.split()) for message in chat_history])
            bot_responses = [message.content for i, message in enumerate(chat_history) if i % 2 == 1]
            return bot_responses
        except Exception as e:
            return [f"Error: {e}"]

    def get_pdf_text(self, pdf_docs):
        text = ""
        for pdf in pdf_docs:
            try:
                print(f"Processing '{pdf}'")
                pdf_reader = PdfReader(pdf)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            except Exception as e:
                print(f"Error reading PDF file '{pdf}': {e}")
        return text

    def get_text_chunks(self, text):
        if text is None:
            print("text is none")
            return []
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def create_vectorstore(self, text_chunks, id):
        embeddings = OpenAIEmbeddings()
        vector_store_file = f"vectorstore-{id}.joblib"
        if os.path.exists(vector_store_file):
            vector_store = joblib.load(vector_store_file)
        else:
            vector_store = joblib.load('vectorstore.joblib')
        for i in range(0, len(text_chunks), 10):
            batch = text_chunks[i:i+10]
            batch_vector_store = FAISS.from_texts(texts=batch, embedding=embeddings)
            vector_store.merge_from(batch_vector_store)
        joblib.dump(vector_store, filename=vector_store_file)
        return vector_store