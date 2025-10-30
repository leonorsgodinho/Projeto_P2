import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Projeto P2 - BrasilAPI", layout="wide")
st.title("Estatísticas Interativas de Municípios Brasileiros")

# Sidebar - filtro de estado
estados = ["SP", "RJ", "MG", "BA", "RS"]  # podemos expandir depois
estado_selecionado = st.sidebar.selectbox("Escolha um estado", estados)

# Buscar dados da API
url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{estado_selecionado}"
try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data)
except:
    st.error("Não foi possível carregar os dados da API.")
    df = pd.DataFrame()

if not df.empty:
    st.subheader(f"Municípios do estado {estado_selecionado}")
    st.dataframe(df[['nome', 'codigo_ibge', 'microrregiao']])

    st.subheader("Número de municípios por microrregião")
    chart_data = df.groupby('microrregiao').size().reset_index(name='NumeroMunicipios')
    fig = px.bar(chart_data, x='microrregiao', y='NumeroMunicipios', color='microrregiao', text='NumeroMunicipios')
    st.plotly_chart(fig, use_container_width=True)
