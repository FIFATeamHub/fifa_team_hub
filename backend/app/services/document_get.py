from app.config.database import db
from app.models.document import Document
from sqlalchemy import or_, and_

class DocumentService:

    
    @staticmethod
    def list_accessible_documents(current_user, doc_type_filter=None, page=1, per_page=10):
        """
        Monta a query com base no perfil do usuário, aplica filtros opcionais da URL
        e retorna o objeto paginado do SQLAlchemy.
        """
        user_role = current_user.role
        user_id = current_user.id
        selection_id = current_user.selection_id

        # 1. Inicializa a query básica
        query = db.session.query(Document)

        # 2. Aplica a árvore estrita de permissões (RBAC)
        if user_role == "ORGANIZER":
            query = query.filter(Document.type.in_(["PASSPORT", "CONVOCADO"]))

        elif user_role == "AUDITOR":
            query = query.filter(
                Document.selection_id == selection_id,
                Document.type.in_(["PASSPORT", "LAUDO_MEDICO"])
            )

        elif user_role == "TECHNICAL_STAFF":
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type.in_(["CONVOCADO", "LAUDO_MEDICO", "RELATORIO_TATICO", "ESQUEMA_JOGADAS"]),
                    and_(Document.type == "PASSPORT", Document.user_id == user_id)
                )
            )

        elif user_role == "MEDICAL_STAFF":
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type == "LAUDO_MEDICO",
                    and_(Document.type == "PASSPORT", Document.user_id == user_id)
                )
            )

        elif user_role == "ATHELETE":
            query = query.filter(
                Document.selection_id == selection_id,
                or_(
                    Document.type.in_(["CONVOCADO", "LAUDO_MEDICO", "RELATORIO_TATICO", "ESQUEMA_JOGADAS"]),
                    and_(Document.type == "PASSPORT", Document.user_id == user_id)
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
        """
        Busca um documento por ID e valida se o usuário autenticado 
        possui permissão estrita de leitura sobre ele.
        Retorna uma tupla: (documento_objeto, "motivo_do_erro_se_houver")
        """
        # 1. Busca inicial no banco
        document = db.session.query(Document).get(document_id)
        if not document:
            return None, "NOT_FOUND"

        user_role = current_user.role
        user_id = current_user.id
        selection_id = current_user.selection_id

        # 2. Validação da Matriz de Permissões
        
        # --- Caso do ORGANIZER ---
        if user_role == "ORGANIZER":
            if document.type in ["PASSPORT", "CONVOCADO"]:
                return document, None
            return None, f"ORGANIZER tentou acessar tipo restrito: {document.type}"

        # --- Caso dos demais perfis vinculados a uma seleção ---
        else:
            # Trava Primária: Garantia absoluta de isolamento de país/seleção
            if document.selection_id != selection_id:
                return None, f"Usuário da seleção {selection_id} tentou acessar documento da seleção {document.selection_id}"

            # Trava Secundária: Validação por tipo permitido dentro da seleção
            if user_role == "AUDITOR":
                if document.type in ["PASSPORT", "LAUDO_MEDICO"]:
                    return document, None
                return None, "AUDITOR tentou acessar tipo não autorizado"

            elif user_role in ["TECHNICAL_STAFF", "ATHELETE"]:
                # Vê os documentos táticos/gerais do time OU o seu PRÓPRIO passaporte
                if document.type in ["CONVOCADO", "LAUDO_MEDICO", "RELATORIO_TATICO", "ESQUEMA_JOGADAS"]:
                    return document, None
                elif document.type == "PASSPORT" and document.user_id == user_id:
                    return document, None
                return None, "TECHNICAL_STAFF/ATHLETE tentou acessar passaporte de terceiro ou tipo inválido"

            elif user_role == "MEDICAL_STAFF":
                # Vê LAUDO_MEDICO do time OU o seu PRÓPRIO passaporte
                if document.type == "LAUDO_MEDICO":
                    return document, None
                elif document.type == "PASSPORT" and document.user_id == user_id:
                    return document, None
                return None, "MEDICAL_STAFF tentou acessar passaporte de terceiro ou documento tático"

        return None, "PERMISSAO_INVALIDA"