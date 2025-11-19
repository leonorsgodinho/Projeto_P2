import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(layout="wide", page_title="Análise de Conflitos no Brasil")
sns.set_style("whitegrid")

@st.cache_data
def load_data(file_path):
    try:
        # Read as strings first to avoid column-shift from malformed rows; be permissive with quotes
        df = pd.read_csv(
            file_path,
            sep=",",
            encoding="latin1",
            engine="python",
            on_bad_lines="skip"
        )        

        
        # Limpeza básica
        df.columns = df.columns.str.strip()

        # Datas: attempt flexible parsing (try dayfirst False, then True)
        parsed = pd.to_datetime(df["date_start"], errors="coerce", dayfirst=False)
        if parsed.isna().all():
            parsed = pd.to_datetime(df["date_start"], errors="coerce", dayfirst=True)
        df["date_start"] = parsed

        # Coordenadas
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        # Mortes (best_est)
        df["best_est"] = pd.to_numeric(df["best_est"], errors="coerce")
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        
        # Shift all columns to the right after `where_coordinates` for all rows,
        # by inserting a temporary blank column at the end and moving values.
        if "where_coordinates" in df.columns:
            cols = list(df.columns)
            idx = cols.index("where_coordinates")
            # create a unique temporary column name
            tmp = "__shift_tmp__"
            while tmp in df.columns:
                tmp += "_"
            df[tmp] = None

            # refresh cols now that tmp exists
            cols = list(df.columns)
            # shift values one column to the right for all columns after idx
            for j in range(len(cols) - 1, idx, -1):
                df[cols[j]] = df[cols[j - 1]]

            # set the original where_coordinates column to None (cleared)
            df[cols[idx]] = None

            # remove the temporary column
            df = df.drop(columns=[tmp])

        # Criação da coluna mês-ano (só quando date_start é datetimelike)
        try:
            if pd.api.types.is_datetime64_any_dtype(df["date_start"]):
                df["month_year"] = df["date_start"].dt.to_period("M")
            else:
                # attempt a final coercion
                parsed_final = pd.to_datetime(df["date_start"], errors="coerce")
                if pd.api.types.is_datetime64_any_dtype(parsed_final):
                    df["date_start"] = parsed_final
                    df["month_year"] = parsed_final.dt.to_period("M")
                else:
                    df["month_year"] = pd.NaT
                    st.warning("Algumas datas não foram parseadas para datetime; 'month_year' ficará vazio.")
        except Exception as e:
            df["month_year"] = pd.NaT
            st.warning(f"Erro ao criar 'month_year': {e}")

        return df

    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None


df = load_data("brazil_conflicts_dataset.csv")

if df is not None:

    # ==========================
    # SIDEBAR – FILTROS
    # ==========================

    st.sidebar.header("Filtros")

    anos_disponiveis = sorted(df["year"].dropna().unique()) 
    tipos_violencia = sorted(df["type_of_violence"].dropna().unique())
    regioes = sorted(df["adm_1"].dropna().unique())
    
    ano_selecionado = st.sidebar.selectbox(
        "Selecione o ano",
        options=anos_disponiveis
    )
    
    tipo_escolhido = st.sidebar.multiselect(
        "Tipo de Violência",
        tipos_violencia,
        default=tipos_violencia
    )
    
    regiao_escolhida = st.sidebar.multiselect(
        "Região (Estado)",
        regioes,
        default=regioes
    )
    
    # Aplicar filtros
    df_filtrado = df[
        (df["year"] == ano_selecionado).copy() &
        (df["type_of_violence"].isin(tipo_escolhido)) &
        (df["adm_1"].isin(regiao_escolhida))
    ]
    
    st.success(f"{len(df_filtrado):,} eventos após filtros")
        
    st.title("Dashboard: Conflitos Armados no Brasil")

    # KPIs gerais
    total_eventos = len(df_filtrado)
    total_mortes = int(df_filtrado["best_est"].sum())

    col1, col2 = st.columns(2)
    col1.metric("Total de Eventos", f"{total_eventos:,}")
    col2.metric("Total de Mortes (best_est)", f"{total_mortes:,}")

    # --------------------------
    # GRÁFICOS TEMPORAIS
    # --------------------------

    st.header("Análise Temporal")

    eventos_mes = df_filtrado.groupby("month_year").size().reset_index(name="total_eventos")
    eventos_mes["month_year"] = eventos_mes["month_year"].dt.to_timestamp()

    mortes_mes = df_filtrado.groupby("month_year")["best_est"].sum().reset_index(name="total_mortes")
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

    # Diagnóstico do mapa
    df_map = df_filtrado.dropna(subset=["latitude", "longitude"]).copy()
    lat = pd.to_numeric(df_map["latitude"], errors="coerce")
    lon = pd.to_numeric(df_map["longitude"], errors="coerce")
    st.write(f"Pontos para map: {len(df_map)}")
    if len(df_map) > 0:
        st.write(f"Latitude min/max: {lat.min()} / {lat.max()}")
        st.write(f"Longitude min/max: {lon.min()} / {lon.max()}")

    # Use scatter_map which is the modern Plotly API (mapbox backend handled internally)
    fig_map = px.scatter_map(
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

    st.plotly_chart(fig_map, width='stretch')

