import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Censo Demográfico", layout="wide")

# Nomes padrão das 15 colunas deste dataset
COLUNAS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"
]

@st.cache_data
def carregar_dados():
    # Lê o CSV sem cabeçalho, removendo espaços após a vírgula e tratando '?' como nulo
    df = pd.read_csv(
        "dados.csv",
        names=COLUNAS,
        sep=",",
        skipinitialspace=True,
        na_values="?"
    )
    # Remove linhas incompletas caso existam
    df.dropna(subset=["income"], inplace=True)
    # Preenche nulos categóricos para não perder linhas nos filtros
    df.fillna("Não informado", inplace=True)
    return df

df = carregar_dados()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")

faixa_renda = st.sidebar.multiselect(
    "Faixa de Renda:",
    options=df["income"].unique(),
    default=df["income"].unique()
)

genero = st.sidebar.multiselect(
    "Gênero:",
    options=df["sex"].unique(),
    default=df["sex"].unique()
)

idade_min, idade_max = int(df["age"].min()), int(df["age"].max())
faixa_idade = st.sidebar.slider(
    "Faixa Etária:",
    min_value=idade_min,
    max_value=idade_max,
    value=(idade_min, idade_max)
)

# Aplicando os filtros
df_filtrado = df[
    (df["income"].isin(faixa_renda)) &
    (df["sex"].isin(genero)) &
    (df["age"].between(faixa_idade[0], faixa_idade[1]))
]

# --- CORPO PRINCIPAL ---
st.title("📊 Análise Demográfica e de Renda")
st.markdown("Explore os indicadores de escolaridade, ocupação e horas trabalhadas.")

# Métricas (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Registros", f"{len(df_filtrado):,}")
col2.metric("Idade Média", f"{df_filtrado['age'].mean():.1f} anos")
col3.metric("Horas/Semana (Média)", f"{df_filtrado['hours_per_week'].mean():.1f}h")
pct_maior_50k = (df_filtrado["income"] == ">50K").mean() * 100
col4.metric("Renda > 50K", f"{pct_maior_50k:.1f}%")

st.divider()

# Gráficos - Linha 1
g1, g2 = st.columns(2)

with g1:
    fig_edu = px.histogram(
        df_filtrado,
        x="education",
        color="income",
        barmode="group",
        title="Distribuição de Renda por Escolaridade",
        labels={"education": "Escolaridade", "count": "Quantidade", "income": "Renda"}
    )
    fig_edu.update_xaxes(categoryorder="total descending")
    st.plotly_chart(fig_edu, use_container_width=True)

with g2:
    fig_occ = px.histogram(
        df_filtrado,
        y="occupation",
        color="income",
        barmode="stack",
        title="Renda por Ocupação",
        labels={"occupation": "Ocupação", "count": "Quantidade", "income": "Renda"}
    )
    fig_occ.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig_occ, use_container_width=True)

# Gráficos - Linha 2
g3, g4 = st.columns(2)

with g3:
    fig_age = px.box(
        df_filtrado,
        x="income",
        y="age",
        color="sex",
        title="Distribuição de Idade por Renda e Gênero",
        labels={"income": "Renda", "age": "Idade", "sex": "Gênero"}
    )
    st.plotly_chart(fig_age, use_container_width=True)

with g4:
    fig_work = px.pie(
        df_filtrado,
        names="workclass",
        title="Proporção por Setor de Trabalho",
        hole=0.4
    )
    st.plotly_chart(fig_work, use_container_width=True)

# Tabela de dados brutos (expansível)
with st.expander("Visualizar tabela de dados filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)