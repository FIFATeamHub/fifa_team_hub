from flask import request
from app.extensions import db
from app.models.audit_log import AuditLog
from uuid import UUID
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import traceback

FUSO_SP = ZoneInfo("America/Sao_Paulo")


def _coerce_uuid(value):
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def register_audit_log(user_id_e, action_e, status_e, resource_id_e, date_event, details_e = None, selection_id_e = None):

    try :

        with db.session.begin_nested():

            log_falha = AuditLog(
                user_id = user_id_e,
                action = action_e,
                resource_id = _coerce_uuid(resource_id_e),
                ip_address = request.remote_addr or "0.0.0.0",
                status = status_e,
                details = details_e,
                created_at = date_event,
                selection_id = selection_id_e
            )
            db.session.add(log_falha)

        db.session.commit()


    except Exception as e:
        db.session.rollback()
        traceback.print_exc()


class AuditService:
    @staticmethod
    def list_logs(current_user, page=1, per_page=10, action_filter=None, user_id_filter=None, start_date=None, end_date=None):
        query = AuditLog.query

        query = query.filter(AuditLog.selection_id == current_user.selection_id)

        if action_filter:
            query = query.filter(AuditLog.action == action_filter)

        if user_id_filter:
            query = query.filter(AuditLog.user_id == _coerce_uuid(user_id_filter))

        if start_date:
            inicio_local = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=FUSO_SP)
            inicio_utc = inicio_local.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(AuditLog.created_at >= inicio_utc)

        if end_date:
            fim_local = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).replace(tzinfo=FUSO_SP)
            fim_utc = fim_local.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(AuditLog.created_at < fim_utc)

        query = query.order_by(AuditLog.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)
