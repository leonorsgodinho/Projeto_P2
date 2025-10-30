import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Violência Organizada no Brasil", layout="wide")
st.title("📊 Estatísticas de Conflitos Organizados no Brasil")

# Ler CSV
df = pd.read_csv("data/brazil_conflicts_dataset.csv", low_memory=False)

# Mostrar colunas e primeiras linhas para debug
st.write("Colunas disponíveis:", df.columns)
st.write(df.head())

# Filtros
regioes_disponiveis = df['Region'].dropna().unique()
regiao_selecionada = st.sidebar.selectbox("Escolha uma região/estado", regioes_disponiveis)

anos_disponiveis = sorted(df['Year'].dropna().unique())
ano_selecionado = st.sidebar.select_slider(
    "Escolha o ano",
    options=anos_disponiveis,
    value=anos_disponiveis[-1]
)

# Aplicar filtros
df_filtrado = df[(df['Region'] == regiao_selecionada) & (df['Year'] == ano_selecionado)]

# Mostrar tabela filtrada
st.subheader(f"Dados de conflitos em {regiao_selecionada} em {ano_selecionado}")
st.dataframe(df_filtrado)

# Gráfico de barras — número de incidentes por tipo de conflito
if 'Conflict Type' in df_filtrado.columns and 'Deaths' in df_filtrado.columns:
    chart_data = df_filtrado.groupby('Conflict Type')['Deaths'].sum().reset_index()
    fig = px.bar(
        chart_data,
        x='Conflict Type',
        y='Deaths',
        color='Conflict Type',
        text='Deaths',
        labels={'Conflict Type': 'Tipo de Conflito', 'Deaths': 'Número de Mortos'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("As colunas 'Conflict Type' ou 'Deaths' não foram encontradas no dataset.")
