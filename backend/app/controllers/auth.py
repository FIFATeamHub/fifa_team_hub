from flask import request, jsonify, Blueprint

import re
from app.routes.schema import RegisterSchema, LoginSchema
from app.config.database import db
from app.models.user import User
from app.models.enums.user_role import UserRole
from app.services.auth import hash_senha, verificar_senha, gerar_token
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    dados = request.get_json()
    
    register_schema = RegisterSchema()
    erros = register_schema.validate(dados)

    # Valida campos obrigatórios
    campos = ["email", "password", "full_name", "role"]
    for campo in campos:
        if not dados.get(campo):
            return jsonify({"error": f"Campo '{campo}' é obrigatório"}), 400
        
    # Cole isto no seu register() logo após validar os campos obrigatórios:
    email = dados.get("email")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return jsonify({"error": "Formato de e-mail inválido. Verifique se digitou o '.com'."}), 400

    # Valida se role é um valor válido do enum
    try:
        role = UserRole(dados["role"])
    except ValueError:
        roles_validos = [r.value for r in UserRole]
        return jsonify({"error": f"Role inválido. Use: {roles_validos}"}), 400

    # Verifica se email já existe
    if User.query.filter_by(email=dados["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    # Cria o usuário com senha hasheada
    novo_user = User(
        email=dados["email"],
        password_hash=hash_senha(dados["password"]),
        full_name=dados["full_name"],
        role=role,
        selection_id=dados.get("selection_id")
    )

    db.session.add(novo_user)
    db.session.commit()

    return jsonify({
        "id": str(novo_user.id),
        "email": novo_user.email,
        "full_name": novo_user.full_name,
        "role": novo_user.role.value,
        "selection_id": str(novo_user.selection_id) if novo_user.selection_id else None
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    schema = LoginSchema()
    erros = schema.validate(dados)
    if erros:
        return jsonify({"error": erros}), 400

    email = dados.get("email")
    password = dados.get("password")

    if not email or not password:
        return jsonify({"error": "Email e password são obrigatórios"}), 400

    try:
        # Busca user por email
        user = User.query.filter_by(email=email.lower()).first()
        # Credenciais inválidas
        if not user or not verificar_senha(password, user.password_hash):
            return jsonify({"error": "Credenciais inválidas"}), 401
        token = gerar_token(user)
        return jsonify({
            "access_token": token,
            "token_type": "bearer"
        }), 200
    except Exception as e:
        # Se QUALQUER coisa der errado (banco cair, erro de digitação no código), 
        # a gente captura aqui para não dar erro 500 seco no navegador.
        print(f"Erro no login: {e}") # Isso vai pro terminal
        return jsonify({"error": "Erro interno no servidor"}), 500

@auth_bp.route("/me", methods=["GET"])
def me(current_user):
    # Retorna dados do usuário autenticado (injetado pelo middleware)
    return jsonify({
    "id": str(current_user.id),
    "email": current_user.email,
    "full_name": current_user.full_name,
    "role": current_user.role.value,
    "selection_id": str(current_user.selection_id) if current_user.selection_id else None
}), 200

