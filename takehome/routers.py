
from __init__ import app, db
from flask import request
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from schema import Login, Registration, Template
import jwt
from datetime import datetime, timedelta
import uuid 


app.config['SECRET_KEY'] = 'r3fit450gjgt5otrgi5t0rjidjkgtrotrpeai;9ropetiporjerutwo'


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/register', methods=['POST'])
def register(data: Registration):
	_firstName = data.firstName
	_lastName = data.lastName
	_email = data.email
	_password = data.password

	if _firstName  and _lastName and _email and _password \
	and request.method == 'POST':
		#do not save password as a plain text
		_hashed_password = generate_password_hash(_password)
		# save details
		id = db.user.insert({
			'id': uuid.uuid4,
			'first_ame': _firstName, 
			'last_name': _lastName,
			'email': _email, 
			'password': _hashed_password
			})
		resp = jsonify('User added successfully!')
		resp.status_code = 200
		return resp
	else:
		resp = jsonify('Bad Request!')
		resp.status_code = 400
		return resp

@app.route("/login", methods=["POST"])
def login(data: Login):
	user_from_db = db.users.find_one({'email': data.email})  # search for user in database
	if user_from_db:
		if not user_from_db:
        # returns 401 if user does not exist
			return make_response(
				'Could not verify',
				401
				)
		if check_password_hash(user_from_db.password, data.password):
			# generates the JWT Token
			token = jwt.encode({
				'public_id': user_from_db.id,
				'exp' : datetime.utcnow() + timedelta(minutes = 30)
			}, app.config['SECRET_KEY'])
	
			return make_response(jsonify({'token' : token.decode('UTF-8')}), 201)
		# returns 403 if password is wrong
		return make_response(
			'Could not verify',
			403,
			{'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
		)

@app.route('/template', methods=["GET"])
def get_template_all():
	users = db.template.find()
	resp = dumps(users)
	return resp

@app.route("/template", methods=["POST"])
def create_template(data: Template):
	mydb = db["user"]
	mycol = mydb["user"]
	mydict = { 
		"template_name": data.template_name, 
		"subject": data.subject, "body": data.body, 
		"template_id": uuid.uuid4
	}
	x = mycol.insert_one(mydict)
	return x



@app.route('/template/<template_id>', methods=["GET"])
def get_template(template_id):
	user = db.user.find_one({'template_id': ObjectId(template_id)})
	resp = dumps(user)
	return resp
		


@app.route('/template/<template_id>', methods=['PUT'])
def template_update(template_id, data: Template):

	_template_name = data.template_name
	_subject = data.subject
	_body = data.body
	user = db.user.find_one({'template_id': ObjectId(template_id)})		
	# validate the received values
	if user and request.method == 'PUT':
		
		# save edits
		db.user.update_one(
			{'id': ObjectId(template_id['$otemplate_id']) 
			if '$otemplate_id' in template_id else ObjectId(template_id)}, 
			{'$set': {
				'_template_name': _template_name, 
				'_body': _body, '_subject': _subject
				}}
			)
		resp = jsonify('User updated successfully!')
		resp.status_code = 200
		return resp
	else:
		return not_found()
		
@app.route('/delete/<template_id>', methods=['DELETE'])
def delete_template(template_id):
	db.user.delete_one({'id': ObjectId(template_id)})
	resp = jsonify('User deleted successfully!')
	resp.status_code = 204
	return resp
		

