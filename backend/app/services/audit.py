from flask import request
from app.extensions import db
from app.models.audit_log import AuditLog
from uuid import UUID
import traceback


def _coerce_uuid(value):
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def register_audit_log(user_id_e, action_e, status_e, resource_id_e, date_event, details_e = None):

    try :

        with db.session.begin_nested():

            log_falha = AuditLog(
                user_id = user_id_e,
                action = action_e,
                resource_id = _coerce_uuid(resource_id_e),
                ip_address = request.remote_addr or "0.0.0.0",
                status = status_e,
                details = details_e,
                created_at = date_event
            )
            db.session.add(log_falha)

        # Commita a transação global para garantir a persistência imediata
        db.session.commit()


    except Exception as e:
        db.session.rollback()
        traceback.print_exc()


class AuditService:
    @staticmethod
    def list_logs(page=1, per_page=10, action_filter=None, user_id_filter=None, start_date=None, end_date=None):
        query = AuditLog.query

        # Filtrar por tipo de Ação (ex: LOGIN, UPLOAD, DELETE)
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)

        # Filtrar pelo autor da ação
        if user_id_filter:
            query = query.filter(AuditLog.user_id == user_id_filter)
        
        # Ordenar dos mais recentes para os mais antigos
        query = query.order_by(AuditLog.created_at.desc())

        # Dispara a paginação do próprio SQLAlchemy
        return query.paginate(page=page, per_page=per_page, error_out=False)
