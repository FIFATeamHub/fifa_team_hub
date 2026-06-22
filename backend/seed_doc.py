from app import create_app
from app.config.database import db
from app.models.user import User
from app.models.selection import Selection
from app.models.document import Document
from app.models.enums.user_role import TypeDocument

app = create_app()

with app.app_context():
    # 1. Pega o usuario de teste
    user = User.query.first()
    if not user:
        print("Usuario nao encontrado!")
        exit(1)

    # 2. Cria selecao caso nao exista
    sel = Selection.query.first()
    if not sel:
        sel = Selection(name="Brasil", code="BRA")
        db.session.add(sel)
        db.session.commit()

    # 3. Cria documento falso
    doc = Document(
        selection_id=sel.id,
        uploaded_by=user.id,
        type=TypeDocument.PASSPORT,
        filename="passaporte_jogador.pdf",
        storage_url="gs://fifa_team_hub_bucket/passaporte_jogador.pdf"
    )
    db.session.add(doc)
    db.session.commit()
    print("Documento inserido com sucesso!")
