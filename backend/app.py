from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from decouple import config
from datetime import timedelta
from routes.authRoutes import auth_blueprint 
from routes.botRoutes import bot_blueprint 

app = Flask(__name__)

CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

app.config['JWT_SECRET_KEY'] = config('JWT_SECRET')

app.register_blueprint(auth_blueprint,url_prefix='/api/v1/auth')
app.register_blueprint(bot_blueprint,url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)