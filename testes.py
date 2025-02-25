from databricks import sql
import pandas as pd
import os
from dotenv import load_dotenv

# 🔹 Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# 🔹 Dados de conexão (obtidos das variáveis de ambiente)
HOST = os.getenv("DATABRICKS_HOST")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
ACCESS_TOKEN = os.getenv("DATABRICKS_ACCESS_TOKEN")

# Verificação para garantir que os dados foram carregados corretamente
if not all([HOST, HTTP_PATH, ACCESS_TOKEN]):
    raise ValueError("❌ Erro: Variáveis de ambiente ausentes. Verifique o arquivo .env.")

# Criar a conexão
try:
    conn = sql.connect(
        server_hostname=HOST,
        http_path=HTTP_PATH,
        access_token=ACCESS_TOKEN
    )

    print("✅ Conexão bem-sucedida!")

    # Criar cursor
    cursor = conn.cursor()

    # Executar uma query simples (ajuste conforme necessário)
    cursor.execute("SELECT * FROM headless_bi.client_q700zorent.dim_user")
    dados = cursor.fetchall()

    # Transformar em DataFrame
    df = pd.DataFrame(dados, columns=[desc[0] for desc in cursor.description])

    # Fechar conexão
    cursor.close()
    conn.close()

    # Exibir os dados
    print(df)

except Exception as e:
    print("❌ Erro na conexão:", e)
