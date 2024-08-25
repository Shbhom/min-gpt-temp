from flask import request,jsonify,Blueprint
from common.db import db
from datetime import timedelta, datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from dotenv import load_dotenv
from common.chatBot import bot
from common.db import db
import fitz
from resource_manager import ResourceManager


load_dotenv()
bot_blueprint = Blueprint('chatbot', __name__)

chatBot = bot()  
RM= ResourceManager()

@bot_blueprint.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    try:
        id = get_jwt_identity()
        
        if not request.is_json:
            return jsonify({"error": "Request must be in JSON format"}), 400
        data = request.get_json()
        if 'query' not in data:
            return jsonify({"error": "Missing 'prompt' in the request body"}), 400
        if not isinstance(data['query'], str):
            return jsonify({"error": "'prompt' must be a string"}), 400

        data = request.get_json()
        user_question = data.get('query')
        
        response_count = db.usage.count_documents({
            'user_id': id,
            'type': 'response_count',
            'created_at': {'$gte': datetime.now() - timedelta(minutes=10)}
        })
        if response_count > 5:
            return jsonify({"success":False,"message":"Response Limit Reached"})
        
        llm = RM.getLLM() 
        ret=RM.getRag_and_Retriever(index_name=f"{id}_index")
        
        conversation = chatBot.get_conversation_chain(retriever=ret,llm=llm)
        chat_history = chatBot.getMessageHistory(str(id))
        
        if db.usage.insert_one({"user_id":id, "type":"response", 'created_at': datetime.now()}):
            bot_responses = chatBot.handle_userinput(user_question=user_question,conversation=conversation,chat_history=chat_history,retriever=ret)
            chatBot.updateMessageHistory(str(id),query=user_question,response=bot_responses)
            return jsonify({"success":True, 'response': bot_responses})
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"}),500

    except Exception as e:
        return jsonify({'error': str(e)}),500

    
@bot_blueprint.route('/processpdf', methods=['POST'])
@jwt_required()
def process_pdf():
    try:
        id = get_jwt_identity()

        response_count = db.usage.count_documents({
            'user_id': id,
            'type': 'pdf',
            'created_at': {'$gte': datetime.now() - timedelta(hours=1)}
        })
        if response_count > 3:
            return jsonify({"success":False,"message":"Response Limit Reached"})
        
        pdf_file = request.files['file']

        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        if pdf_file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        md = chatBot.pdf2MD(pdf_document)
        if db.usage.insert_one({"user_id":id, "type":"pdf", 'created_at': datetime.now()}):
            RM.updateIndex(indexName=f"{id}",md=md)
            return jsonify({"success":True, 'message':"Pdf processing Successfull" })
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@bot_blueprint.route('/processvideo', methods=['POST'])
@jwt_required()
def process_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        id = get_jwt_identity()

        response_count = db.usage.count_documents({
            'user_id': id,
            'type': 'video',
            'created_at': {'$gte': datetime.now() - timedelta(hours=1)}
        })
        if response_count > 3:
            return jsonify({"success":False,"message":"Response Limit Reached"})
        transcript  = chatBot.get_video_transcript(video_url)
        if db.usage.insert_one({"user_id":id, "type":"video", 'created_at': datetime.now()}):
            RM.updateIndex(indexName=f"{id}",md=transcript)
            return jsonify({"success":True, 'message':"Video processing Successfull" })
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"})
        
    except Exception as e:
        return jsonify({'success': "false","message":"Something Went Wrong", "e":str(e)})

@bot_blueprint.route('/process-url', methods=['POST'])
@jwt_required()
def process_url():
    try:
        data = request.json
        url = data.get('url')
        id = get_jwt_identity()

        response_count = db.usage.count_documents({
            'user_id': id,
            'type': 'website',
            'created_at': {'$gte': datetime.now() - timedelta(hours=1)}
        })
        if response_count > 3:
            return jsonify({"success":False,"message":"Response Limit Reached"})

        if not url:
            return jsonify({'error': 'URL is required in the request data'})

        txt = chatBot.scrape_website(url)
        new_md = chatBot.html2MD(txt)
        if db.usage.insert_one({"user_id":id, "type":"website", 'created_at': datetime.now()}):
            RM.updateIndex(indexName=f"{id}",md=new_md)
            return jsonify({"success":True, 'message':"Video processing Successfull" })
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"})

    except Exception as e:
        return jsonify({'success': "false"})