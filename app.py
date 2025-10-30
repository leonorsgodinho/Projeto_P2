import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da Página: CORREÇÃO DO ATRIBUTO
st.set_page_config(layout="wide", page_title="Análise de Conflitos no Brasil") 
sns.set_style("whitegrid")

# --- Carregamento e Cache dos Dados ---
@st.cache_data
def load_data(file_path):
    """
    Carrega, limpa e padroniza os dados do CSV.
    """
    try:
        # PARÂMETROS FINAIS E ESSENCIAIS PARA ESTE ARQUIVO:
        # sep=',' -> Separador de colunas (necessário para encontrar o cabeçalho)
        # engine='python' -> Essencial para lidar com inconsistências de formatação.
        # on_bad_lines='skip' -> Essencial para ignorar linhas malformadas (como a linha 188).
        # REMOVEMOS QUOTING=3: Permite que o Pandas trate aspas duplas, corrigindo o KeyError.
        df = pd.read_csv(
            file_path, 
            sep=',',
            engine='python', 
            on_bad_lines='skip'
        )
        
        # --- Limpeza e Transformação ---
        
        # Converte 'date_start' (agora encontrado) para datetime
        df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
        
        # Força colunas numéricas (transforma strings problemáticas em NaN)
        # O separador decimal é o ponto por padrão (correto para lat/lon)
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['best_est'] = pd.to_numeric(df['best_est'], errors='coerce')

        # Remove linhas sem data ou coordenadas
        df = df.dropna(subset=['date_start', 'latitude', 'longitude'])
        
        # Cria uma coluna 'month_year'
        df['month_year'] = df['date_start'].dt.to_period('M')

        return df
    
    except Exception as e:
        st.error(f"Erro Crítico de Leitura do CSV: Falha ao carregar o arquivo. Detalhes: {e}")
        return None

# --- Carregar os Dados ---
df = load_data('brazil_conflicts_dataset.csv')

if df is not None:
    
    # --- BARRA LATERAL (Filtros) ---
    st.sidebar.header("Filtros Interativos")

    # Filtro multiselect para o Estado (adm_1)
    all_states = sorted(df['adm_1'].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "Selecione o(s) Estado(s) (adm_1):",
        options=all_states,
        default=all_states
    )

    # Filtra o DataFrame principal
    if selected_states:
        df_filtered = df[df['adm_1'].isin(selected_states)]
    else:
        df_filtered = df.copy()

    # --- PÁGINA PRINCIPAL ---
    st.title("Dashboard: Análise de Conflitos no Brasil")
    
    # --- Métricas Principais (KPIs) ---
    total_events = len(df_filtered)
    total_deaths = int(df_filtered['best_est'].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Estados Selecionados", len(selected_states))
    col2.metric("Total de Eventos", f"{total_events:,}")
    col3.metric("Total de Mortes (best_est)", f"{total_deaths:,}")

    # --- Secção de Gráficos ---
    st.header("Análise Temporal e Geográfica")

    # --- Gráficos em colunas ---
    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        # GRÁFICO 1: Eventos de Conflito por Mês (filtrado)
        st.subheader("Eventos de Conflito por Mês")
        events_per_month = df_filtered.groupby('month_year').size().reset_index(name='total_events')
        events_per_month['month_year'] = events_per_month['month_year'].dt.to_timestamp()
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=events_per_month, x='month_year', y='total_events', ax=ax1)
        ax1.set_title('Total de Eventos por Mês')
        ax1.set_xlabel('Data')
        ax1.set_ylabel('Número de Eventos')
        st.pyplot(fig1)

    with fig_col2:
        # GRÁFICO 2: Total de Mortes por Mês (filtrado)
        st.subheader("Total de Mortes por Mês")
        deaths_per_month = df_filtered.groupby('month_year')['best_est'].sum().reset_index(name='total_deaths')
        deaths_per_month['month_year'] = deaths_per_month['month_year'].dt.to_timestamp()
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=deaths_per_month, x='month_year', y='total_deaths', color='red', ax=ax2)
        ax2.set_title("Total de Mortes ('best_est') por Mês")
        ax2.set_xlabel('Data')
        ax2.set_ylabel('Número de Mortes')
        st.pyplot(fig2)

    # --- Mapa de Ocorrências ---
    st.header("Mapa de Ocorrências")
    
    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])

    if not df_map.empty:
        st.map(df_map[['latitude', 'longitude']])
    else:
        st.warning("Não há dados de latitude/longitude válidos para os filtros selecionados.")

    # --- Tabela de Dados (Opcional) ---
    if st.checkbox("Mostrar dados filtrados"):
        st.subheader("Dados Filtrados")
        st.dataframe(df_filtered)

else:
    st.error("A aplicação não pode continuar devido a um erro no carregamento dos dados.")
