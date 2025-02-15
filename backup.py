from wordcloud import WordCloud
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re


st.set_page_config(
    page_title="Dashboard KPIs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dados de autenticação
USER_CREDENTIALS = {
    "CX": "Cx@wap",
    "user1": "123",
    "user2": "12345",
    "wap2025": "wap2025"
}

# Inicializa o estado de autenticação
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# Função de autenticação
def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password

# Página de Login
def login_page():
    st.title("Login")
    st.write("Por favor, faça login para acessar o dashboard.")

    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        login_button = st.form_submit_button("Entrar")

        if login_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.current_page = "dashboard"
                st.stop()
            else:
                st.error("Usuário ou senha incorretos. Tente novamente.")

def adicionar_logout():
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_page = "login"
            

# Página com valores gerais
def valores_gerais(df, calls_data):
    st.title("KPIs Agrupados - Visão Geral")
    adicionar_logout()
            # Estilo Customizado


# CSS para personalizar a aparência
 
    total_chamadas = calls_data.shape[0]

    # Convertendo centésimos de segundos para segundos (1 segundo = 100 centésimos de segundo)
    duracao_media_segundos = round(calls_data["Duration"].mean() / 100, 2)  # Agora o cálculo está correto!

    # Cálculo da taxa de abandono
    chamadas_abandonadas = calls_data[calls_data["Abandon"] == 1].shape[0]
    notas_validas = calls_data[calls_data['NotaAtendimento'].notnull()]

    # Calculando a frequência de cada nota
    frequencia_notas = notas_validas['NotaAtendimento'].value_counts().sort_index()

    # Criando um DataFrame para as notas e quantidades
    df_notas = pd.DataFrame({
        'Nota': frequencia_notas.index,
        'Qtde': frequencia_notas.values
    })

    # Calculando o total de cada nota (Nota * Qtde)
    df_notas['Total'] = df_notas['Nota'] * df_notas['Qtde']

    # Calculando a Nota de Satisfação (Soma dos Totais / Soma das Quantidades)
    nota_satisfacao = df_notas['Total'].sum() / df_notas['Qtde'].sum()

    # Outros KPIs
    total_chamadas = calls_data.shape[0]

    # Convertendo a duração de chamadas de centésimos de segundos para segundos
    duracao_media_segundos = round(calls_data["Duration"].mean() / 100, 2)

    # Calculando a taxa de abandono
    chamadas_abandonadas = calls_data[calls_data["Abandon"] == 1].shape[0]
    taxa_abandono = round((chamadas_abandonadas / total_chamadas) * 100, 2) if total_chamadas > 0 else 0

    # Calculando a média das notas de atendimento
    media_nota_atendimento = round(calls_data["NotaAtendimento"].mean(), 2)

    # Exibindo os KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="📞 Total de Chamadas", value=f"{total_chamadas:,}".replace(",", "."))
    with col2:
        st.metric(label="⏳ Tempo Médio", value=f"{duracao_media_segundos:.2f} seg")
    with col3:
        st.metric(label="📉 Taxa de Abandono", value=f"{taxa_abandono:.2f}%")
    with col4:
        st.metric(label="⭐ Nota Média", value=f"{media_nota_atendimento:.2f}")

    # Funções para cálculos
    def calcular_volume_atendimentos(data):
        calls_per_hour = data.groupby(data['CallLocalTime'].dt.hour).size()
        return calls_per_hour

    def calcular_frequencia_notas(data):
        notas_validas = data[data['NotaAtendimento'].notnull()]
        frequencia_notas = notas_validas['NotaAtendimento'].value_counts().sort_index()
        return frequencia_notas

    def calcular_taxa_abandono(data):
        total_chamadas = len(data)
        
        if total_chamadas == 0:  # Evita divisão por zero
            return {"taxa_abandono": 0, "chamadas_abandonadas": 0, "chamadas_concluidas": 0}

        chamadas_abandonadas = data[data["Abandon"] == 1].shape[0]
        chamadas_concluidas = total_chamadas - chamadas_abandonadas
        taxa_abandono = (chamadas_abandonadas / total_chamadas) * 100

        return {
            "taxa_abandono": round(taxa_abandono, 2),
            "chamadas_abandonadas": chamadas_abandonadas,
            "chamadas_concluidas": chamadas_concluidas
        }
    
    def calcular_taxa_resolucao(data):
        """
        Calcula a taxa de resolução considerando que um número (ANI) não repetido é resolvido.
        """
        # Filtra as chamadas que possuem nota de atendimento
        chamadas_com_nota = data[data["NotaAtendimento"].notnull()]

        # Conta o total de chamadas com nota
        total_chamadas_com_nota = len(chamadas_com_nota)

        # Identifica os números (ANI) únicos e repetidos
        chamadas_com_ani_unico = chamadas_com_nota.groupby("ANI").filter(lambda x: len(x) == 1)  # Número único
        chamadas_com_ani_repetido = chamadas_com_nota.groupby("ANI").filter(lambda x: len(x) > 1)  # Número repetido

        # Chamadas resolvidas: números únicos
        chamadas_resolvidas = len(chamadas_com_ani_unico)

        # Chamadas não resolvidas: números repetidos
        chamadas_nao_resolvidas = len(chamadas_com_ani_repetido)

        # Calcula a taxa de resolução
        taxa_resolucao = (chamadas_resolvidas / total_chamadas_com_nota) * 100 if total_chamadas_com_nota > 0 else 0

        return [chamadas_resolvidas, chamadas_nao_resolvidas, taxa_resolucao]

    # Volume de Atendimentos por Hora
    calls_per_hour = calcular_volume_atendimentos(calls_data)
    fig1 = px.line(
        x=calls_per_hour.index,
        y=calls_per_hour.values,
        title="Volume de Atendimentos por Hora",
        labels={"x": "Horário", "y": "Quantidade de Atendimentos"},
        markers=True
    )
    fig1.update_traces(line=dict(color="#0979b0", width=5), marker=dict(size=8, color="gray", symbol="circle"), fill='tozeroy')


    # Frequência de Notas
    frequencia_notas = calcular_frequencia_notas(calls_data)
    fig2 = px.bar(
        x=frequencia_notas.index,
        y=frequencia_notas.values,
        title="Taxa de Satisfação do Cliente",
        labels={"x": "Notas de Atendimento", "y": "Avaliações"},
        text=frequencia_notas.values,
        color_discrete_sequence=["#0979b0"]
    )
    fig2.update_traces(texttemplate="%{text}", textposition="outside")


    dados_abandono = calcular_taxa_abandono(calls_data)
    dados_resolucao = calcular_taxa_resolucao(calls_data)

    # Extraindo os valores para os gráficos
    labels_abandono = ["Abandonadas", "Concluídas"]
    values_abandono = [dados_abandono["chamadas_abandonadas"], dados_abandono["chamadas_concluidas"]]

    labels_resolucao = ["Resolvidas", "Não Resolvidas"]
    values_resolucao = dados_resolucao  # Essa função já retorna uma lista, então está correto

    # Gráfico de Taxa de Abandono
    fig3 = go.Figure(
        data=[go.Pie(
            labels=labels_abandono,
            values=values_abandono,
            hole=0.4,
            textinfo="percent+label",
            marker=dict(colors=["#6b6b6b", "#0979b0"], line=dict(color="white", width=1))
        )]
    )

    # Gráfico de Taxa de Resolução
    fig4 = go.Figure(
        data=[go.Pie(
            labels=labels_resolucao,
            values=values_resolucao,
            hole=0.4,
            textinfo="percent+label",
            marker=dict(colors=["#0979b0", "#6b6b6b"], line=dict(color="white", width=1))
        )]
    )


    # Exibição dos gráficos
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.plotly_chart(fig4, use_container_width=True)

# Página com valores por dia
def valores_por_dia(df, calls_data):
    st.title("KPIs Detalhados - Visão por Dia")



    # Filtro de datas
    def calcular_taxa_abandono_diaria(data):
        chamadas_por_dia = data.groupby(data['CallLocalTime'].dt.date)
        resultados = []
        for dia, chamadas in chamadas_por_dia:
            total_chamadas = len(chamadas)
            chamadas_abandonadas = chamadas[chamadas["Abandon"] == 1].shape[0]
            chamadas_concluidas = total_chamadas - chamadas_abandonadas
            resultados.append({"Dia": dia, "Abandonadas": chamadas_abandonadas, "Concluídas": chamadas_concluidas})
        return pd.DataFrame(resultados)

    def calcular_taxa_resolucao_diaria(data):
        chamadas_por_dia = data.groupby(data['CallLocalTime'].dt.date)
        resultados = []
        for dia, chamadas in chamadas_por_dia:
            chamadas_com_nota = chamadas[chamadas["NotaAtendimento"].notnull()]
            total_chamadas_com_nota = len(chamadas_com_nota)
            chamadas_resolvidas = chamadas_com_nota[chamadas_com_nota["NotaAtendimento"] >= 4].shape[0]
            chamadas_nao_resolvidas = total_chamadas_com_nota - chamadas_resolvidas
            resultados.append({"Dia": dia, "Resolvidas": chamadas_resolvidas, "Não Resolvidas": chamadas_nao_resolvidas})
        return pd.DataFrame(resultados)


    def calcular_taxas_por_atendente(data):
        resultados = []
        for atendente in data["Nome Atendente"].dropna().unique():
            dados_atendente = data[data["Nome Atendente"] == atendente]

            # Excluindo chamadas abandonadas (Abandon == 1)
            dados_atendente = dados_atendente[dados_atendente["Abandon"] != 1]

            # Total de chamadas do atendente (sem contar os abandonos)
            total_chamadas = len(dados_atendente)

            # Identificando as chamadas repetidas (mesmo ANI)
            chamadas_com_nota = dados_atendente[dados_atendente["NotaAtendimento"].notnull()]
            chamadas_repetidas = chamadas_com_nota.groupby("ANI").size()  # Contando as repetições de chamadas

            # Chamadas resolvidas: consideramos como resolvidas as chamadas únicas (que não se repetem)
            chamadas_resolvidas = chamadas_repetidas[chamadas_repetidas == 1].count()

            # Taxa de Resolução: % de chamadas resolvidas em relação ao total de chamadas
            taxa_resolucao = (chamadas_resolvidas / total_chamadas) * 100 if total_chamadas > 0 else 0

            # Cálculo da Nota Média por Atendente
            nota_media = dados_atendente["NotaAtendimento"].mean()

            # Adicionando os resultados à lista
            resultados.append({
                "Nome Atendente": atendente,
                "Chamadas Totais": total_chamadas,
                "Chamadas Resolvidas": chamadas_resolvidas,
                "Taxa de Resolução (%)": round(taxa_resolucao, 2),
                "Nota Média": round(nota_media, 2)
            })

        # Convertendo a lista de resultados para um DataFrame
        df_resultados = pd.DataFrame(resultados)

        # Gerando o gráfico de barras para a Nota Média por Atendente
        fig = px.bar(
            df_resultados,
            x="Nome Atendente",  # Eixo X será o nome do atendente
            y="Nota Média",  # Eixo Y será a nota média
            title="Nota Média por Atendente",  # Título do gráfico
            labels={"Nome Atendente": "Atendente", "Nota Média": "Nota Média"},  # Rótulos dos eixos
            color="Nota Média",  # Cor do gráfico com base na nota média
            color_continuous_scale="Viridis",  # Escolhendo a paleta de cores
        )

        # Exibindo o gráfico de barras
        st.plotly_chart(fig, use_container_width=True)

        # Retornando o DataFrame com os resultados
        return df_resultados


    # Carregar os dados diretamente da planilha base
    @st.cache_data
    def carregar_dados():
        data = pd.read_excel("Relatório de Ligações Jan25.xlsx")
        data["CallLocalTime"] = pd.to_datetime(data["CallLocalTime"])  # Converter para datetime
        return data

    # Carregar os dados da planilha
    calls_data = carregar_dados()

    # Configuração da barra lateral com filtros
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro de datas
        min_date = calls_data['CallLocalTime'].min().date()
        max_date = calls_data['CallLocalTime'].max().date()
        start_date = st.date_input("Data inicial", min_date, min_value=min_date, max_value=max_date, key="start_date_key")
        end_date = st.date_input("Data final", max_date, min_value=min_date, max_value=max_date, key="end_date_key")
        
        if start_date > end_date:
            st.error("A data inicial não pode ser maior que a data final.")
            st.stop()
        
        # Filtrar dados por intervalo de datas
        filtered_data = calls_data[(calls_data['CallLocalTime'].dt.date >= start_date) & 
                                (calls_data['CallLocalTime'].dt.date <= end_date)]
        
        # Filtro por atendente
        atendentes = ["Todos"] + list(filtered_data["Nome Atendente"].dropna().unique())
        atendente_selecionado = st.selectbox("Selecione o atendente", options=atendentes)

        # Filtrar os dados por atendente selecionado
        if atendente_selecionado != "Todos":
            filtered_data = filtered_data[filtered_data["Nome Atendente"] == atendente_selecionado]

    # Cálculos de taxas
    taxa_abandono_diaria = calcular_taxa_abandono_diaria(filtered_data)
    taxa_resolucao_diaria = calcular_taxa_resolucao_diaria(filtered_data)
    taxas_por_atendente = calcular_taxas_por_atendente(filtered_data)

    # Gráficos diários
    fig_abandono_diaria = px.bar(
        taxa_abandono_diaria,
        x="Dia",
        y=["Abandonadas", "Concluídas"],
        title="Taxa de Abandono por Dia",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=["#696969", "#FFD700"]
    )

    fig_resolucao_diaria = px.bar(
        taxa_resolucao_diaria,
        x="Dia",
        y=["Resolvidas", "Não Resolvidas"],
        title="Taxa de Resolução por Dia",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=["#FFD700", "#696969"]
    )

    fig_resolucao_por_atendente = px.bar(
        taxas_por_atendente,
        x="Nome Atendente",
        y="Taxa de Resolução (%)",
        title="Taxa de Resolução por Atendente",
        text="Taxa de Resolução (%)",
        color_discrete_sequence=['#FFD700', "#696969"]
    )
    fig_resolucao_por_atendente.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

    # Exibição dos gráficos
    st.plotly_chart(fig_abandono_diaria, use_container_width=True)
    st.plotly_chart(fig_resolucao_diaria, use_container_width=True)
    st.plotly_chart(fig_resolucao_por_atendente, use_container_width=True)

# Navegação entre as páginas
def dashboard_page():
    df = pd.read_excel('Relatório de Ligações Jan25.xlsx')
    calls_data = pd.read_excel('Relatório de Ligações Jan25.xlsx', sheet_name='Calls')
    calls_data['CallLocalTime'] = pd.to_datetime(calls_data['CallLocalTime'], errors='coerce')

    with st.sidebar:
        opcao = st.radio("Navegação", ["Valores Gerais", "Valores por Dia"])

    if opcao == "Valores Gerais":
        valores_gerais(df, calls_data)
    elif opcao == "Valores por Dia":
        valores_por_dia(df, calls_data)


# Função para extrair o produto solicitado do texto
def extrair_produto(texto):
    """
    Extrai o nome completo do produto solicitado de um texto.

    Exemplo:
    - Entrada: "Cliente realizou pesquisa para comprar - Produto: Aspirador de Pó Vertical"
    - Saída: "Aspirador de Pó Vertical"

    :param texto: String contendo o produto mencionado
    :return: Nome completo do produto ou None se não encontrado
    """
    if pd.isnull(texto) or not isinstance(texto, str):
        return None
    
    # 1️⃣ Tenta extrair tudo após "Produto:"
    padrao = re.search(r"(?i)produto[:\-]\s*(.*)", texto)
    if padrao:
        return padrao.group(1).strip()  # Retorna tudo após "Produto:"

    # 2️⃣ Se não encontrar "Produto:", tenta pegar o último segmento separado por "- "
    if " - " in texto:
        return texto.split(" - ")[-1].strip()

    # 3️⃣ Como último recurso, retorna o próprio texto completo (evita perda de dados)
    return texto.strip()

# Função para gerar o gráfico de frequência de palavras com Plotly Express
def gerar_frequencia_produtos(data, coluna_texto, titulo="Mapa de Frequência dos Produtos Solicitados"):
    """
    Gera um gráfico Treemap com a frequência dos produtos solicitados.
    """
    # Extrai os produtos da coluna
    data["ProdutoSolicitado"] = data[coluna_texto].apply(extrair_produto)

    # Conta a frequência dos produtos
    frequencia = data["ProdutoSolicitado"].value_counts().reset_index()
    frequencia.columns = ["Produto", "Frequência"]

    fig = px.treemap(
        frequencia.head(15),  # Mostra os 15 produtos mais solicitados
        path=["Produto"],      # Hierarquia do treemap (apenas um nível neste caso)
        values="Frequência",
        title=titulo,
        color="Frequência",    # A cor será baseada na frequência
        color_continuous_scale="RdBu"  # Paleta de cores (pode ser alterada)
    )

    # Exibir no Streamlit
    st.title("Solicitações Mais Frequentes")
    st.plotly_chart(fig)

    return fig

# Função para gerar o mapa de bolhas
def gerar_mapa_bolhas(df):
    """Gera um mapa scatter geo no formato de bolhas baseado nos DDDs extraídos da coluna 'ANI'."""

    st.subheader("📍 Mapa de Ligações por Estado")

    # 1️⃣ **Verificar se a coluna ANI existe**
    if "ANI" not in df.columns:
        st.error("❌ A coluna 'ANI' não foi encontrada nos dados.")
        return


    # 3️⃣ **Limpeza e extração do DDD**
    df["ANI"] = df["ANI"].astype(str).str.replace(r'\D', '', regex=True)  # Remove qualquer caractere não numérico
    df["DDD"] = df["ANI"].apply(extrair_ddd)


    # 5️⃣ **Mapear os estados a partir dos DDDs**
    df["Estado"] = df["DDD"].map(mapa_ddd_estado)


    # 7️⃣ **Remover valores nulos nos estados**
    df = df.dropna(subset=["Estado"])

    # 8️⃣ **Contar ligações por estado**
    df_estado = df["Estado"].value_counts().reset_index()
    df_estado.columns = ["Estado", "Quantidade"]

    # 9️⃣ **Adicionar latitude e longitude**
    df_estado["Latitude"] = df_estado["Estado"].map(lambda x: estado_coordenadas.get(x, [None, None])[0])
    df_estado["Longitude"] = df_estado["Estado"].map(lambda x: estado_coordenadas.get(x, [None, None])[1])

    # 1️⃣1️⃣ **Remover valores nulos em latitude e longitude**
    df_estado = df_estado.dropna(subset=["Latitude", "Longitude"])

    # 1️⃣2️⃣ **Verificar se há dados suficientes para o mapa**
    if df_estado.empty:
        st.warning("⚠ Nenhum dado disponível para gerar o mapa.")
        return

    # 1️⃣3️⃣ **Criar o mapa**
    fig = px.scatter_geo(
        df_estado,
        lat="Latitude",
        lon="Longitude",
        size="Quantidade",
        hover_name="Estado",
        title="Distribuição de Ligações por Estado",
        projection="natural earth",
        template="plotly_dark",
        color="Quantidade",
        color_continuous_scale="Blues"
    )

    # 1️⃣4️⃣ **Exibir o mapa**
    st.plotly_chart(fig, use_container_width=True)

# Dicionário de DDDs para estados
mapa_ddd_estado = {
    "11": "SP", "12": "SP", "13": "SP", "14": "SP", "15": "SP", "16": "SP", "17": "SP", "18": "SP", "19": "SP",
    "21": "RJ", "22": "RJ", "24": "RJ",
    "27": "ES", "28": "ES",
    "31": "MG", "32": "MG", "33": "MG", "34": "MG", "35": "MG", "37": "MG", "38": "MG",
    "41": "PR", "42": "PR", "43": "PR", "44": "PR", "45": "PR", "46": "PR",
    "47": "SC", "48": "SC", "49": "SC",
    "51": "RS", "53": "RS", "54": "RS", "55": "RS",
    "61": "DF",
    "62": "GO", "64": "GO",
    "63": "TO",
    "65": "MT", "66": "MT",
    "67": "MS",
    "68": "AC",
    "69": "RO",
    "71": "BA", "73": "BA", "74": "BA", "75": "BA", "77": "BA",
    "79": "SE",
    "81": "PE", "87": "PE",
    "82": "AL",
    "83": "PB",
    "84": "RN",
    "85": "CE", "88": "CE",
    "86": "PI", "89": "PI",
    "91": "PA", "93": "PA", "94": "PA",
    "92": "AM", "97": "AM",
    "95": "RR",
    "96": "AP",
    "98": "MA", "99": "MA"
}

# 📌 Dicionário de coordenadas dos estados
estado_coordenadas = {
    "AC": [-9.02, -70.81], "AL": [-9.57, -36.78], "AP": [1.41, -51.77], "AM": [-3.07, -60.02], "BA": [-12.97, -38.51],
    "CE": [-3.73, -38.52], "DF": [-15.83, -47.86], "ES": [-20.32, -40.34], "GO": [-16.68, -49.25], "MA": [-2.53, -44.30],
    "MT": [-12.64, -55.42], "MS": [-20.44, -54.65], "MG": [-18.10, -44.38], "PA": [-1.45, -48.50], "PB": [-7.12, -34.88],
    "PR": [-25.42, -49.27], "PE": [-8.05, -34.88], "PI": [-5.09, -42.80], "RJ": [-22.91, -43.17], "RN": [-5.81, -35.21],
    "RS": [-30.01, -51.22], "RO": [-8.76, -63.90], "RR": [2.82, -60.67], "SC": [-27.59, -48.55], "SP": [-23.55, -46.63],
    "SE": [-10.91, -37.07], "TO": [-10.25, -48.32]
}

# 📌 Função para extrair DDD do número de telefone
def extrair_ddd(ani):
    """Extrai os dois primeiros dígitos do número de telefone como DDD."""
    if pd.isnull(ani) or not isinstance(ani, str):
        return None
    ani = ani.strip()
    match = re.match(r"^(\d{2})", ani)  # Captura os dois primeiros números (DDD)
    return match.group(1) if match else None

# 📌 Função para gerar o mapa de bolhas
def gerar_mapa_bolhas(df):
    """Gera um mapa scatter geo no formato de bolhas baseado nos DDDs extraídos da coluna 'ANI'."""

    st.subheader("📍 Mapa de Ligações por Estado")

    # 1️⃣ **Verificar se a coluna ANI existe**
    if "ANI" not in df.columns:
        st.error("❌ A coluna 'ANI' não foi encontrada nos dados.")
        return

    # 3️⃣ **Limpeza e extração do DDD**
    # Remover qualquer valor não numérico ou espaços extras na coluna ANI
    df["ANI"] = df["ANI"].astype(str).str.replace(r'\D', '', regex=True)  # Remove qualquer caractere não numérico
    df["DDD"] = df["ANI"].apply(extrair_ddd)


    # 5️⃣ **Mapear os estados a partir dos DDDs**
    df["Estado"] = df["DDD"].map(mapa_ddd_estado)


    # 7️⃣ **Remover valores nulos nos estados**
    df = df.dropna(subset=["Estado"])

    # 8️⃣ **Contar ligações por estado**
    df_estado = df["Estado"].value_counts().reset_index()
    df_estado.columns = ["Estado", "Quantidade"]

    # 9️⃣ **Adicionar latitude e longitude**
    df_estado["Latitude"] = df_estado["Estado"].map(lambda x: estado_coordenadas.get(x, [None, None])[0])
    df_estado["Longitude"] = df_estado["Estado"].map(lambda x: estado_coordenadas.get(x, [None, None])[1])


    # 1️⃣1️⃣ **Remover valores nulos em latitude e longitude**
    df_estado = df_estado.dropna(subset=["Latitude", "Longitude"])

    # 1️⃣2️⃣ **Verificar se há dados suficientes para o mapa**
    if df_estado.empty:
        st.warning("⚠ Nenhum dado disponível para gerar o mapa.")
        return

    # 1️⃣3️⃣ **Criar o mapa**
    fig1 = px.scatter_geo(
        df_estado,
        lat="Latitude",
        lon="Longitude",
        size="Quantidade",
        hover_name="Estado",
        title="Distribuição de Ligações por Estado",
        projection="natural earth",
        template="plotly_dark",
        color="Quantidade",
        color_continuous_scale="Blues"
    )


    # 1️⃣4️⃣ **Exibir o mapa**
    st.plotly_chart(fig1, use_container_width=True)

def dashboard_produtos(df):
    """
    Dashboard para exibir o gráfico de frequência dos produtos solicitados e o mapa de bolhas.
    Ambos os gráficos serão exibidos no mesmo local.
    """
    st.title("Análise de Produtos Solicitados e Mapa de Ligações")

    # Filtro de datas
    min_date = df['CallLocalTime'].min().date()
    max_date = df['CallLocalTime'].max().date()
    start_date = st.sidebar.date_input("Data inicial", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Data final", max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("A data inicial não pode ser maior que a data final.")
        return

    # Filtra os dados com base no intervalo de datas
    filtered_data = df[(df['CallLocalTime'].dt.date >= start_date) & (df['CallLocalTime'].dt.date <= end_date)]

    # Verifica se a coluna Memo existe
    if 'Memo' not in filtered_data.columns:
        st.warning("A coluna 'Memo' não foi encontrada nos dados.")
        return

    # Condição para exibir o gráfico de Treemap ou Mapa de Bolhas
    # Verifique se os dados de 'Memo' estão disponíveis para gerar o Treemap
    if 'Memo' in filtered_data.columns:
        # Gerar e exibir o Treemap de Produtos
        fig = gerar_frequencia_produtos(filtered_data, 'Memo', "Produtos Solicitados pelos Clientes")
    
    # Sempre que precisar do gráfico do Mapa de Bolhas, ele será gerado na sequência
    gerar_mapa_bolhas(filtered_data)  # Exibe o gráfico de Mapa de Bolhas

def carregar_dados():
    try:
        df = pd.read_excel("Relatório de Ligações Jan25.xlsx", sheet_name="Calls")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None


def analise_acoes():
    # Load data
    file_path = 'Relatório de Ligações Jan25.xlsx'
    data = pd.ExcelFile(file_path)
    actions_data = data.parse('Actions')

    # Data Preprocessing
    actions_data['Duration_minutes'] = (actions_data['Duration'] * 0.01 / 60).astype(int)
    actions_data['Descrição estados'] = actions_data['Descrição estados'].fillna('Nulo')
    actions_data['Date'] = pd.to_datetime(actions_data['ActionLocalTime']).dt.date

    # Sidebar - Select Attendants
    st.sidebar.title("Filtros")
    attendants = actions_data['Nome Agente'].unique()
    selected_attendants = st.sidebar.multiselect("Selecione os atendentes", attendants, default=attendants)

    # Sidebar - Select Date Range
    start_date = st.sidebar.date_input("Data Inicial", value=pd.to_datetime(actions_data['Date']).min())
    end_date = st.sidebar.date_input("Data Final", value=pd.to_datetime(actions_data['Date']).max())

    if start_date > end_date:
        st.error("A data inicial não pode ser maior que a data final.")
        return

    # Filter data by selected attendants and date range
    filtered_data = actions_data[(actions_data['Nome Agente'].isin(selected_attendants)) &
                                  (actions_data['Date'] >= start_date) &
                                  (actions_data['Date'] <= end_date)]

    # Remove rows with 'Nulo' in 'Descrição estados'
    filtered_data = filtered_data[filtered_data['Descrição estados'] != 'Nulo']

    st.title("Análise de Duração por Ação e Atendente")
 
  

    # Group data for overall averages
    overall_avg = filtered_data.groupby(['Descrição estados', 'Nome Agente'])['Duration_minutes'].mean().reset_index()
    overall_avg = overall_avg.rename(columns={"Duration_minutes": "Tempo Médio (min)"})

    # Display average duration by action and attendant
    for action in overall_avg['Descrição estados'].unique():
        st.subheader(f"Ação: {action}")
        action_data = overall_avg[overall_avg['Descrição estados'] == action]
        action_data['Tempo Médio (min)'] = action_data['Tempo Médio (min)'].astype(int)  # Ensure integer values for labels
        fig = px.bar(
            action_data, x='Nome Agente', y='Tempo Médio (min)',
            title=f"Tempo Médio por Atendente - Ação: {action}",
            labels={"Nome Agente": "Atendente", "Tempo Médio (min)": "Tempo Médio (min)"},
            text='Tempo Médio (min)',
            color_discrete_sequence=['#7cdaf9']
        )
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')  # Show only integer values

        st.plotly_chart(fig, use_container_width=True)

    # Group data for daily averages
    daily_avg = filtered_data.groupby(['Date', 'Descrição estados'])['Duration_minutes'].mean().reset_index()
    daily_avg = daily_avg.rename(columns={"Duration_minutes": "Tempo Médio Diário (min)"})

    st.title("Análise de Duração Diária por Ação")

    # Display daily average duration by action
    for action in daily_avg['Descrição estados'].unique():
        st.subheader(f"Ação: {action}")
        action_daily_data = daily_avg[daily_avg['Descrição estados'] == action]
        action_daily_data['Tempo Médio Diário (min)'] = action_daily_data['Tempo Médio Diário (min)'].astype(int)  # Ensure integer values for labels
        fig_daily = px.bar(
            action_daily_data, x='Date', y='Tempo Médio Diário (min)',
            title=f"Tempo Médio Diário - Ação: {action}",
            labels={"Date": "Data", "Tempo Médio Diário (min)": "Tempo Médio Diário (min)"},
            text='Tempo Médio Diário (min)',
            color_discrete_sequence=['#FFD700']
        )
        fig_daily.update_traces(texttemplate='%{text:.0f}', textposition='outside')  # Show only integer values

# Página do Dashboard
def dashboard_page():
    # Verifique se os arquivos de dados estão disponíveis
    try:
        df = pd.read_excel('Relatório de Ligações Jan25.xlsx')
        calls_data = pd.read_excel('Relatório de Ligações Jan25.xlsx', sheet_name='Calls')
        calls_data['CallLocalTime'] = pd.to_datetime(calls_data['CallLocalTime'], errors='coerce')
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return

    # Adiciona a navegação na barra lateral
    with st.sidebar:
        opcao = st.radio("Navegação", ["Valores Gerais", "Valores por Dia", "Frequência de Produtos", "Análise de Ações"])

    # Navega entre as páginas
    if opcao == "Valores Gerais":
        valores_gerais(df, calls_data)
    elif opcao == "Valores por Dia":
        valores_por_dia(df, calls_data)
    elif opcao == "Frequência de Produtos":
        dashboard_produtos(calls_data)
    elif opcao == "Análise de Ações":
        analise_acoes()

# Navegação
if st.session_state.current_page == "login" and not st.session_state.authenticated:
    login_page()
elif st.session_state.current_page == "dashboard" and st.session_state.authenticated:
    dashboard_page()
else:
    st.warning("Você não está autenticado. Redirecionando para a página de login...")
    st.session_state.current_page = "login"
    st.stop()
