import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="Análise de Conflitos no Brasil")
sns.set_style("whitegrid")

@st.cache_data
def load_data(file_path):
    """
    Carrega, limpa e padroniza os dados do CSV.
    """
    try:
        df = pd.read_csv(
            file_path, 
            decimal=',', 
            sep=';', 
            engine='python', 
            on_bad_lines='skip'
        )      
        
        df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
        
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['best_est'] = pd.to_numeric(df['best_est'], errors='coerce')

        df = df.dropna(subset=['date_start', 'latitude', 'longitude'])
        
        df['month_year'] = df['date_start'].dt.to_period('M')

        return df
    
    except pd.errors.ParserError as e:
        st.error(f"Erro Crítico de Leitura do CSV: Falha ao analisar o arquivo. Por favor, verifique se o arquivo '{file_path}' não tem linhas malformadas. Detalhes: {e}")
        return None
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{file_path}' não encontrado. Certifique-se de que está na pasta.")
        return None

df = load_data('brazil_conflicts_dataset.csv')

if df is not None:
    
    st.sidebar.header("Filtros Interativos")

    all_states = sorted(df['adm_1'].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "Selecione o(s) Estado(s) (adm_1):",
        options=all_states,
        default=all_states
    )

    if selected_states:
        df_filtered = df[df['adm_1'].isin(selected_states)]
    else:
        df_filtered = df.copy()

    st.title("Dashboard: Análise de Conflitos no Brasil")
    
    total_events = len(df_filtered)
    total_deaths = int(df_filtered['best_est'].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Estados Selecionados", len(selected_states))
    col2.metric("Total de Eventos", f"{total_events:,}")
    col3.metric("Total de Mortes (best_est)", f"{total_deaths:,}")

    st.header("Análise Temporal e Geográfica")

    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        st.subheader("Eventos de Conflito por Mês")
        events_per_month = df_filtered.groupby('month_year').size().reset_index(name='total_events')
        events_per_month['month_year'] = events_per_month['month_year'].dt.to_timestamp()
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=events_per_month, x='month_year', y='total_events', color='blue', ax=ax1)
        ax1.set_title('Total de Eventos por Mês')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Número de Eventos')
        st.pyplot(fig1)

    with fig_col2:
        st.subheader("Total de Mortes por Mês")
        deaths_per_month = df_filtered.groupby('month_year')['best_est'].sum().reset_index(name='total_deaths')
        deaths_per_month['month_year'] = deaths_per_month['month_year'].dt.to_timestamp()
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=deaths_per_month, x='month_year', y='total_deaths', color='red', ax=ax2)
        ax2.set_title("Total de Mortes ('best_est') por Mês")
        ax2.set_xlabel('Data')
        ax2.set_ylabel('Número de Mortes')
        st.pyplot(fig2)

    st.header("Mapa de Ocorrências")
    st.markdown("Visualização dos pontos de conflito (baseado nos filtros selecionados).")
    
    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])

    if not df_map.empty:
        st.map(df_map[['latitude', 'longitude']])
    else:
        st.warning("Não há dados de latitude/longitude válidos para os filtros selecionados.")

   
    if st.checkbox("Mostrar dados filtrados"):
        st.subheader("Dados Filtrados")
        st.dataframe(df_filtered)

else:
    st.error("A aplicação não pode continuar devido a um erro no carregamento dos dados.")
