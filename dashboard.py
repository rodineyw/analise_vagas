import logging
import re
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide", page_title="Dashboard de Vagas de Dados - Brasil", page_icon="📊")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def clean_salary(salary_str: str) -> Optional[float]:
    if not isinstance(salary_str, str) or "R$" not in salary_str:
        return None
    numbers = re.findall(r'\d+\.?\d*', salary_str.replace('.', '').replace(',', '.'))
    if numbers:
        return float(numbers[0])
    return None

def map_uf_to_regiao(uf: str) -> str:
    sudeste = ['SP', 'RJ', 'ES', 'MG']
    sul = ['PR', 'SC', 'RS']
    centro_oeste = ['MT', 'MS', 'GO', 'DF']
    nordeste = ['BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA']
    norte = ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC']
    if uf in sudeste: 
        return "Sudeste"
    if uf in sul: 
        return "Sul"
    if uf in centro_oeste: 
        return "Centro-Oeste"
    if uf in nordeste: 
        return "Nordeste"
    if uf in norte: 
        return "Norte"
    if uf == "Remoto": 
        return "Remoto"
    return "Não especificada"

@st.cache_data
def load_and_process_data() -> pd.DataFrame:
    try:
        df = pd.read_csv('vagas_consolidadas.csv')
        df['salario_valor'] = df['salario'].apply(clean_salary)
        df['regiao'] = df['uf'].apply(map_uf_to_regiao)
        df['cidade'] = df['localizacao'].apply(
            lambda x: str(x).split('-')[0].split('/')[0].split(',')[0].strip() if isinstance(x, str) else 'Não especificada'
        )
        return df
    except FileNotFoundError:
        st.error("Arquivo 'vagas_consolidadas.csv' não encontrado. Execute o scraper primeiro.")
        return pd.DataFrame()

st.title("📊 Dashboard de Vagas de Dados (Vagas.com)")
st.caption("Dados atualizado diariamente.")

df = load_and_process_data()

if not df.empty:
    with st.sidebar:
        st.header("🎛️ Filtros Avançados")
        all_ufs = sorted(df['uf'].unique())
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

    # KPIs em cards com ícone
    total_vagas = len(filtered_df)
    vagas_com_salario = filtered_df['salario_valor'].notna().sum()
    media_salarial = filtered_df['salario_valor'].mean()
    mediana_salarial = filtered_df['salario_valor'].median()
    maior_salario = filtered_df['salario_valor'].max()
    menor_salario = filtered_df['salario_valor'].min()
    total_remoto = (filtered_df['uf'] == 'Remoto').sum()
    empresas_unicas = filtered_df['empresa'].nunique()
    cidades_unicas = filtered_df['cidade'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Vagas", f"{total_vagas}")
    col2.metric("🏢 Empresas", f"{empresas_unicas}")
    col3.metric("🌍 Cidades", f"{cidades_unicas}")
    col4.metric("🏠 Remotas", f"{total_remoto}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("💸 Média Salário", f"{media_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")
    col6.metric("🔻 Mediana Salário", f"{mediana_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")
    col7.metric("⬆️ Maior Salário", f"{maior_salario:,.2f}" if vagas_com_salario > 0 else "N/A")
    col8.metric("⬇️ Menor Salário", f"{menor_salario:,.2f}" if vagas_com_salario > 0 else "N/A")

    st.markdown("---")

    # GRÁFICOS (Power BI vibes)
    colA, colB = st.columns(2)

    with colA:
        st.subheader("📈 Vagas por UF")
        vagas_por_uf = filtered_df['uf'].value_counts().reset_index()
        vagas_por_uf.columns = ['UF', 'Quantidade']
        fig = px.bar(vagas_por_uf, x='UF', y='Quantidade', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("💰 Salário Médio por UF")
        salario_por_uf = filtered_df.groupby('uf')['salario_valor'].mean().dropna().reset_index()
        salario_por_uf.columns = ['UF', 'Salario_Medio']
        fig2 = px.bar(salario_por_uf, x='UF', y='Salario_Medio', text_auto='.2f', template="plotly_white", color='Salario_Medio', color_continuous_scale='Purples')
        st.plotly_chart(fig2, use_container_width=True)

    with colB:
        st.subheader("🏙️ Vagas por Cidade (Top 10)")
        top_cidades = filtered_df['cidade'].value_counts().head(10).reset_index()
        top_cidades.columns = ['Cidade', 'Quantidade']
        fig3 = px.bar(top_cidades, x='Quantidade', y='Cidade', orientation='h', text_auto=True, template="seaborn", color='Quantidade', color_continuous_scale='Greens')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("🎯 Modalidade da Vaga")
        modalidade = filtered_df['uf'].apply(lambda x: 'Remoto' if x == 'Remoto' else 'Presencial')
        modalidade_count = modalidade.value_counts().reset_index()
        modalidade_count.columns = ['Modalidade', 'Quantidade']
        fig6 = px.pie(modalidade_count, values='Quantidade', names='Modalidade', hole=.4, color='Modalidade', color_discrete_map={'Remoto': 'deepskyblue', 'Presencial': 'orange'})
        fig6.update_traces(textinfo='percent+label')
        st.plotly_chart(fig6, use_container_width=True)

    # Boxplot, Top Empresas, Histograma, Expander detalhado — estilo BI:
    st.markdown("## 🎓 Detalhes e Distribuições Avançadas")

    exp1, exp2 = st.columns(2)

    with exp1:
        st.subheader("📊 Boxplot de Salários por UF")
        df_boxplot = filtered_df.dropna(subset=['salario_valor'])
        if not df_boxplot.empty:
            fig5 = px.box(df_boxplot, x='uf', y='salario_valor', template="simple_white", color='uf',
                          labels={'uf': 'UF', 'salario_valor': 'Salário'}, points="all")
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Nenhuma vaga com salário informado para a seleção atual.")

    with exp2:
        st.subheader("🏆 Top 5 Empresas que Mais Pagam (Média)")
        top_empresas_salario = (
            filtered_df.groupby('empresa')['salario_valor']
            .mean().dropna().sort_values(ascending=False).head(5).reset_index()
        )
        top_empresas_salario.columns = ['Empresa', 'Salario_Medio']
        fig4 = px.bar(top_empresas_salario, x='Salario_Medio', y='Empresa', orientation='h', template="ggplot2",
                      labels={'Salario_Medio': 'Salário Médio', 'Empresa': 'Empresa'}, text_auto='.2f', color='Salario_Medio', color_continuous_scale='sunsetdark')
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("🔍 Ver distribuição completa de salários (histograma)"):
        st.subheader("Distribuição de Salários")
        df_salario = filtered_df.dropna(subset=['salario_valor'])
        if not df_salario.empty:
            fig = px.histogram(df_salario, x="salario_valor", nbins=20, title="Distribuição de Salários", template="seaborn")
            fig.update_layout(xaxis_title="Salário (R$)", yaxis_title="Quantidade de Vagas")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma vaga com salário informado para a seleção atual.")

    st.markdown("---")
    with st.expander("🗃️ Ver tabela completa de dados"):
        st.dataframe(filtered_df, use_container_width=True)
