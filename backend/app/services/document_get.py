from app.extensions import db
from app.models.document import Document
from app.models.enums.user_role import UserRole, TypeDocument
from sqlalchemy import or_, and_

class DocumentService:

    
    @staticmethod
    def list_accessible_documents(current_user, doc_type_filter=None, page=1, per_page=10):

        user_role = current_user.role
        user_id = current_user.id
        selection_id = current_user.selection_id

        # 1. Inicializa a query básica
        query = db.session.query(Document)

        # 2. Aplica a árvore estrita de permissões (RBAC)
        if user_role == UserRole.ORGANIZER:
            query = query.filter(Document.type.in_([TypeDocument.PASSPORT, TypeDocument.CONVOCADO]))

        elif user_role == UserRole.AUDITOR:
            query = query.filter(
                Document.selection_id == selection_id,
                Document.type.in_([TypeDocument.PASSPORT, TypeDocument.LAUDO_MEDICO])
            )

        elif user_role == UserRole.TECHNICAL_STAFF:
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type.in_([TypeDocument.CONVOCADO, TypeDocument.LAUDO_MEDICO, TypeDocument.RELATORIO_TATICO, TypeDocument.ESQUEMA_JOGADAS]),
                    and_(Document.type == TypeDocument.PASSPORT, Document.uploaded_by == user_id)
                )
            )

        elif user_role == UserRole.MEDICAL_STAFF:
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type == TypeDocument.LAUDO_MEDICO,
                    and_(Document.type == TypeDocument.PASSPORT, Document.uploaded_by == user_id)
                )
            )

        elif user_role == UserRole.ATHELETE:
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type.in_([TypeDocument.CONVOCADO, TypeDocument.LAUDO_MEDICO, TypeDocument.RELATORIO_TATICO, TypeDocument.ESQUEMA_JOGADAS]),
                    and_(Document.type == TypeDocument.PASSPORT, Document.uploaded_by == user_id)
                )
            )
        else:
            # Se o perfil não for mapeado, retorna None para a controller barrar
            return None

        # 3. Suporte ao Filtro de URL Dinâmico (?doc_type=X)
        if doc_type_filter:
            query = query.filter(Document.type == doc_type_filter)

        # 4. Ordenação Padrão exigida (Mais recentes primeiro)
        query = query.order_by(Document.created_at.desc())

        # 5. Executa e retorna a paginação nativa do SQLAlchemy (LIMIT / OFFSET)
        return query.paginate(page=page, per_page=per_page, error_out=False)
    



    @staticmethod
    def get_accessible_document(current_user, document_id):
        # 1. Busca inicial no banco
        document = db.session.query(Document).get(document_id)
        if not document:
            return None, "NOT_FOUND"

        user_role = current_user.role
        user_id = current_user.id
        selection_id = current_user.selection_id

        # 2. Validação da Matriz de Permissões
        
        # --- Caso do ORGANIZER ---
        if user_role == UserRole.ORGANIZER:
            if document.type in [TypeDocument.PASSPORT, TypeDocument.CONVOCADO]:
                return document, None
            return None, f"ORGANIZER tentou acessar tipo restrito: {document.type}"

        # --- Caso dos demais perfis vinculados a uma seleção ---
        else:
            # Trava Primária: Garantia absoluta de isolamento de país/seleção
            if document.selection_id != selection_id:
                return None, f"Usuário da seleção {selection_id} tentou acessar documento da seleção {document.selection_id}"

            # Trava Secundária: Validação por tipo permitido dentro da seleção
            if user_role == UserRole.AUDITOR:
                if document.type in [TypeDocument.PASSPORT, TypeDocument.LAUDO_MEDICO]:
                    return document, None
                return None, "AUDITOR tentou acessar tipo não autorizado"

            elif user_role in [UserRole.TECHNICAL_STAFF, UserRole.ATHELETE]:
                # Vê os documentos táticos/gerais do time OU o seu PRÓPRIO passaporte
                if document.type in [TypeDocument.CONVOCADO, TypeDocument.LAUDO_MEDICO, TypeDocument.RELATORIO_TATICO, TypeDocument.ESQUEMA_JOGADAS]:
                    return document, None
                elif document.type == TypeDocument.PASSPORT and document.uploaded_by == user_id:
                    return document, None
                return None, "TECHNICAL_STAFF/ATHLETE tentou acessar passaporte de terceiro ou tipo inválido"

            elif user_role == UserRole.MEDICAL_STAFF:
                # Vê LAUDO_MEDICO do time OU o seu PRÓPRIO passaporte
                if document.type == TypeDocument.LAUDO_MEDICO:
                    return document, None
                elif document.type == TypeDocument.PASSPORT and document.uploaded_by == user_id:
                    return document, None
                return None, "MEDICAL_STAFF tentou acessar passaporte de terceiro ou documento tático"

        return None, "PERMISSAO_INVALIDA"