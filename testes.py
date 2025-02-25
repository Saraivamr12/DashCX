import json
import os
from databricks import sql

# 🔹 Carregar configurações do JSON
with open("config.json", "r") as file:
    config = json.load(file)

# 🔹 Obter credenciais do JSON
HOST = config.get("DATABRICKS_HOST")
HTTP_PATH = config.get("DATABRICKS_HTTP_PATH")
ACCESS_TOKEN = config.get("DATABRICKS_ACCESS_TOKEN")

# Verificar se todas as credenciais foram carregadas corretamente
if not all([HOST, HTTP_PATH, ACCESS_TOKEN]):
    raise ValueError("❌ Erro: Configurações ausentes no JSON!")

# Criar a conexão com o Databricks
try:
    conn = sql.connect(
        server_hostname=HOST,
        http_path=HTTP_PATH,
        access_token=ACCESS_TOKEN
    )

    print("✅ Conexão bem-sucedida!")

    # Criar cursor
    cursor = conn.cursor()

    # Executar uma query simples
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
