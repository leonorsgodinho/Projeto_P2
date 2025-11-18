import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(layout="wide", page_title="Conflitos no Brasil — Dashboard")
sns.set_style("whitegrid")

@st.cache_data
def load_data(path):
    df = pd.read_csv(
            file_path,
            sep=",",
            engine="python",
            on_bad_lines="skip"
        )

    df.columns = df.columns.str.strip()

    df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["best_est"] = pd.to_numeric(df["best_est"], errors="coerce")

    df = df.dropna(subset=["date_start", "latitude", "longitude"])

    df["month_year"] = df["date_start"].dt.to_period("M")

    return df

    except Exception as e:
        st.error(f"Erro ao carregar o CSV: {e}")
        return None

df = load_data("brazil_conflicts_dataset.csv")

if df is None:
    st.stop()

st.title("📊 Dashboard: Análise de Conflitos no Brasil (1993–2024)")

total_events = len(df)
total_deaths = int(df["best_est"].sum())

col1, col2 = st.columns(2)
col1.metric("Total de Eventos", f"{total_events:,}")
col2.metric("Total de Mortes (best_est)", f"{total_deaths:,}")

st.subheader("📈 Eventos de Conflito por Mês")

events_per_month = (
    df.groupby("month_year")
    .size()
    .reset_index(name="total_events")
)
events_per_month["month_year"] = events_per_month["month_year"].dt.to_timestamp()

fig1, ax1 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=events_per_month, x="month_year", y="total_events", ax=ax1)
ax1.set_title("Total de Eventos por Mês")
ax1.set_xlabel("Data")
ax1.set_ylabel("Número de Eventos")
st.pyplot(fig1)

st.subheader("📉 Total de Mortes por Mês")

deaths_per_month = (
    df.groupby("month_year")["best_est"]
    .sum()
    .reset_index(name="total_deaths")
)
deaths_per_month["month_year"] = deaths_per_month["month_year"].dt.to_timestamp()

fig2, ax2 = plt.subplots(figsize=(12, 4))
sns.lineplot(data=deaths_per_month, x="month_year", y="total_deaths", ax=ax2, color="red")
ax2.set_title("Total de Mortes por Mês")
ax2.set_xlabel("Data")
ax2.set_ylabel("Número de Mortes")
st.pyplot(fig2)


st.markdown("---")

st.subheader("🗺️ Mapa de Ocorrências no Brasil")

df_map = df.dropna(subset=["latitude", "longitude"])

fig_map = px.scatter_mapbox(
    df_map,
    lat="latitude",
    lon="longitude",
    hover_name="adm_1",
    hover_data=["date_start", "best_est"],
    zoom=3,
    height=550
)

fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0, "t":0, "l":0, "b":0})

st.plotly_chart(fig_map, use_container_width=True)


st.markdown("---")

if st.checkbox("Mostrar tabela completa do dataset"):
    st.subheader("📄 Dados Completos")
    st.dataframe(df, use_container_width=True)
