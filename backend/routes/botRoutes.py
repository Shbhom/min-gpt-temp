from flask import request,jsonify,Blueprint
from common.db import db
import os
from datetime import timedelta, datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
from dotenv import load_dotenv
from common.chatBot import bot
from common.db import db

import re
import argparse
from string import punctuation
import os
import torch
import yaml
import numpy as np
from torch.utils.data import DataLoader
from g2p_en import G2p
from pypinyin import pinyin, Style

from utils.model import get_model, get_vocoder
from utils.tools import to_device, synth_samples
from dataset import TextDataset
from text import text_to_sequence
import nltk




load_dotenv()
bot_blueprint = Blueprint('chatbot', __name__)

chatBot = bot()  
nltk.download('averaged_perceptron_tagger_eng')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def load_model():
    
    global args, all_configs,configs,models
    dir_name=os.path.dirname(os.path.dirname(__file__))
    args=Args({
    "restore_step":900000
    ,"mode":"single"
    ,"text":""
    ,"speaker_id":0
    ,"preprocess_config":os.path.join(dir_name,"config","LJSpeech","preprocess.yaml")
    ,"model_config":os.path.join(dir_name,"config","LJSpeech","model.yaml")
    ,"train_config":os.path.join(dir_name,"config","LJSpeech","train.yaml")
    ,"pitch_control":1.0
    ,"energy_control":1.0
    ,"duration_control":1.0
    ,"source":None
    })
    if args.mode == "single":
        assert args.source is None and args.text is not None

    # Read Config
    all_configs=Args({
    "preprocess_config":yaml.load(
        open(args.preprocess_config, "r"), Loader=yaml.FullLoader
    )
    ,"model_config":yaml.load(open(args.model_config, "r"), Loader=yaml.FullLoader)
    ,"train_config":yaml.load(open(args.train_config, "r"), Loader=yaml.FullLoader)
    })

    configs = (all_configs.preprocess_config, all_configs.model_config, all_configs.train_config)

    # Get model
    model = get_model(args, configs, device, train=False)

    # Load vocoder
    vocoder = get_vocoder(all_configs.model_config, device)
    models=Args({"model":model,"vocoder":vocoder})


def read_lexicon(lex_path):
    lexicon = {}
    with open(lex_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            word = temp[0]
            phones = temp[1:]
            if word.lower() not in lexicon:
                lexicon[word.lower()] = phones
    return lexicon

def preprocess_english(text, preprocess_config):
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    g2p = G2p()
    phones = []
    words = re.split(r"([,;.\-\?\!\s+])", text)
    for w in words:
        if w.lower() in lexicon:
            phones += lexicon[w.lower()]
        else:
            phones += list(filter(lambda p: p != " ", g2p(w)))
    phones = "{" + "}{".join(phones) + "}"
    phones = re.sub(r"\{[^\w\s]?\}", "{sp}", phones)
    phones = phones.replace("}{", " ")

    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)


def synthesize(model, step, configs, vocoder, batchs, control_values):
    preprocess_config, model_config, train_config = configs
    pitch_control, energy_control, duration_control = control_values

    for batch in batchs:
        batch = to_device(batch, device)
        with torch.no_grad():
            # Forward
            output = model(
                *(batch[2:]),
                p_control=pitch_control,
                e_control=energy_control,
                d_control=duration_control
            )
            synth_samples(
                batch,
                output,
                vocoder,
                model_config,
                preprocess_config,
                train_config["path"]["result_path"],
            )


class Args(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        self[key] = value

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
    



load_model()


@bot_blueprint.route('/tts', methods=['POST'])
@jwt_required()
def tts():
    data = request.get_json()
    print(data.keys())
    print(type(data),type(request))
    print()
    args["text"]=data["data"]
    if args.mode == "single":
        ids = raw_texts = [args.text]
        speakers = np.array([args.speaker_id])
        
        if all_configs.preprocess_config["preprocessing"]["text"]["language"] == "en":
            texts = np.array([preprocess_english(args.text, all_configs.preprocess_config)])
        
        text_lens = np.array([len(texts[0])])
        batchs = [(ids, raw_texts, speakers, texts, text_lens, max(text_lens))]

    control_values = args.pitch_control, args.energy_control, args.duration_control

    synthesize(models.model, args.restore_step, configs, models.vocoder, batchs, control_values)

    audio_url=os.path.join(os.path.dirname(os.path.dirname(__file__)),"output","result","LJSpeech","sound.wav")
    print(audio_url)
    return jsonify({"success":True, 'message': data})

    
    
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
