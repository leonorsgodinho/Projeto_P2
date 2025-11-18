import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout="wide",
    page_title="Análise de Conflitos no Brasil"
)

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, sep=',', engine='python', on_bad_lines='skip')

    df.columns = df.columns.str.strip()

    df["date_start"] = pd.to_datetime(df["date_start"].astype(str).str.strip(), errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"].astype(str).str.strip(), errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"].astype(str).str.strip(), errors="coerce")
    df["best_est"] = pd.to_numeric(df["best_est"].astype(str).str.strip(), errors="coerce").fillna(0)
    df["adm_1"] = df["adm_1"].astype(str).str.strip()

    df = df.dropna(subset=["date_start", "latitude", "longitude", "adm_1"])

    df["month_year"] = df["date_start"].dt.to_period("M").dt.to_timestamp()

    return df

df = load_data("brazil_conflicts_dataset.csv")

st.sidebar.header("Filtros")

states = sorted(df["adm_1"].unique())

selected_states = st.sidebar.multiselect(
    "Seleciona Estado(s):",
    options=states,
    default=states
)

df_filtered = df[df["adm_1"].isin(selected_states)] if selected_states else df.copy()

total_events = len(df_filtered)
total_deaths = int(df_filtered["best_est"].sum())

st.title("Dashboard: Conflitos no Brasil (1993–2024)")

col1, col2, col3 = st.columns(3)

col1.metric("Estados Selecionados", len(selected_states))
col2.metric("Total de Eventos", f"{total_events:,}")
col3.metric("Total de Mortes Estimadas (best_est)", f"{total_deaths:,}")

st.header("Evolução Temporal")

events_month = df_filtered.groupby("month_year").size().reset_index(name="total_events")

fig_events = px.line(
    events_month,
    x="month_year",
    y="total_events",
    markers=True,
    title="Eventos de Conflito por Mês"
)

st.plotly_chart(fig_events, use_container_width=True)

deaths_month = df_filtered.groupby("month_year")["best_est"].sum().reset_index(name="total_deaths")

fig_deaths = px.line(
    deaths_month,
    x="month_year",
    y="total_deaths",
    markers=True,
    title="Mortes Estimadas por Mês"
)

st.plotly_chart(fig_deaths, use_container_width=True)


st.header("Mapa de Ocorrências")

if not df_filtered[["latitude", "longitude"]].dropna().empty:
    fig_map = px.scatter_mapbox(
        df_filtered,
        lat="latitude",
        lon="longitude",
        color="best_est",
        size="best_est",
        zoom=3,
        height=500
  )
fig_map.update_layout(mapbox_style="open-street-map")
