from __init__ import app, db
from flask import request
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from schema import Login, Registration, Template,UpdateTemplate
import jwt
from datetime import datetime, timedelta
from flask_pydantic import validate
from auth import token_required
import json
from config import SECRET_KEY


@app.errorhandler(404)
def not_found(error=None, message = ""):
    message = {
        'status': 404,
        'detail': 'Not Found: ' + request.url,
		"message": message
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/register', methods=['POST'])
@validate()
def register(body: Registration):
	_firstName = body.firstName
	_lastName = body.lastName
	_email = body.email
	_password = body.password

	if _firstName  and _lastName and _email and _password \
	and request.method == 'POST':
		#do not save password as a plain text
		_hashed_password = generate_password_hash(_password)
		# save details
		id = db.user.insert_one({
			'first_name': _firstName, 
			'last_name': _lastName,
			'email': _email, 
			'password': _hashed_password
			})
		resp = jsonify({"message":'User added successfully!'})
		resp.status_code = 200
		return resp
	else:
		resp = jsonify({"message":'Bad Request!'})
		resp.status_code = 400
		return resp

@app.route("/login", methods=["POST"])
@validate()
def login(body: Login):
	user_from_db = db.user.find_one({'email': body.email})  # search for user in database
	if user_from_db:
		if check_password_hash(user_from_db["password"], body.password):
			# generates the JWT Token
			token = jwt.encode({
				'public_id': str(user_from_db["_id"]),
				'exp' : datetime.utcnow() + timedelta(minutes = 30)
			}, SECRET_KEY, algorithm="HS256")
	
			res = jsonify({'token' : token})
			res.status_code=(200)
			return res
		# returns 403 if password is wrong
		res = jsonify({"message": "wrong password"})
		res.status_code = (401)
		return res
	else:
		res = jsonify({"message": "Could not find user"})
		res.status_code = 404
		return res

	

@app.route('/template', methods=["GET"])
@token_required
def get_template_all(current_user):
	templates = db.templates.find()
	resp = dumps(templates)
	return json.loads(resp)

@app.route("/template", methods=["POST"])
@validate()
@token_required
def create_template(current_user, body: Template):
	print(current_user)
	mydict = { 
		"template_name": body.template_name, 
		"subject": body.subject, 
		"body": body.body, 

	}
	x = db.templates.insert_one(mydict)
	res = jsonify({"message": "Template created"})
	res.status_code = 201
	return res



@app.route('/template/<template_id>', methods=["GET"])
@token_required
def get_template(current_user, template_id):
	user = db.templates.find_one({'_id': ObjectId(template_id)})
	resp = dumps(user)
	return json.loads(resp)
		

def remove_none(dicti: dict):
	dict_copy = dicti.copy()
	for i in dict_copy:
		if dict_copy[i] == None:
			del dicti[i]
	return dicti

@app.route('/template/<template_id>', methods=['PUT'])
@validate()
@token_required
def template_update(current_user, template_id, body: UpdateTemplate):
	body_dict = remove_none(body.dict())
	template = db.templates.find_one({'_id': ObjectId(template_id)})		
	# validate the received values
	if template and request.method == 'PUT':
		# save edits
		db.templates.find_one_and_update({"_id": ObjectId(template_id)}, {"$set":body_dict}
			)
		resp = jsonify({"message":'Template Updated successfully!'})
		resp.status_code = 200
		return resp
	else:
		return not_found()
		
@app.route('/template/<template_id>', methods=['DELETE'])
@token_required
def delete_template(current_user, template_id):
	template = db.templates.find_one({'_id': ObjectId(template_id)})
	if not template:
		return not_found(message="Template not found")
	db.templates.find_one_and_delete({'_id': ObjectId(template_id)})
	resp = jsonify({"message":'Template deleted successfully!'})
	resp.status_code = 200
	return resp
		