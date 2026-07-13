from flask import request, jsonify
from app.services.audit import AuditService
from app.models.enums.user_role import UserRole

def list_audit_logs(current_user):
    #Trava de Segurança
    if current_user.role != UserRole.AUDITOR:
        return jsonify({"error": "Acesso negado. Requer papel de AUDITOR."}), 403

    # Captura os parâmetros da URL, e com fallback para paginação padrão
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    action_filter = request.args.get('action')
    user_id_filter = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Devolve a bucha para o nosso Service
    paginated_result = AuditService.list_logs(
        current_user=current_user,
        page=page,
        per_page=per_page,
        action_filter=action_filter,
        user_id_filter=user_id_filter,
        start_date=start_date,
        end_date=end_date
    )

    data_list = []
    for log in paginated_result.items:
        data_list.append({
            "id": str(log.id),
            "user_id": str(log.user_id),
            "action": log.action.value if hasattr(log.action, 'value') else str(log.action),
            "resource_id": str(log.resource_id) if log.resource_id else None,
            "status": log.status,
            "ip_address": log.ip_address,
            "details": log.details,
            "created_at": log.created_at.isoformat() + "Z" if log.created_at else None
        })

    return jsonify({
        "data": data_list,
        "pagination": {
            "page": paginated_result.page,
            "per_page": paginated_result.per_page,
            "total": paginated_result.total,
            "pages": paginated_result.pages
        }
    }), 200
