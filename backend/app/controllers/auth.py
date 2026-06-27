from flask import request, jsonify, Blueprint, g

from app.config.database import db
from app.models.user import User
from app.models.enums.user_role import UserRole
from app.services.auth import hash_senha, verificar_senha, gerar_token
from app.routes.schema import RegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    dados = request.get_json()
    
    register_schema = RegisterSchema()
    erros = register_schema.validate(dados)

    if erros:
        return jsonify({"error": erros}), 400

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


def me():
    # busca o usuario no banco usando o ID guardado pelo require_auth no flask.g
    user = User.query.get(g.current_user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "selection_id": str(user.selection_id) if user.selection_id else None,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 200
