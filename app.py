import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Conflitos no Brasil", layout="wide")

st.title("📊 Análise de Conflitos no Brasil")

# Carregar os dados
df = pd.read_csv("brazil_conflicts_dataset.csv")

# Converter datas corretamente
df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce")
df["date_end"] = pd.to_datetime(df["date_end"], errors="coerce")

# Remover linhas sem latitude ou longitude
df = df.dropna(subset=["latitude", "longitude"])

# Seletor de anos
anos_disponiveis = sorted(df["year"].dropna().unique())
ano_selecionado = st.sidebar.selectbox("Selecionar ano:", anos_disponiveis)

df_filtrado = df[df["year"] == ano_selecionado]

# Mostrar métricas
st.subheader(f"Resultados para {ano_selecionado}")

col1, col2, col3 = st.columns(3)
col1.metric("Total de ocorrências", len(df_filtrado))
col2.metric("Mortes", int(df_filtrado["fatalities"].sum()))
col3.metric("Feridos", int(df_filtrado["injuries"].sum()))

# Gráfico de barras
st.subheader("Número de conflitos por tipo")

if "type" in df_filtrado.columns:
    conflitos_tipo = df_filtrado["type"].value_counts().reset_index()
    conflitos_tipo.columns = ["tipo", "ocorrencias"]

    fig_bar = px.bar(
        conflitos_tipo,
        x="tipo",
        y="ocorrencias",
        title="Conflitos por tipo",
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.error("A coluna 'type' não existe no dataset.")

# Mapa
st.subheader("Mapa das ocorrências")

fig_map = px.scatter_mapbox(
    df_filtrado,
    lat="latitude",
    lon="longitude",
    color="fatalities",
    size="fatalities",
    hover_name="location",
    zoom=3,
    height=600,
)

fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
