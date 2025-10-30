import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuração da página
st.set_page_config(page_title="Projeto P2 - Municípios Brasileiros", layout="wide")
st.title("📊 Estatísticas Interativas de Municípios do Brasil")

st.sidebar.header("Filtros")

# Lista de estados brasileiros
estados = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA",
    "MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN",
    "RS","RO","RR","SC","SP","SE","TO"
]

# Seleção de estado
estado_selecionado = st.sidebar.selectbox("Escolha um estado", estados)

# Chamada à API
url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{estado_selecionado}"
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    df = pd.json_normalize(data)
except Exception as e:
    st.error(f"Erro ao carregar dados da API: {e}")
    df = pd.DataFrame()

if not df.empty:
    # Criar coluna Microrregiao com valor padrão se faltar
    if "microrregiao" in df.columns:
        df["Microrregiao"] = df["microrregiao"].apply(
            lambda x: x["nome"] if isinstance(x, dict) and "nome" in x else "Desconhecida"
        )
    else:
        df["Microrregiao"] = "Desconhecida"

    # Mostrar tabela
    st.subheader(f"Municípios do estado de {estado_selecionado}")
    colunas_para_mostrar = [col for col in ["nome", "id", "Microrregiao"] if col in df.columns]
    st.dataframe(df[colunas_para_mostrar])

    # Gráfico de barras
    st.subheader("Número de Municípios por Microrregião")
    chart_data = df.groupby("Microrregiao").size().reset_index(name="Número de Municípios")
    fig = px.bar(
        chart_data,
        x="Microrregiao",
        y="Número de Municípios",
        color="Microrregiao",
        text="Número de Municípios"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Não foi possível obter dados para este estado. Tente novamente.")
