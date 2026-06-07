from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
from app.schemas import RegisterSchema

auth_bp = Blueprint('auth', __name__)
register_schema = RegisterSchema()

@auth_bp.route('/register', methods=['POST'])

def register():
    errors = register_schema.validate(request.json)
    if errors == True:
        return jsonify({"error": errors}), 400

    data = request.json
    
    existing_user = User.query.filter_by(email=data['email']).first()

    if existing_user == True:
        return jsonify({"error": "Email já cadastrado"}), 409

    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        email=data['email'],
        password=hashed_password,
        role=data['role'],
        selection_id=data.get('selection_id')
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }), 201