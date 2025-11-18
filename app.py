import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

import os
st.write("Ficheiros disponíveis no diretório atual:")
st.write(os.listdir("."))

st.set_page_config(layout="wide", page_title="Análise de Conflitos no Brasil")
sns.set_style("whitegrid")

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, sep=",", engine="python", on_bad_lines="skip")
        
        # Limpeza básica
        df.columns = df.columns.str.strip()

        # Datas
        df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce")

        # Coordenadas
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        # Mortes (best_est)
        df["best_est"] = pd.to_numeric(df["best_est"], errors="coerce")

        # Remove linhas essenciais nulas
        df = df.dropna(subset=["date_start", "latitude", "longitude"])

        # Criação da coluna mês-ano
        df["month_year"] = df["date_start"].dt.to_period("M")

        return df

    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None


df = load_data("brazil_conflicts_dataset.csv")

# --- DEBUG: VERIFICAR O CONTEÚDO DO CSV ---
st.subheader("DEBUG - Primeiras linhas do CSV")
st.write("Colunas:", df.columns.tolist())
st.write(df.head(10))
# -------------------------------------------

if df is not None:

    st.title("Dashboard: Conflitos Armados no Brasil")

    # KPIs gerais
    total_eventos = len(df)
    total_mortes = int(df["best_est"].sum())

    col1, col2 = st.columns(2)
    col1.metric("Total de Eventos", f"{total_eventos:,}")
    col2.metric("Total de Mortes (best_est)", f"{total_mortes:,}")

    # --------------------------
    # GRÁFICOS TEMPORAIS
    # --------------------------

    st.header("Análise Temporal")

    eventos_mes = df.groupby("month_year").size().reset_index(name="total_eventos")
    eventos_mes["month_year"] = eventos_mes["month_year"].dt.to_timestamp()

    mortes_mes = df.groupby("month_year")["best_est"].sum().reset_index(name="total_mortes")
    mortes_mes["month_year"] = mortes_mes["month_year"].dt.to_timestamp()

    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        st.subheader("Eventos por Mês")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=eventos_mes, x="month_year", y="total_eventos", ax=ax1)
        ax1.set_xlabel("Data")
        ax1.set_ylabel("Nº de Eventos")
        st.pyplot(fig1)

    with fig_col2:
        st.subheader("Mortes por Mês")
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=mortes_mes, x="month_year", y="total_mortes", ax=ax2)
        ax2.set_xlabel("Data")
        ax2.set_ylabel("Nº de Mortes")
        st.pyplot(fig2)

    # --------------------------
    # MAPA GEOGRÁFICO
    # --------------------------
    st.header("Mapa de Ocorrências no Brasil")

    df_map = df.dropna(subset=["latitude", "longitude"])

    fig_map = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        hover_name="adm_1",
        hover_data={"best_est": True, "date_start": True},
        zoom=3,
        height=600
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0, "t":0, "l":0, "b":0})

    st.plotly_chart(fig_map, use_container_width=True)

    # --------------------------
    # DADOS BRUTOS
    # --------------------------
    if st.checkbox("Mostrar dados brutos"):
        st.dataframe(df)

else:
    st.error("Erro ao carregar os dados.")
