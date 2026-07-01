import os

from datetime import datetime
from flask import g, Blueprint

from app.models import Document
from app.models import AuditLog
from app.middlewares import auth
from app.extensions import db
from app.middlewares.auth import require_auth, require_role

blueprint_name = Blueprint("Delete", __name__)

@blueprint_name.route("/<int:document_id>", methods = ["DELETE"])
@require_auth
@require_role("TECHNICAL_STAFF")


def delete(document_id):
    document = Document.query.get(document_id)

    if document.uploaded_by != g.current_user_id:
        return {"error": "Permissão negada"}, 403
        
    if document.selection_id == g.current_selection_id:
        if os.path.exists(document.storage_path):
            os.remove(document.storage_path)
            audit_entry = AuditLog(
                action = "DELETE",
                status = "SUCCESS"
            )
            document.deleted_at = datetime.utcnow() 
            db.session.add(audit_entry)

        db.session.add(document)
        db.session.commit()

        return 204
    else:
        audit_entry = AuditLog(
            action = "ACCESS DENIED"
        )
        db.session.add(audit_entry)
        db.session.commit()
        return {"error": "Permissão não concedida"}, 403
    