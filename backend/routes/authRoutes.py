from bson import ObjectId
# from pymongo import ObjectId
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask import request,jsonify,Blueprint
from flask_bcrypt import Bcrypt
from common.db import db
from datetime import datetime,timedelta

auth_blueprint = Blueprint('authentications', __name__)
bcrypt = Bcrypt()

@auth_blueprint.route('/register', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data['email']

        if db.users.find_one({'email': email}):
            return jsonify({"success":False,"message": "Email already exists"}), 200
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        print(hashed_password)

        name = data['name']
        answer = data['answer']

        print("got all details")
        new_user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'answer': answer,
            'role': 0,
            'admin': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        print("going to insert new user")
        if db.users.insert_one(new_user):
          print("inserted successfully")
          return jsonify({"success":True,"message": "User Registered Successfully"}), 200
        else:
          return jsonify({"success":False,"message": "Internal Server Error"}), 200


    except Exception as e:
        return jsonify({"success":False,"message": str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        if not email or not password:
            return jsonify({"success": False, "message": "both email and password required"}), 200

        user = db.users.find_one({"email": email})

        if not user:
            return jsonify({"success": False, "message": "user does not exist, please register"}), 200

        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({"success": False, "message": "invalid credentials"}), 200

        access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(days=7))

        return jsonify({"success": True, "message": "login successful", "token": access_token, "user": {"name": user['name'], "email": user['email']}}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Something Went Wrong {e}"}), 400

@auth_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
  try:
    data = request.get_json()
    email = data.get('email')
    answer = data.get('answer')
    new_password = data.get('newpassword')
    user_id = data.get('id')

    if not email or not answer or not new_password:
      return jsonify({"success": False, "message": "one of the required field is missing"}), 200

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
      return jsonify({"success": False, "message": "invalid credentials"}), 200

    if user['answer'] != answer:
      return jsonify({"success": False, "message": "invalid answer"}), 200

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    update_result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"password": hashed_password}})

    if update_result.matched_count > 0:
      return jsonify({"success": True, "message": "password updated successfully"}), 200
    else:
      return jsonify({"success": False, "message": "error updating the password"}), 200

  except Exception as e:
    return jsonify({"success": False, "message": f"Something Went Wrong{e}"}), 400
  
@auth_blueprint.route('/get-all-users', methods=['GET'])
@jwt_required()
def get_all_users():
  try:
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if (not user) or (user.get('admin', 0) == 0):
      return jsonify({"success": False, "message": "Unauthorized Access"}), 200

    users = list(db.users.find({"admin": 0}))
    for u in users:
      u['_id'] = str(u['_id'])  

    return jsonify({"success": True, "users": users})

  except Exception as e:
    return jsonify({"success": False, "message": "Something Went Wrong", 'e': str(e)}), 400


  
@auth_blueprint.route('/delete-user', methods=['GET'])
@jwt_required()
def delete_user():
  try:
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if (not user) or (user.get('admin', 0) == 0):
      return jsonify({"success": False, "message": "Un Authorized Access"}), 200
    
    id = request.args.get('id')

    if not id:
        return jsonify({"success": False, "message": "Missing user ID"}), 400   
      
    if db.users.delete_one({"_id":ObjectId(id)}):
        return jsonify({"success":True,"message":"user deleted Successfully"}), 200
    else:
        return jsonify({"success":False,"message":"Something Went Wrong"}), 200

  except Exception as e:
    return jsonify({"success": False, "message": "Something Went Wrong"}), 500
  


@auth_blueprint.route('/admin-auth', methods=['GET'])
@jwt_required()
def admin_auth():
  try:
    user_id = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
      return jsonify({"success": False}), 200

    if user['admin'] == 1:
      return jsonify({"success": True}), 200
    else:
       return jsonify({"success":False}),200

  except Exception as e:
    return jsonify({"success": False, "message": "Something Went Wrong"}), 400