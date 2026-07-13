from flask import request, jsonify, Blueprint

import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from app.routes.schema import RegisterSchema, LoginSchema
from app.extensions import db
from app.models.user import User
from app.models.enums.user_role import UserRole, LogAction, RegistrationStatus
from app.services.audit import register_audit_log

from app.services.auth import hash_password, verify_password, create_access_token

auth_bp = Blueprint("auth", __name__)

UUID_LOGIN_SEM_USUARIO = uuid.uuid4()


def register():
    dados = request.get_json()

    register_schema = RegisterSchema()
    erros = register_schema.validate(dados)
    if erros:
        return jsonify({"error": erros}), 400

    campos = ["email", "password", "full_name", "selection_id"]
    for campo in campos:
        if not dados.get(campo):
            return jsonify({"error": f"Campo '{campo}' é obrigatório"}), 400

    email = dados.get("email")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return jsonify({"error": "Formato de e-mail inválido. Verifique se digitou o '.com'."}), 400

    if User.query.filter_by(email=dados["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    novo_user = User(
        email=dados["email"],
        password_hash=hash_password(dados["password"]),
        full_name=dados["full_name"],
        role=UserRole.ATHELETE,
        registration_status=RegistrationStatus.PENDING,
        selection_id=uuid.UUID(dados["selection_id"])
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
        user = User.query.filter_by(email=email.lower()).first()
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

        if user.registration_status != RegistrationStatus.APPROVED:
            mensagem = (
                "Cadastro pendente de aprovação do Auditor"
                if user.registration_status == RegistrationStatus.PENDING
                else "Cadastro rejeitado pelo Auditor"
            )
            register_audit_log(
                user.id, LogAction.ACCESS_DENIED, "FAILURE", user.id,
                momento_requisicao, mensagem, selection_id_e=user.selection_id
            )
            return jsonify({"error": mensagem}), 403

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


def list_pending_registrations(current_user):
    if current_user.role != UserRole.AUDITOR:
        return jsonify({"error": "Acesso negado. Requer papel de AUDITOR."}), 403

    usuarios = User.query.filter(
        User.registration_status == RegistrationStatus.PENDING,
        User.selection_id == current_user.selection_id,
    ).order_by(User.created_at.asc()).all()

    data = [{
        "id": str(usuario.id),
        "full_name": usuario.full_name,
        "email": usuario.email,
        "selection_id": str(usuario.selection_id) if usuario.selection_id else None,
        "created_at": usuario.created_at.isoformat() if usuario.created_at else None,
    } for usuario in usuarios]

    return jsonify({"data": data}), 200


def approve_registration(current_user, user_id):
    if current_user.role != UserRole.AUDITOR:
        return jsonify({"error": "Acesso negado. Requer papel de AUDITOR."}), 403

    fuso_sp = ZoneInfo("America/Sao_Paulo")
    momento_requisicao = datetime.now(fuso_sp)

    dados = request.get_json() or {}
    role_bruta = dados.get("role")

    try:
        role = UserRole(role_bruta)
    except ValueError:
        return jsonify({"error": "Role inválida"}), 400

    usuario = db.session.get(User, user_id)
    if usuario is None:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if usuario.selection_id != current_user.selection_id:
        return jsonify({"error": "Acesso negado. Cadastro pertence a outra seleção."}), 403

    if usuario.registration_status != RegistrationStatus.PENDING:
        return jsonify({"error": "Cadastro já foi processado"}), 409

    usuario.role = role
    usuario.registration_status = RegistrationStatus.APPROVED
    db.session.commit()

    register_audit_log(
        current_user.id, LogAction.REGISTER_APPROVED, "SUCCESS", usuario.id,
        momento_requisicao, f"Cadastro aprovado pelo auditor com papel {role.value}",
        selection_id_e=usuario.selection_id,
    )

    return jsonify({
        "id": str(usuario.id),
        "email": usuario.email,
        "full_name": usuario.full_name,
        "role": usuario.role.value,
        "registration_status": usuario.registration_status.value,
    }), 200


def reject_registration(current_user, user_id):
    if current_user.role != UserRole.AUDITOR:
        return jsonify({"error": "Acesso negado. Requer papel de AUDITOR."}), 403

    fuso_sp = ZoneInfo("America/Sao_Paulo")
    momento_requisicao = datetime.now(fuso_sp)

    usuario = db.session.get(User, user_id)
    if usuario is None:
        return jsonify({"error": "Usuário não encontrado"}), 404

    if usuario.selection_id != current_user.selection_id:
        return jsonify({"error": "Acesso negado. Cadastro pertence a outra seleção."}), 403

    if usuario.registration_status != RegistrationStatus.PENDING:
        return jsonify({"error": "Cadastro já foi processado"}), 409

    usuario.registration_status = RegistrationStatus.REJECTED
    db.session.commit()

    register_audit_log(
        current_user.id, LogAction.REGISTER_REJECTED, "SUCCESS", usuario.id,
        momento_requisicao, "Cadastro rejeitado pelo auditor",
        selection_id_e=usuario.selection_id,
    )

    return jsonify({
        "id": str(usuario.id),
        "email": usuario.email,
        "full_name": usuario.full_name,
        "registration_status": usuario.registration_status.value,
    }), 200


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
