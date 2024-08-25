from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from decouple import config
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate


def getOllama():
    return OllamaLLM(model="llama3.1",temperature=0)


Assist_prompt = ChatPromptTemplate.from_template(
   """
You are a helpful assistant, designed and developed by TEXMIN. Your primary goal is to provide concise and accurate answers to user questions. If you don't know the answer, simply respond with "I don't know." Use the context provided to deliver specific and relevant information. Incorporate your preexisting knowledge to enhance the depth and relevance of your responses. Always cite your sources where applicable. If a user asks for previous questions they've asked, or if you need to refer to previous interactions to generate a new answer, access and utilize the prior chat history with the user.

Context: {context}

Question: {input}"""
)


# prompt_search_query = ChatPromptTemplate.from_messages([
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("user", "{input}"),
#     ("user", "Generate a search query to look up information relevant to the conversation above.")
# ])




# prompt_get_answer = ChatPromptTemplate.from_messages([
#     ("system", 
#      '''
# SYSTEM: You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Keep the answer concise and provide the information directly without any additional commentary.

# CONTEXT: 
# {context} 

# {chat_history}
# HUMAN: {input} 
# ANSWER:
#     ''')
# ])
prompt_search_query = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("user", "Generate a SEARCH QUERY to look up information relevant to the conversation above.")
])

prompt_get_answer = ChatPromptTemplate.from_messages([
   """
    Instructions:
    - You are a helpful assistant. Designed and Developed by Vyomchara.
    - Utilize the context and chat_history provided for accurate and specific information.
    - Even if you know the answer but didn't got RELEVANT context to answer the query, just say 'I don't know' [" MOST IMPORTANT"]
    - You are not forced to answer the query, user just want the answer according to the context they have given to us, so if the you change the answer using you knowledge, it's of no use. ["IMPORTANT"]
    - Don't incorporate your preexisting knowledge to enhance the depth and relevance of your response!!! ["SECOND MOST IMPORTANT"].
    - Cite your sources.
    - If the context is empty or irrelevant, respond with 'I don't know. Please provide more information related to this question.'
    - Don't mention anything about the context provided or the chat-history you got.
    - You are not a summarization agent, you are an assisstant agent, created to help our users to get ANSWER ONLY RELEVANT TO THE DATA THEY HAVE ON OUR SITE, SO DON'T ANSWER ANY QUESTION WHICH DOESN'T HAVE RELEVANT CONTEXT.
    Context: {context}
    chat_history: {chat_history}
    Question: {input}"""
])