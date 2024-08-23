from flask import Flask,jsonify,request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from decouple import config
from datetime import timedelta
from routes.authRoutes import auth_blueprint 
from routes.botRoutes import bot_blueprint 
from ollama_helper import generateAnswer,getLLM
from helpers import getRAGPostIndex,getRetriever, pdf2MD,AppendIndex,html2MD
import fitz
from common.chatBot import bot


def initialize():
    print("Initializing resources...")
    Rag=getRAGPostIndex(".ragatouille/colbert/indexes/min-gpt")
    llm=getLLM()
    ret=getRetriever(RAGMODEL=Rag,index_name="min-gpt")
    print("Initialization complete.")
    return (Rag,llm,ret)


def create_app():
    global Rag, llm,ret
    app = Flask(__name__)
    CORS(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_SECRET_KEY'] = config('JWT_SECRET')
    with app.app_context():
        Rag,llm,ret  = initialize()
    app.register_blueprint(auth_blueprint,url_prefix='/api/v1/auth')
    # app.register_blueprint(bot_blueprint,url_prefix='/api')

    chatbot=bot()
    @app.route('/ask', methods=['POST'])
    def ask():
        try:
            if not request.is_json:
                return jsonify({"error": "Request must be in JSON format"}), 400
            data = request.get_json()
            if 'query' not in data:
                return jsonify({"error": "Missing 'prompt' in the request body"}), 400
            if not isinstance(data['query'], str):
                return jsonify({"error": "'prompt' must be a string"}), 400
            query = data['query']
            print("everythings fine")
            with app.app_context():
                print({"ret":ret,"llm":llm,"query":query})
                print("teri")
                response = generateAnswer(retriever=ret,llm=llm,query=query)
                return jsonify({"response": response}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        
    @app.route('/process-pdf',methods=['POST'])
    def process_pdf():
        global Rag,ret
        try:
            pdf_file = request.files['file']
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file part'})
            if pdf_file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'})
            pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
            md = pdf2MD(pdf_document)
            New_Rag=AppendIndex(RAGMODEL=Rag,newMD=md)
            Rag=New_Rag
            ret=getRetriever(Rag,"min-gpt")
            return jsonify({"success":True, 'message':"Pdf processing Successfull" })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
        
    @app.route('/processvideo',methods=['POST'])
    def process_video():
        global Rag,ret
        try:
            data = request.get_json()
            video_url = data.get('video_url')
            transciprt=chatbot.get_video_transcript(video_url=video_url)
            md = chatbot.extract_text(transcript=transciprt)
            new_Rag = AppendIndex(RAGMODEL=Rag,newMD=md)
            Rag=new_Rag
            ret=getRetriever(Rag,"min-gpt")
            return jsonify({"success":True, 'message':"video processed Successfully" })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            
    @app.route('/process-url',methods=['POST'])
    def process_url():
        global Rag,ret
        try:
            data =request.json
            url = data.get('url')
            if not url:
                return jsonify({'error': 'URL is required in the request data'})
            txt=chatbot.scrape_website(url=url)
            print({txt})
            new_md= html2MD(txt)
            print({new_md})
            print("site scraped")
            new_Rag = AppendIndex(RAGMODEL=Rag,newMD=new_md)
            print("Rag updated")
            Rag=new_Rag
            ret=getRetriever(Rag,"min-gpt")
            print("Retriever updated")
            return jsonify({"success":True, 'message':"url processed Successfully" })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return app