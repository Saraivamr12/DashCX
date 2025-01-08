from wordcloud import WordCloud
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
    "user2": "12345"
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

    st.markdown(
        """
        <style>

        .stRadio > div > label{
            color: white !important;
        }

        [data-baseweb="radio"] > label {
            color: white !important;
        }

        .custom-box {
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #FFD700;
            text-align: center;
            font-family: 'Arial', sans-serif;
            width: 200px;
            height: 120px;
        }

        .custom-box strong {
            font-size: 18px;
            color: #ffffff;
        }

        .custom-box span {
            font-size: 30px;
            color: #FFD700;
        }

        .flex-container {
            display: flex;
            justify-content: space-evenly;
            gap: 10px;
            margin-bottom: 20px;
        }
        /* Fundo preto para toda a aplicação */
        .stApp {
            background-color: #1e1e1e;  /* Preto escuro */
            color: #ffffff;  /* Texto branco */
        }

        /* Fundo e estilo da sidebar */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;  /* Cinza escuro */
            color: #ffffff;  /* Texto branco */
            border-right: 3px solid #FFD700; /* Linha divisória amarela */
        }

        /* Espaçamento e padding da sidebar */
        [data-testid="stSidebar"] 
        .block-container {
            padding: 20px;
        }

        /* Botões da sidebar */
        [data-testid="stSidebar"] button {
            background-color: #1e1e1e; /* Azul */
            color: #ffffff;  /* Texto branco */
            border: 1px, solid, #FFD700;
            border-radius: 5px;
        }

        /* Links na sidebar */
        [data-testid="stSidebar"] a {
            color: #ffffff;  /* Branco */
            text-decoration: none;
        }

        /* Linha horizontal personalizada */
        hr {
            border: none;
            border-right: 1px solid #FFD700; /* Linha amarela */
            margin: 20px 0;
        }

        /* Títulos principais */
        h1, h2, h3 {
            color: #FFD700;  /* Amarelo ouro */
        }

        </style>
        """,
    unsafe_allow_html=True
)

    # Resumo Geral
    st.markdown(
        """
        <div class="flex-container">
            <div class="custom-box">
                <strong>Total de Chamadas:</strong><br><span>7.448</span>
            </div>
            <div class="custom-box">
                <strong>Duração Média por Chamada:</strong><br><span>3 minutos</span>
            </div>
            <div class="custom-box">
                <strong>Taxa de Abandono:</strong><br><span>2,88%</span>
            </div>
            <div class="custom-box">
                <strong>Notas de Atendimento:</strong><br><span>692</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("---")

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
        chamadas_abandonadas = data[data["EndReason"] < 0].shape[0]
        chamadas_concluidas = total_chamadas - chamadas_abandonadas
        return [chamadas_abandonadas, chamadas_concluidas]

    def calcular_taxa_resolucao(data):
        chamadas_com_nota = data[data["NotaAtendimento"].notnull()]
        total_chamadas_com_nota = len(chamadas_com_nota)
        chamadas_resolvidas = chamadas_com_nota[chamadas_com_nota["NotaAtendimento"] >= 4].shape[0]
        chamadas_nao_resolvidas = total_chamadas_com_nota - chamadas_resolvidas
        return [chamadas_resolvidas, chamadas_nao_resolvidas]

    # Volume de Atendimentos por Hora
    calls_per_hour = calcular_volume_atendimentos(calls_data)
    fig1 = px.line(
        x=calls_per_hour.index,
        y=calls_per_hour.values,
        title="Volume de Atendimentos por Hora",
        labels={"x": "Horário", "y": "Quantidade de Atendimentos"},
        markers=True
    )
    fig1.update_traces(line=dict(color="#FFD700", width=5), marker=dict(size=10, color="gray", symbol="circle"))
    fig1.update_layout(
        title_font=(dict(color="white", size=22)),
        plot_bgcolor="#1e1e1e", 
        paper_bgcolor="#1e1e1e", 
        font=dict(color="black"),
        xaxis=dict(title=dict(font=dict(color="white", size=16))),
        yaxis=dict(title=dict(font=dict(color="white", size=16)))
    ) 

    # Frequência de Notas
    frequencia_notas = calcular_frequencia_notas(calls_data)
    fig2 = px.bar(
        x=frequencia_notas.index,
        y=frequencia_notas.values,
        title="Taxa de Satisfação do Cliente",
        labels={"x": "Notas de Atendimento", "y": "Avaliações"},
        text=frequencia_notas.values,
        color_discrete_sequence=["#FFD700", "#1e1e1e"]
    )
    fig2.update_traces(texttemplate="%{text}", textposition="outside")
    fig2.update_layout(
        title_font=(dict(color="white", size=22)),
        plot_bgcolor="#1e1e1e", 
        paper_bgcolor="#1e1e1e", 
        font=dict(color="white"),
        xaxis=dict(title=dict(font=dict(color="white", size=16))),
        yaxis=dict(title=dict(font=dict(color="white", size=16)))
    )

    # Taxa de Abandono e Resolução
    sizes_abandono = calcular_taxa_abandono(calls_data)
    sizes_resolucao = calcular_taxa_resolucao(calls_data)

    fig3 = go.Figure(
        data=[go.Pie(
            labels=["Abandonadas", "Concluídas"],
            values=sizes_abandono,
            hole=0.4,
            textinfo="percent+label",
            marker=dict(colors=["#5f5f5f", "#FFD700"], line=dict(color="white", width=1))
        )]
    )
    fig3.update_layout(
        title="Taxa de Abandono", 
        title_font=dict(color="white", size=22),
        paper_bgcolor="#1e1e1e", 
        font=dict(color="white"),
        legend=dict(
            font=dict(color="white")
        )

    )

    fig4 = go.Figure(
        data=[go.Pie(
            labels=["Resolvidas", "Não Resolvidas"],
            values=sizes_resolucao,
            hole=0.4,
            textinfo="percent+label",
            marker=dict(colors=["#FFD700", "#5F5F5F"], line=dict(color="white", width=1))
        )]
    )
    fig4.update_layout(
        title="Taxa de Resolução", 
        title_font=dict(color="white", size=22),
        paper_bgcolor="#1e1e1e", 
        font=dict(color="white"),
        legend=dict(
            font=dict(color="white")
        )
        
        
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

    st.markdown(
        """
        <style>
        .stRadio > div > label {
            color: white !important;
        }

        [data-baseweb="radio"] > label {
            color: white !important;
        }

        .custom-box {
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #FFD700;
            text-align: center;
            font-family: 'Arial', sans-serif;
            width: 200px;
            height: 120px;
        }

        .custom-box strong {
            font-size: 18px;
            color: #ffffff;
        }

        .custom-box span {
            font-size: 30px;
            color: #FFD700;
        }

        .flex-container {
            display: flex;
            justify-content: space-evenly;
            gap: 10px;
            margin-bottom: 20px;
        }

        /* Fundo preto para toda a aplicação */
        .stApp {
            background-color: #1e1e1e;  /* Preto escuro */
            color: #ffffff;  /* Texto branco */
        }

        /* Fundo e estilo da sidebar */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;  /* Cinza escuro */
            color: #ffffff;  /* Texto branco */
            border-right: 3px solid #FFD700; /* Linha divisória amarela */
        }

        /* Espaçamento e padding da sidebar */
        [data-testid="stSidebar"] .block-container {
            padding: 20px;
        }

        /* Botões da sidebar */
        [data-testid="stSidebar"] button {
            background-color: #1e1e1e; /* Azul */
            color: #ffffff;  /* Texto branco */
            border: 1px solid #FFD700;
            border-radius: 5px;
        }

        /* Links na sidebar */
        [data-testid="stSidebar"] a {
            color: #ffffff;  /* Branco */
            text-decoration: none;
        }

        /* Linha horizontal personalizada */
        hr {
            border: none;
            border-right: 1px solid #FFD700; /* Linha amarela */
            margin: 20px 0;
        }

        /* Títulos principais */
        h1, h2, h3 {
            color: #FFD700;  /* Amarelo ouro */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Filtro de datas
    def calcular_taxa_abandono_diaria(data):
        chamadas_por_dia = data.groupby(data['CallLocalTime'].dt.date)
        resultados = []
        for dia, chamadas in chamadas_por_dia:
            total_chamadas = len(chamadas)
            chamadas_abandonadas = chamadas[chamadas["EndReason"] < 0].shape[0]
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
        for atendente in data["Nome Atendente"].unique():
            dados_atendente = data[data["Nome Atendente"] == atendente]

            total_chamadas = len(dados_atendente)
            chamadas_abandonadas = len(dados_atendente[dados_atendente["EndReason"] < 0])
            taxa_abandono = (chamadas_abandonadas / total_chamadas) * 100 if total_chamadas > 0 else 0

            chamadas_com_nota = dados_atendente[dados_atendente["NotaAtendimento"].notnull()]
            total_chamadas_com_nota = len(chamadas_com_nota)
            chamadas_resolvidas = len(chamadas_com_nota[chamadas_com_nota["NotaAtendimento"] >= 4])
            taxa_resolucao = (chamadas_resolvidas / total_chamadas_com_nota) * 100 if total_chamadas_com_nota > 0 else 0

            resultados.append({
                "Nome Atendente": atendente,
                "Taxa de Abandono (%)": taxa_abandono,
                "Taxa de Resolução (%)": taxa_resolucao
            })
        return pd.DataFrame(resultados)

    # Carregar os dados diretamente da planilha base
    @st.cache_data
    def carregar_dados():
        data = pd.read_excel("Cópia de Cópia de Relatorio wap 2025_12.xlsx")
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
    fig_abandono_diaria.update_layout(
        title_font=dict(color="white"),
        paper_bgcolor="#1e1e1e", 
        font=dict(color="white"),
        plot_bgcolor="#1e1e1e",
        legend=dict(font=dict(color="white"))
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
    fig_resolucao_diaria.update_layout(
        title_font=dict(color="white"),
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        plot_bgcolor="#1e1e1e",
        legend=dict(font=dict(color="white"))
    )

    # Gráficos por atendente
    fig_abandono_por_atendente = px.bar(
        taxas_por_atendente,
        x="Nome Atendente",
        y="Taxa de Abandono (%)",
        title="Taxa de Abandono por Atendente",
        text="Taxa de Abandono (%)",
        color_discrete_sequence=['#FFD700', '696969']
    )
    fig_abandono_por_atendente.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig_abandono_por_atendente.update_layout(
        title_font=dict(color="white"),
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        plot_bgcolor="#1e1e1e",
        legend=dict(font=dict(color="white")),
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
    fig_resolucao_por_atendente.update_layout(
        title_font=dict(color="white"),
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        plot_bgcolor="#1e1e1e",
        legend=dict(font=dict(color="white"))
    )
    # Exibição dos gráficos
    st.plotly_chart(fig_abandono_diaria, use_container_width=True)
    st.plotly_chart(fig_resolucao_diaria, use_container_width=True)
    st.plotly_chart(fig_abandono_por_atendente, use_container_width=True)
    st.plotly_chart(fig_resolucao_por_atendente, use_container_width=True)

# Navegação entre as páginas
def dashboard_page():
    df = pd.read_excel('Cópia de Cópia de Relatorio wap 2025_12.xlsx')
    calls_data = pd.read_excel('Cópia de Cópia de Relatorio wap 2025_12.xlsx', sheet_name='Calls')
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
    Extrai o último trecho do texto que representa o produto solicitado.
    Exemplo: "Cliente realizou pesquisa para comprar - Produto: Aspirador"
    Retorna: "Aspirador"
    """
    if pd.isnull(texto):
        return None
    # Busca a parte final após um marcador ou padrão específico (ajustar conforme necessário)
    if "Produto:" in texto:
        return texto.split("Produto:")[-1].strip()
    else:
        return texto.split()[-1]  # Retorna a última palavra como fallback

# Função para gerar o gráfico de frequência de palavras com Plotly Express
def gerar_frequencia_produtos(data, coluna_texto, titulo="Frequência dos Produtos Solicitados"):
    """
    Gera um gráfico de barras com a frequência dos produtos solicitados.

    :param data: DataFrame com os dados
    :param coluna_texto: Nome da coluna contendo os textos para análise
    :param titulo: Título do gráfico
    """
    # Extrai os produtos da coluna
    data["ProdutoSolicitado"] = data[coluna_texto].apply(extrair_produto)

    # Conta a frequência dos produtos
    frequencia = data["ProdutoSolicitado"].value_counts().reset_index()
    frequencia.columns = ["Produto", "Frequência"]

    # Gera o gráfico de barras
    fig = px.bar(
        frequencia.head(15),  # Mostra os 15 produtos mais solicitados
        x="Frequência",
        y="Produto",
        title=titulo,
        text="Frequência",
        orientation="h",  # Barras horizontais
        labels={"Frequência": "Quantidade", "Produto": "Produto"}
    )
    fig.update_traces(marker_color="#FFD700", textposition="outside")
    fig.update_layout(
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        xaxis=dict(gridcolor="lightgrey"),
        yaxis=dict(gridcolor="lightgrey")
    )

    # Retorna o gráfico
    return fig

# Adiciona o gráfico ao dashboard
def dashboard_frequencia_produtos(df):
    """
    Dashboard para exibir o gráfico de frequência dos produtos solicitados.
    """
    st.title("Análise de Produtos Solicitados")

    st.markdown(
        """
        <style>
        .stRadio > div > label {
            color: white !important;
        }

        [data-baseweb="radio"] > label {
            color: white !important;
        }

        .custom-box {
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #FFD700;
            text-align: center;
            font-family: 'Arial', sans-serif;
            width: 200px;
            height: 120px;
        }

        .custom-box strong {
            font-size: 18px;
            color: #ffffff;
        }

        .custom-box span {
            font-size: 30px;
            color: #FFD700;
        }

        .flex-container {
            display: flex;
            justify-content: space-evenly;
            gap: 10px;
            margin-bottom: 20px;
        }

        /* Fundo preto para toda a aplicação */
        .stApp {
            background-color: #1e1e1e;  /* Preto escuro */
            color: #ffffff;  /* Texto branco */
        }

        /* Fundo e estilo da sidebar */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;  /* Cinza escuro */
            color: #ffffff;  /* Texto branco */
            border-right: 3px solid #FFD700; /* Linha divisória amarela */
        }

        /* Espaçamento e padding da sidebar */
        [data-testid="stSidebar"] .block-container {
            padding: 20px;
        }

        /* Botões da sidebar */
        [data-testid="stSidebar"] button {
            background-color: #1e1e1e; /* Azul */
            color: #ffffff;  /* Texto branco */
            border: 1px solid #FFD700;
            border-radius: 5px;
        }

        /* Links na sidebar */
        [data-testid="stSidebar"] a {
            color: #ffffff;  /* Branco */
            text-decoration: none;
        }

        /* Linha horizontal personalizada */
        hr {
            border: none;
            border-right: 1px solid #FFD700; /* Linha amarela */
            margin: 20px 0;
        }

        /* Títulos principais */
        h1, h2, h3 {
            color: #FFD700;  /* Amarelo ouro */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Filtro de datas
    min_date = df['CallLocalTime'].min().date()
    max_date = df['CallLocalTime'].max().date()
    start_date = st.sidebar.date_input("Data inicial", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Data final", max_date, min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.error("A data inicial não pode ser maior que a data final.")
        st.stop()
    # Filtra os dados com base no intervalo de datas
    filtered_data = df[(df['CallLocalTime'].dt.date >= start_date) &
                       (df['CallLocalTime'].dt.date <= end_date)]
    
    adicionar_logout()

    # Verifica se a coluna Memo existe
    if 'Memo' not in filtered_data.columns:
        st.warning("A coluna 'Memo' não foi encontrada nos dados.")
        st.stop()

    # Gera o gráfico de frequência dos produtos solicitados
    fig = gerar_frequencia_produtos(filtered_data, 'Memo', "Produtos Solicitados pelos Clientes")

    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)

def analise_acoes():
    # Load data
    file_path = 'Cópia de Cópia de Relatorio wap 2025_12.xlsx'
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
    st.markdown(
        """
        <style>
        .stRadio > div > label {
            color: white !important;
        }

        [data-baseweb="radio"] > label {
            color: white !important;
        }

        .custom-box {
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #FFD700;
            text-align: center;
            font-family: 'Arial', sans-serif;
            width: 200px;
            height: 120px;
        }

        .custom-box strong {
            font-size: 18px;
            color: #ffffff;
        }

        .custom-box span {
            font-size: 30px;
            color: #FFD700;
        }

        .flex-container {
            display: flex;
            justify-content: space-evenly;
            gap: 10px;
            margin-bottom: 20px;
        }

        /* Fundo preto para toda a aplicação */
        .stApp {
            background-color: #1e1e1e;  /* Preto escuro */
            color: #ffffff;  /* Texto branco */
        }

        /* Fundo e estilo da sidebar */
        [data-testid="stSidebar"] {
            background-color: #1e1e1e;  /* Cinza escuro */
            color: #ffffff;  /* Texto branco */
            border-right: 3px solid #FFD700; /* Linha divisória amarela */
        }

        /* Espaçamento e padding da sidebar */
        [data-testid="stSidebar"] .block-container {
            padding: 20px;
        }

        /* Botões da sidebar */
        [data-testid="stSidebar"] button {
            background-color: #1e1e1e; /* Azul */
            color: #ffffff;  /* Texto branco */
            border: 1px solid #FFD700;
            border-radius: 5px;
        }

        /* Links na sidebar */
        [data-testid="stSidebar"] a {
            color: #ffffff;  /* Branco */
            text-decoration: none;
        }

        /* Linha horizontal personalizada */
        hr {
            border: none;
            border-right: 1px solid #FFD700; /* Linha amarela */
            margin: 20px 0;
        }

        /* Títulos principais */
        h1, h2, h3 {
            color: #FFD700;  /* Amarelo ouro */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
  

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
            color_discrete_sequence=['#FFD700']
        )
        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')  # Show only integer values
        fig.update_layout(
            title_font=dict(size=18),
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#1e1e1e",
            font=dict(size=12),
            xaxis=dict(title=dict(font=dict(color='white', size=14))),
            yaxis=dict(title=dict(font=dict(color='white', size=14)))
        )
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
        fig_daily.update_layout(
            title_font=dict(size=18),
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#1e1e1e",
            font=dict(size=12),
            xaxis=dict(title=dict(font=dict(color='white', size=14))),
            yaxis=dict(title=dict(font=dict(color='white', size=14))))
        st.plotly_chart(fig_daily, use_container_width=True)


# Página do Dashboard
def dashboard_page():
    # Verifique se os arquivos de dados estão disponíveis
    try:
        df = pd.read_excel('Cópia de Cópia de Relatorio wap 2025_12.xlsx')
        calls_data = pd.read_excel('Cópia de Cópia de Relatorio wap 2025_12.xlsx', sheet_name='Calls')
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
        dashboard_frequencia_produtos(calls_data)
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
