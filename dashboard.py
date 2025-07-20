# dashboard.py
import logging
import re
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide", page_title="Dashboard de Vagas de Dados - Brasil", page_icon="📊")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mantém seu estilo customizado para os cards de métricas
st.markdown(
    """
    <style>
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg,#fff,#f4f7fb 75%);
        border-radius: 12px;
        padding: 16px 8px 16px 8px;
        margin-bottom: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px 0 rgba(80,80,80,0.09);
    }
    .block-container {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True
)

def map_uf_to_regiao(uf: str) -> str:
    """Mapeia a sigla do UF para uma região do Brasil."""
    sudeste = ['SP', 'RJ', 'ES', 'MG']
    sul = ['PR', 'SC', 'RS']
    centro_oeste = ['MT', 'MS', 'GO', 'DF']
    nordeste = ['BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA']
    norte = ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC']
    if uf in sudeste: return "Sudeste"
    if uf in sul: return "Sul"
    if uf in centro_oeste: return "Centro-Oeste"
    if uf in nordeste: return "Nordeste"
    if uf in norte: return "Norte"
    if uf == "Remoto": return "Remoto"
    return "Não especificada"

def get_seniority_from_title(title_str: str) -> str:
    """Extrai o nível de senioridade a partir do título da vaga."""
    title_lower = title_str.lower()
    if any(term in title_lower for term in ['sênior', 'sr', 'senior', 'specialist', 'especialista']):
        return 'Sênior / Especialista'
    if any(term in title_lower for term in ['pleno', 'pl']):
        return 'Pleno'
    if any(term in title_lower for term in ['júnior', 'jr', 'junior']):
        return 'Júnior'
    if any(term in title_lower for term in ['estágio', 'estagiário', 'intern']):
        return 'Estágio'
    if any(term in title_lower for term in ['líder', 'lider', 'leader', 'tech lead', 'coordenador']):
        return 'Liderança'
    return 'Não especificado'

@st.cache_data
def load_and_process_data() -> pd.DataFrame:
    """Carrega e processa os dados do CSV, adicionando as novas colunas de análise."""
    try:
        df = pd.read_csv('vagas_consolidadas.csv')
        df['regiao'] = df['uf'].apply(map_uf_to_regiao)
        df['cidade'] = df['localizacao'].apply(
            lambda x: str(x).split('-')[0].split('/')[0].split(',')[0].strip() if isinstance(x, str) else 'Não especificada'
        )
        df['senioridade'] = df['titulo'].apply(get_seniority_from_title)
        return df
    except FileNotFoundError:
        st.error("Arquivo 'vagas_consolidadas.csv' não encontrado. Execute o scraper primeiro.")
        return pd.DataFrame()

st.title("📊 Dashboard de Vagas de Dados (Vagas.com)")
st.caption("Dados atualizado diariamente.")

df: pd.DataFrame = load_and_process_data()

if not df.empty:
    with st.sidebar:
        st.header("🎛️ Filtros Avançados")
        # --- CORREÇÃO APLICADA AQUI ---
        # Converte a coluna 'uf' para string antes de obter os valores únicos e ordenar.
        # Isso evita o erro de tipo misto (float e str).
        all_ufs = sorted(df['uf'].astype(str).unique())
        all_regioes = sorted(df['regiao'].unique())
        all_empresas = sorted(df['empresa'].unique())

        selected_ufs = st.multiselect("Filtrar por UF", all_ufs, default=all_ufs)
        selected_regioes = st.multiselect("Filtrar por Região", all_regioes, default=all_regioes)
        selected_empresas = st.multiselect("Filtrar por Empresa", all_empresas, default=None)

    filtered_df = df[
        df['uf'].isin(selected_ufs) &
        df['regiao'].isin(selected_regioes)
    ]
    if selected_empresas:
        filtered_df = filtered_df[filtered_df['empresa'].isin(selected_empresas)]

    # KPIs
    total_vagas = len(filtered_df)
    total_remoto = (filtered_df['uf'] == 'Remoto').sum()
    empresas_unicas = filtered_df['empresa'].nunique()
    cidades_unicas = filtered_df['cidade'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Vagas", f"{total_vagas}")
    col2.metric("🏢 Empresas", f"{empresas_unicas}")
    col3.metric("🌍 Cidades", f"{cidades_unicas}")
    col4.metric("🏠 Remotas", f"{total_remoto}")

    st.markdown("---")

    # GRÁFICOS
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📈 Vagas por UF")
        vagas_por_uf = filtered_df['uf'].value_counts().reset_index()
        vagas_por_uf.columns = ['UF', 'Quantidade']
        fig = px.bar(vagas_por_uf, x='UF', y='Quantidade', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("👔 Vagas por Senioridade")
        seniority_counts = filtered_df['senioridade'].value_counts().reset_index()
        seniority_counts.columns = ['Senioridade', 'Quantidade']
        fig_seniority = px.bar(seniority_counts, x='Senioridade', y='Quantidade', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Oranges')
        st.plotly_chart(fig_seniority, use_container_width=True)

    with colB:
        st.subheader("🏙️ Vagas por Cidade (Top 10)")
        top_cidades = filtered_df['cidade'].value_counts().head(10).reset_index()
        top_cidades.columns = ['Cidade', 'Quantidade']
        fig3 = px.bar(top_cidades, x='Quantidade', y='Cidade', orientation='h', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Greens')
        st.plotly_chart(fig3, use_container_width=True)

        # ANÁLISE CORRIGIDA: Usa a coluna 'descricao' para a contagem de palavras-chave
        st.subheader("🛠️ Tecnologias em Destaque")
        keywords = {
            'Power BI': 'power bi|powerbi|pbi', 'Excel': 'excel', 'SQL': 'sql', 
            'Python': 'python', 'Tableau': 'tableau', 'Cloud': 'aws|azure|gcp|cloud'
        }
        # Garante que a coluna 'descricao' seja do tipo string para evitar erros
        descriptions = filtered_df['descricao'].astype(str)
        keyword_counts = {key: descriptions.str.contains(val, case=False).sum() for key, val in keywords.items()}
        df_keywords = pd.DataFrame(list(keyword_counts.items()), columns=['Tecnologia', 'Quantidade']).sort_values('Quantidade', ascending=False)
        
        fig_keywords = px.bar(df_keywords, x='Quantidade', y='Tecnologia', orientation='h', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Purples')
        st.plotly_chart(fig_keywords, use_container_width=True)

    st.markdown("---")
    with st.expander("🗃️ Ver tabela completa de dados"):
        st.dataframe(filtered_df.drop(columns=['fonte', 'descricao'], errors='ignore'), use_container_width=True)
