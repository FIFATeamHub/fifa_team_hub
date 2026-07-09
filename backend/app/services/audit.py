from app.models.audit_log import AuditLog

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
