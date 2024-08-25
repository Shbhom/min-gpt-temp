import torch._dynamo.config
from flask import request,jsonify,Blueprint, send_file
from common.db import db
import os
import re
import numpy as np
from datetime import timedelta, datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from dotenv import load_dotenv
from common.chatBot import bot
from common.db import db
import io
from pydub import AudioSegment
import json


import torch
from scipy.io.wavfile import write
from ChatTTS import ChatTTS


 
torch._dynamo.config.cache_size_limit = 64
torch._dynamo.config.suppress_errors = True
torch.set_float32_matmul_precision("high")

load_dotenv()
bot_blueprint = Blueprint('chatbot', __name__)

chatBot = bot()  


@bot_blueprint.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    try:
        data = request.get_json()
        user_question = data.get('question')
        id = get_jwt_identity()

        response_count = db.usage.count_documents({
            'user_id': id,
            'type': 'response_count',
            'created_at': {'$gte': datetime.now() - timedelta(minutes=10)}
        })

        if response_count > 5:
            return jsonify({"success":False,"message":"Response Limit Reached"})

        if not os.path.exists(f"vectorstore-{id}.joblib"):
            chunks = chatBot.get_text_chunks('''
                My name is MineGPT, and I stand ready as a versatile and adept assistant in various tasks and contexts. Leveraging my robust language processing capabilities, I excel at comprehending and interpreting textual inputs with precision and accuracy. Whether it involves answering user queries, generating informative responses, or facilitating complex computations, I reliably deliver results tailored to specific requirements. Positioned as a vital component within the application framework, I play a pivotal role in streamlining processes and enhancing user experiences. My adaptability and intelligence make me an invaluable asset, empowering applications to handle diverse challenges with efficiency and effectiveness.''')
            chatBot.create_vectorstore(chunks,id)

        vectorstore = chatBot.load_vectorstore(id)
        conversation = chatBot.get_conversation_chain(vectorstore)

        print(user_question)

        if db.usage.insert_one({"user_id":id, "type":"response", 'created_at': datetime.now()}):
            bot_responses = chatBot.handle_userinput(user_question, conversation)
            return jsonify({"success":True, 'response': bot_responses})
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"})

    except Exception as e:
        return jsonify({'error': str(e)})

    
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

        all_text = chatBot.get_pdf_text([pdf_file])
        batches = chatBot.get_text_chunks(all_text)

        if db.usage.insert_one({"user_id":id, "type":"pdf", 'created_at': datetime.now()}):
            chatBot.create_vectorstore(batches,id)
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

        transscript  = chatBot.get_video_transcript(video_url)
        all_text = chatBot.extract_text(transscript)
        batches = chatBot.get_text_chunks(all_text)

        if db.usage.insert_one({"user_id":id, "type":"video", 'created_at': datetime.now()}):
            chatBot.create_vectorstore(batches,id)
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

        text = chatBot.scrape_website(url)
        batches = chatBot.get_text_chunks(text)

        if db.usage.insert_one({"user_id":id, "type":"website", 'created_at': datetime.now()}):
            chatBot.create_vectorstore(batches,id)
            return jsonify({"success":True, 'message':"Video processing Successfull" })
        else:
            return jsonify({"success":True, 'message': "Something Went Wrong"})

    except Exception as e:
        return jsonify({'success': "false"})
    
    
chat = ChatTTS.Chat()
chat.load(compile = False)

def replace_non_alphabet_with_spaces(text):
    return re.sub(r'[^A-Za-z]', ' ', text)

@bot_blueprint.route('/tts', methods=['POST'])
@jwt_required()
def tts():
    try:
        data = request.get_json()
        
        # speaker = chat.sample_random_speaker()
        with open("speaker.json","r") as file:
            speaker_dict=json.load(file)
            speaker=speaker_dict["speaker"]
        params_infer=chat.InferCodeParams()
        params_infer.spk_emb = speaker
        text = data.get("data")
        # print(type(text))
        text=replace_non_alphabet_with_spaces(text)
        text = text.split("\n")
        text=" ".join(text)
        text=text.split()
        texts = [] 
        for i in range(0,len(text),200):
            texts.append(" ".join(text[i:i+200]))
        
        final_np_array=[]
        for text in texts:
            waves = chat.infer([text], lang="en",params_infer_code=params_infer)
            final_np_array.append(waves[0].copy())
        nextWave = np.concatenate(final_np_array)
        wav_io = io.BytesIO()
        write(wav_io, 24000, nextWave)
        wav_io.seek(0)
        
        
        return send_file(wav_io, mimetype="audio/mp3", as_attachment=True, download_name="output.mp3")
    except Exception as e:
        print(e)
        return jsonify({"success": "false", "message": "Something Went Wrong"})