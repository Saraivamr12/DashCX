from databricks import sql
import pandas as pd

# 🔹 Dados de conexão (substitua pelo token correto)
HOST = "dbc-6a9b798d-9256.cloud.databricks.com"
HTTP_PATH = "/sql/1.0/warehouses/31ee6c7460cbead5"
ACCESS_TOKEN = "dapi35df33ea3adaf82c8565b62005f6fcea"

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
    cursor.execute("select *  from headless_bi.client_q700zorent.dim_user")
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
