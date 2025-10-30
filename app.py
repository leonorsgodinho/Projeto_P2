import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Violência no Brasil", layout="wide")
st.title("Estatísticas de Violência no Brasil")

# Ler CSV
df = pd.read_csv("data/dados_violencia_br.csv", low_memory=False)

# Mostrar colunas disponíveis (para debug, podes remover depois)
st.write("Colunas disponíveis:", df.columns)

# Filtros
estados_disponiveis = df['state'].dropna().unique()
estado_selecionado = st.sidebar.selectbox("Escolha um estado", estados_disponiveis)

anos_disponiveis = sorted(df['year'].dropna().unique())
ano_selecionado = st.sidebar.select_slider("Escolha o ano", options=anos_disponiveis, value=anos_disponiveis[-1])

# Aplicar filtros
df_filtrado = df[(df['state'] == estado_selecionado) & (df['year'] == ano_selecionado)]

# Mostrar tabela
st.subheader(f"Dados de violência em {estado_selecionado} em {ano_selecionado}")
st.dataframe(df_filtrado)

# Gráfico de barras — número de incidentes por tipo de crime
if 'crime_type' in df_filtrado.columns:
    chart_data = df_filtrado.groupby('crime_type')['incidents'].sum().reset_index()
    fig = px.bar(
        chart_data,
        x='crime_type',
        y='incidents',
        color='crime_type',
        text='incidents',
        labels={'crime_type': 'Tipo de Crime', 'incident_
