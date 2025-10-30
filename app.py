import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Conflitos Organizados no Brasil", layout="wide")
st.title("Estatísticas de Conflitos Organizados no Brasil")

# Ler CSV
df = pd.read_csv("data/brazil_conflicts_dataset.csv", low_memory=False)

# Mostrar colunas e primeiras linhas (debug)
st.write("Colunas disponíveis:", df.columns)
st.write(df.head())

# Filtros
estados_disponiveis = df['adm_1'].dropna().unique()
estado_selecionado = st.sidebar.selectbox("Escolha um estado/região", estados_disponiveis)

anos_disponiveis = sorted(df['year'].dropna().unique())
ano_selecionado = st.sidebar.select_slider(
    "Escolha o ano",
    options=anos_disponiveis,
    value=anos_disponiveis[-1]
)

# Aplicar filtros
df_filtrado = df[(df['adm_1'] == estado_selecionado) & (df['year'] == ano_selecionado)]

# Mostrar tabela filtrada
st.subheader(f"Dados de conflitos em {estado_selecionado} em {ano_selecionado}")
st.dataframe(df_filtrado[['type_of_violence', 'best_est', 'deaths_a', 'deaths_b', 'deaths_civilians']])

# Gráfico de barras — número de mortos por tipo de violência
if 'type_of_violence' in df_filtrado.columns and 'best_est' in df_filtrado.columns:
    chart_data = df_filtrado.groupby('type_of_violence')['best_est'].sum().reset_index()
    fig = px.bar(
        chart_data,
        x='type_of_violence',
        y='best_est',
        color='type_of_violence',
        text='best_est',
        labels={'type_of_violence': 'Tipo de Violência', 'best_est': 'Número Estimado de Mortes'}
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("As colunas necessárias não foram encontradas no dataset.")
