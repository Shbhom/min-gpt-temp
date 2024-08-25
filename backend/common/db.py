from pymongo import MongoClient
from decouple import config

uri = config('MONGO_URI')
client = MongoClient(uri)
db = client['test']
