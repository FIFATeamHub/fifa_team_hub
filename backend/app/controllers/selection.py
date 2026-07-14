import re
from uuid import uuid4

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.enums.user_role import RegistrationStatus, UserRole
from app.models.selection import Selection
from app.models.user import User
from app.services.auth import hash_password

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def list_selections():
    selections = Selection.query.order_by(Selection.name).all()

    return jsonify([
        {
            "id": str(s.id),
            "name": s.name,
            "code": s.code
        }
        for s in selections
    ])


def create_selection(current_user):
    if current_user.role != UserRole.ORGANIZER:
        return jsonify({"error": "Acesso negado. Requer papel de ORGANIZER."}), 403

    dados = request.get_json(silent=True) or {}

    campos = ["name", "code", "auditor_name", "auditor_email", "auditor_password"]
    for campo in campos:
        if not dados.get(campo):
            return jsonify({"error": f"Campo '{campo}' é obrigatório"}), 400

    name = dados["name"].strip()
    code = dados["code"].strip().upper()
    auditor_name = dados["auditor_name"].strip()
    auditor_email = dados["auditor_email"].strip().lower()
    auditor_password = dados["auditor_password"]

    if len(code) != 3:
        return jsonify({"error": "O código da seleção deve ter exatamente 3 caracteres."}), 400

    if not re.match(EMAIL_REGEX, auditor_email):
        return jsonify({"error": "Formato de e-mail do auditor inválido."}), 400

    if len(auditor_password) < 8:
        return jsonify({"error": "A senha do auditor deve ter no mínimo 8 caracteres."}), 400

    if Selection.query.filter_by(code=code).first():
        return jsonify({"error": "Já existe uma seleção cadastrada com este código."}), 400

    if User.query.filter_by(email=auditor_email).first():
        return jsonify({"error": "Este e-mail de auditor já está cadastrado."}), 400

    selection_id = uuid4()

    try:
        selection = Selection(id=selection_id, name=name, code=code)
        db.session.add(selection)

        auditor = User(
            full_name=auditor_name,
            email=auditor_email,
            password_hash=hash_password(auditor_password),
            role=UserRole.AUDITOR,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=selection_id,
        )
        db.session.add(auditor)

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Já existe uma seleção ou auditor com estes dados."}), 400

    return jsonify({
        "selection": {
            "id": str(selection.id),
            "name": selection.name,
            "code": selection.code,
        },
        "auditor": {
            "id": str(auditor.id),
            "full_name": auditor.full_name,
            "email": auditor.email,
            "role": auditor.role.value,
        },
    }), 201
