import os
import urllib.parse
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def test_connection():
    print("Iniciando teste de conexão local com o Cloud SQL (via IP Público)...")
    
    # 1. Pega os dados do .env local
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERRO: DATABASE_URL não encontrada no .env")
        return
        
    print(f"DATABASE_URL configurada: {db_url.split('@')[-1]} (ocultando credenciais)")
    
    try:
        # Tenta se conectar
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"SUCESSO! Conectado ao banco de dados.")
        print(f"Versão do Postgres: {db_version[0]}")
        
        # Mostra as tabelas existentes
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print(f"Tabelas encontradas: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"FALHA NA CONEXÃO: {e}")

if __name__ == "__main__":
    test_connection()
