from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.selection import Selection
from app.models.enums.user_role import RegistrationStatus, UserRole
from app.services.auth import hash_password

app = create_app()

with app.app_context():
    db.session.query(User).delete()
    db.session.query(Selection).delete()

    selecao_bra = Selection(name="Confederação Brasileira de Futebol", code="BRA")
    selecao_arg = Selection(name="Associação do Futebol Argentino", code = "ARG" )
    db.session.add(selecao_bra)
    db.session.add(selecao_arg)
    db.session.flush()

    usuarios_seed = [
        User(
            full_name="Staff Técnico Brasil",
            email="tech@cbf.com.br",
            password_hash=hash_password("12345678"),
            role=UserRole.TECHNICAL_STAFF,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=selecao_bra.id
        ),
         User(
            full_name="Staff Técnico Argentina",
            email="tech@afa.com.br",
            password_hash=hash_password("12345678"),
            role=UserRole.TECHNICAL_STAFF,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=selecao_arg.id
        ),
        User(
            full_name="Organizador FIFA",
            email="organizer@fifa.com",
            password_hash=hash_password("12345678"),
            role=UserRole.ORGANIZER,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=selecao_bra.id
        ),
        User(
            full_name="Auditor Independente",
            email="auditor@audit.com",
            password_hash=hash_password("12345678"),
            role=UserRole.AUDITOR,
            registration_status=RegistrationStatus.APPROVED,
            selection_id=None
        )
    ]

    db.session.bulk_save_objects(usuarios_seed)
    db.session.commit()
    print("Seed executado com sucesso! Usuários de teste criados.")