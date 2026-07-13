import requests
import json

BASE_URL = "http://localhost:5000"

def run_test():
    print("--- INICIANDO TESTE DA ISSUE #149 ---")
    
    # 1. Login Auditor 1
    print("\n1. Fazendo login como auditor1...")
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "auditor1@teste.com",
        "password": "12345678"
    })
    token1 = res.json().get("access_token")
    headers1 = {"Authorization": f"Bearer {token1}"}
    print("Sucesso! Token gerado.")

    # 2. Upload do Passaporte como Auditor 1
    print("\n2. Auditor 1 enviando um Passaporte...")
    files = {'file': ('passaporte_teste.pdf', b'conteudo_fake_do_pdf', 'application/pdf')}
    data = {'type_document': 'PASSPORT'}
    res = requests.post(f"{BASE_URL}/api/document/upload", headers=headers1, files=files, data=data)
    doc = res.json()
    doc_id = doc.get("id")
    print(f"Documento criado com ID: {doc_id}")
    print(f"Status Inicial (Tem que ser PENDING): {doc.get('status')}")

    # 3. Auditor 1 tenta aprovar o próprio documento
    print("\n3. Auditor 1 tenta APROVAR o próprio Passaporte (deve ser bloqueado)...")
    res = requests.patch(f"{BASE_URL}/api/document/{doc_id}/review", headers=headers1, json={"status": "APPROVED"})
    print(f"Status HTTP retornado: {res.status_code}")
    print(f"Mensagem de erro: {res.json().get('error')}")

    # 4. Login Auditor 2
    print("\n4. Fazendo login como auditor2 (para revisão por pares)...")
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "auditor2@teste.com",
        "password": "12345678"
    })
    token2 = res.json().get("access_token")
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 5. Auditor 2 aprova o documento
    print("\n5. Auditor 2 tenta APROVAR o Passaporte do Auditor 1...")
    res = requests.patch(f"{BASE_URL}/api/document/{doc_id}/review", headers=headers2, json={"status": "APPROVED"})
    print(f"Status HTTP retornado: {res.status_code}")
    print(f"Status Final do Documento: {res.json().get('status')}")

    print("\n--- TESTE CONCLUÍDO COM SUCESSO ---")

if __name__ == "__main__":
    run_test()
