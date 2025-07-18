# dashboard.py
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuração da Página do Streamlit ---
# 'wide' usa a largura total da tela.
st.set_page_config(layout="wide", page_title="Dashboard de Vagas de Dados - SP")

# --- Título do Dashboard ---
st.title("📊 Dashboard de Vagas de Dados em São Paulo")
st.markdown("Análise de vagas para Analistas, Engenheiros e Cientistas de Dados.")

# --- Carregamento de Dados ---
# @st.cache_data armazena o resultado da função em cache.
# Isso evita recarregar os dados do disco a cada interação do usuário.
@st.cache_data
def load_data():
    """Carrega os dados do CSV de forma segura."""
    try:
        df = pd.read_csv('vagas_sp.csv')
        logging.info("Arquivo 'vagas_sp.csv' carregado com sucesso.")
        return df
    except FileNotFoundError:
        logging.warning("Arquivo 'vagas_sp.csv' não encontrado. Execute o scraper primeiro.")
        # Retorna um DataFrame vazio se o arquivo não existir, para não quebrar o app.
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Nenhum dado para exibir. Por favor, execute o script `scraper.py` primeiro para coletar os dados.")
else:
    # --- Análise e Visualização ---
    total_vagas = len(df)
    ultima_atualizacao = pd.to_datetime(df['data_coleta']).max().strftime('%d/%m/%Y')

    # Métricas principais (KPIs)
    col1, col2 = st.columns(2)
    col1.metric("Total de Vagas Únicas Analisadas", f"{total_vagas}")
    col2.metric("Última Atualização", ultima_atualizacao)

    st.markdown("---")

    # --- Gráficos ---
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico 1: Top 10 Empresas que mais contratam
        st.subheader("Top 10 Empresas com Mais Vagas")
        top_empresas = df['empresa'].value_counts().nlargest(10)
        fig_empresas = px.bar(
            top_empresas,
            x=top_empresas.values,
            y=top_empresas.index,
            orientation='h',
            labels={'y': 'Empresa', 'x': 'Quantidade de Vagas'},
            text=top_empresas.values,
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_empresas.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_empresas, use_container_width=True)

    with col2:
        # Gráfico 2: Análise de palavras-chave nos títulos das vagas
        st.subheader("Termos Comuns nos Títulos das Vagas")
        # Concatena todos os títulos em um único texto
        textao = ' '.join(df['titulo'].dropna().str.lower())
        # Cria uma série com a contagem de cada palavra
        word_counts = pd.Series(textao.split()).value_counts()
        # Filtra palavras comuns e pouco relevantes
        common_words_to_exclude = ['de', 'e', 'para', 'em', 'vaga', 'i', 'ii', 'iii', 'são', 'paulo', 'sp']
        top_words = word_counts[~word_counts.index.isin(common_words_to_exclude)].nlargest(10)
        
        fig_words = px.bar(
            top_words,
            x=top_words.index,
            y=top_words.values,
            labels={'x': 'Termo', 'y': 'Frequência'},
            text=top_words.values,
            color_discrete_sequence=px.colors.sequential.Mint
        )
        st.plotly_chart(fig_words, use_container_width=True)

    # --- Tabela de Dados Brutos ---
    st.markdown("---")
    st.subheader("Dados Brutos das Vagas")
    st.dataframe(df)

