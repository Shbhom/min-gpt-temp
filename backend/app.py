from flask import Flask
# from flask import jsonify,request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from decouple import config
from datetime import timedelta
from routes.authRoutes import auth_blueprint 
from routes.botRoutes import bot_blueprint 
# from ollama_helper import getLLM
# from helpers import getRAGPostIndex,getRetriever
import os
from common.chatBot import bot
from resource_manager import ResourceManager
from helpers import createKnowledgeBase,getRAGModel

# Rag=None
# llm=None
# ret=None


# def initialize():
#     print("Initializing resources...")
#     Rag=getRAGPostIndex(".ragatouille/colbert/indexes/min-gpt")
#     llm=getLLM()
#     ret=getRetriever(RAGMODEL=Rag,index_name="min-gpt")
#     print("Initialization complete.")
#     return (Rag,llm,ret)

def checkAndInitializeKnowledgeBase():
    index_path = ".ragatouille/colbert/indexes/min-gpt"
    
    if not os.path.exists(index_path):
        print(f"Directory {index_path} does not exist.")
        print("Creating Knowledge Base...")
        Rag= getRAGModel()
        createKnowledgeBase(Rag,"min-gpt")
    else:
        print(f"Directory {index_path} exists.")


app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['JWT_SECRET_KEY'] = config('JWT_SECRET')
app.register_blueprint(auth_blueprint,url_prefix='/api/v1/auth')
app.register_blueprint(bot_blueprint,url_prefix='/api')

if __name__ == '__main__':
    checkAndInitializeKnowledgeBase()
    app.run(host='0.0.0.0', port=5000, debug=True)