import os
from google.cloud import storage

# Limpa resíduos de ambiente
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

print("--- TESTE DE INTEGRAÇÃO REAL (UPLOAD) ---")

try:
    # AJUSTE AQUI: Adicione o caminho 'config/' antes do nome do arquivo
    client = storage.Client.from_service_account_json(
        "config/fifa-team-hub-key.json",
        project="fifa-team-hub"
    )
    
    bucket = client.bucket("fifa-team-hub-documents")
    
    # Tenta criar um arquivo de teste dentro do bucket
    blob = bucket.blob("testes_desenvolvimento/conexao.txt")
    
    print("Tentando fazer upload de um arquivo de teste...")
    blob.upload_from_string("Conexão do FIFA Team Hub realizada com sucesso!")
    print("✓ UPLOAD CONCLUÍDO!")
    
    # Tenta ler o arquivo de volta
    print("Tentando ler o arquivo do bucket...")
    conteudo = blob.download_as_string()
    print(f"✓ DOWNLOAD CONCLUÍDO! Conteúdo: {conteudo.decode('utf-8')}")
    
    # Limpeza
    blob.delete()
    print("✓ Arquivo de teste removido do bucket.")

except FileNotFoundError:
    print("❌ ERRO: O arquivo não foi encontrado em 'config/fifa-team-hub-key.json'!")
    print("Verifique se o nome da pasta e do arquivo estão escritos exatamente assim.")
except Exception as e:
    print(f"❌ Falha no teste: {e}")