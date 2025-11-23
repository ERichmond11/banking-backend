from flask import Blueprint, request, jsonify
from models.user import db, User
from flask_jwt_extended import create_access_token

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

# Register route
@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({'error': 'Missing fields'}), 400

    # check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(name=data['name'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# Login route
@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing fields'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'user': user.name}), 200