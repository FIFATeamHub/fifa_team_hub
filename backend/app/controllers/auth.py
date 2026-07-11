from flask import request, jsonify, Blueprint

import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from app.routes.schema import RegisterSchema, LoginSchema
from app.extensions import db
from app.models.user import User
from app.models.enums.user_role import UserRole, LogAction
from app.services.audit import register_audit_log

from app.services.auth import hash_password, verify_password, create_access_token

auth_bp = Blueprint("auth", __name__)

UUID_LOGIN_SEM_USUARIO = uuid.uuid4()


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

    raw_selection_id = dados.get("selection_id")
    selection_id = None
    if raw_selection_id and str(raw_selection_id).strip() not in ("", "null", "undefined", "None"):
        selection_id = raw_selection_id

    # Cria o usuário com senha hasheada
    novo_user = User(
        email=dados["email"],
        password_hash=hash_password(dados["password"]),
        full_name=dados["full_name"],
        role=role,
        selection_id=selection_id
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

def login():
    fuso_sp = ZoneInfo("America/Sao_Paulo")
    momento_requisicao = datetime.now(fuso_sp)

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
        if not user or not verify_password(password, user.password_hash):
            if user:
                register_audit_log(
                    user.id, LogAction.LOGIN, "FAILURE", user.id,
                    momento_requisicao, "Senha incorreta", selection_id_e=user.selection_id
                )
            else:
                register_audit_log(
                    None, LogAction.LOGIN, "FAILURE", UUID_LOGIN_SEM_USUARIO,
                    momento_requisicao, "Tentativa de login com e-mail não cadastrado"
                )
            return jsonify({"error": "Credenciais inválidas"}), 401

        token = create_access_token(user)

        register_audit_log(
            user.id, LogAction.LOGIN, "SUCCESS", user.id,
            momento_requisicao, "Login realizado com sucesso", selection_id_e=user.selection_id
        )

        return jsonify({
            "access_token": token,
            "token_type": "bearer"
        }), 200
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500


def logout(current_user):
    fuso_sp = ZoneInfo("America/Sao_Paulo")
    momento_requisicao = datetime.now(fuso_sp)

    register_audit_log(
        current_user.id, LogAction.LOGOUT, "SUCCESS", current_user.id,
        momento_requisicao, "Logout realizado com sucesso", selection_id_e=current_user.selection_id
    )

    return jsonify({"message": "Logout realizado com sucesso"}), 200


def me(current_user):
    if current_user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "selection_id": str(current_user.selection_id) if current_user.selection_id else None,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }), 200
