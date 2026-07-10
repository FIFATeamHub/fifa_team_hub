import uuid
import io

def test_delete_inexistent_document(client, token_bra_staff):
    # Simula a tentativa de exclusão com um UUID que com certeza não está no banco
    id_falso = str(uuid.uuid4())
    response = client.delete(
        f"/api/document/{id_falso}",
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    # Garante que a aplicação avisa que o recurso não existe em vez de quebrar
    assert response.status_code == 404


def test_delete_document_success(client, token_bra_staff):
    # Setup: Criar um documento isolado para a execução do nosso teste
    data = {"doc_type": "CONVOCADO", "file": (io.BytesIO(b"%PDF-1.4\n%%EOF"), "teste_delete.pdf")}
    resp_upload = client.post(
        "/api/document/upload", 
        headers={"Authorization": f"Bearer {token_bra_staff}"}, 
        data=data, content_type="multipart/form-data"
    )
    doc_id = resp_upload.json["id"]

    # Act: Disparar nosso controller de exclusão
    response = client.delete(
        f"/api/document/{doc_id}", 
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    
    # Assert: Validar o nosso "Soft Delete" e limpeza de base
    assert response.status_code == 200
    assert response.json["message"] == "Documento removido"
