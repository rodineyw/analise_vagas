# dashboard.py
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(layout="wide")

# Título do Dashboard
st.title("📊 Dashboard de Vagas de Análise de Dados em SP")

@st.cache_data
def load_data():
    """Carrega os dados do CSV, com cache para performance."""
    try:
        df = pd.read_csv('vagas_dados.csv')
        logging.info("Dados carregados com sucesso para o dashboard.")
        return df
    except FileNotFoundError:
        logging.error("Arquivo vagas_dados.csv não encontrado.")
        st.error("Arquivo de dados não encontrado. Execute o scraper primeiro.")
        return pd.DataFrame() # Retorna um DataFrame vazio para não quebrar o app

df = load_data()

if not df.empty:
    # KPI - Número total de vagas
    total_vagas = len(df)
    st.metric(label="Total de Vagas Analisadas", value=total_vagas)

    # Gráfico 1: Top 10 empresas que mais contratam
    st.header("Top 10 Empresas Contratando")
    top_empresas = df['empresa'].value_counts().nlargest(10)
    fig1 = px.bar(top_empresas, x=top_empresas.index, y=top_empresas.values, 
                  labels={'x': 'Empresa', 'y': 'Número de Vagas'},
                  text_auto=True)
    st.plotly_chart(fig1)

    # Mostrar dados brutos
    st.header("Dados Brutos")
    st.dataframe(df)