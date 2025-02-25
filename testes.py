import json
import os
import pandas as pd
from databricks import sql

# 🔹 Verificar se o arquivo JSON existe
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"❌ Erro: O arquivo {CONFIG_FILE} não foi encontrado!")

# 🔹 Carregar configurações do JSON
try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
except json.JSONDecodeError:
    raise ValueError("❌ Erro: O arquivo JSON está mal formatado!")

# 🔹 Obter credenciais do JSON
HOST = config.get("DATABRICKS_HOST")
HTTP_PATH = config.get("DATABRICKS_HTTP_PATH")
ACCESS_TOKEN = config.get("DATABRICKS_ACCESS_TOKEN")

# 🔹 Verificar se todas as credenciais foram carregadas corretamente
if not all([HOST, HTTP_PATH, ACCESS_TOKEN]):
    raise ValueError("❌ Erro: Configurações ausentes no JSON! Verifique o arquivo.")

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
    QUERY = "SELECT * FROM headless_bi.client_q700zorent.dim_user LIMIT 10"
    cursor.execute(QUERY)
    dados = cursor.fetchall()

    # Transformar em DataFrame
    if dados:
        df = pd.DataFrame(dados, columns=[desc[0] for desc in cursor.description])
        print(df)  # Exibir os dados no console
    else:
        print("⚠ Nenhum dado retornado pela consulta.")

    # Fechar conexão
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Erro na conexão com Databricks:", e)
