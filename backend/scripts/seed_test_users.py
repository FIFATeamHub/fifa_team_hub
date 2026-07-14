import sys
import os

# Adiciona o diretório backend ao path para conseguir importar app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.selection import Selection
from app.models.enums.user_role import UserRole, RegistrationStatus
from app.services.auth import hash_password

os.environ["DATABASE_URL"] = "postgresql://fifa_user:fifa_password@localhost:15432/fifa_team_hub"
app = create_app()

with app.app_context():
    print("Injetando dados de teste no banco...")
    sel = Selection.query.filter_by(code="BRA").first()
    if not sel:
        sel = Selection(name="Brasil", code="BRA")
        db.session.add(sel)
        db.session.commit()

    doc = User.query.filter_by(email="medico@teste.com").first()
    if not doc:
        doc = User(
            email="medico@teste.com",
            password_hash=hash_password("12345678"),
            full_name="Dr. Teste Brasil",
            role=UserRole.MEDICAL_STAFF,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=sel.id
        )
        db.session.add(doc)
    else:
        doc.role = UserRole.MEDICAL_STAFF
        doc.registration_status = RegistrationStatus.APPROVED
        doc.selection_id = sel.id
    
    jog = User.query.filter_by(email="jogador@teste.com").first()
    if not jog:
        jog = User(
            email="jogador@teste.com",
            password_hash=hash_password("12345678"),
            full_name="Jogador Teste Brasil",
            role=UserRole.ATHELETE,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=sel.id
        )
        db.session.add(jog)
    else:
        jog.role = UserRole.ATHELETE
        jog.registration_status = RegistrationStatus.APPROVED
        jog.selection_id = sel.id

    db.session.commit()
    print("✅ Contas prontas!")
