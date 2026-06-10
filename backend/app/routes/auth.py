from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
from app.routes.schema import RegisterSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)
register_schema = RegisterSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    errors = register_schema.validate(request.json)
    if errors:
        return jsonify({"error": errors}), 400

    data = request.json
    
    existing_user = User.query.filter_by(email=data['email']).first()

    if existing_user:
        return jsonify({"error": "Email já cadastrado"}), 409

    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        email=data['email'],
        password_hash=hashed_password,
        role=data['role'],
        selection_id=data.get('selection_id'),
        full_name=data['full_name']
    )
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "selection_id": user.selection_id
    }), 200