import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import re
from typing import Optional

st.set_page_config(layout="wide", page_title="Dashboard de Vagas de Dados - Brasil")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        # Nova coluna cidade
        df['cidade'] = df['localizacao'].apply(lambda x: str(x).split('-')[0].split('/')[0].split(',')[0].strip() if isinstance(x, str) else 'Não especificada')
        return df
    except FileNotFoundError:
        st.error("Arquivo 'vagas_consolidadas.csv' não encontrado. Execute o scraper primeiro.")
        return pd.DataFrame()

st.title("📊 Dashboard de Vagas de Dados no Brasil (Vagas.com)")

df = load_and_process_data()

if not df.empty:
    st.sidebar.header("Filtros")
    all_ufs = sorted(df['uf'].unique())
    selected_ufs = st.sidebar.multiselect(
        "Selecione a UF",
        options=all_ufs,
        default=all_ufs
    )
    filtered_df = df[df['uf'].isin(selected_ufs)]

    # --- KPIs ---
    total_vagas = len(filtered_df)
    vagas_com_salario = filtered_df['salario_valor'].notna().sum()
    media_salarial = filtered_df['salario_valor'].mean()
    mediana_salarial = filtered_df['salario_valor'].median()
    maior_salario = filtered_df['salario_valor'].max()
    menor_salario = filtered_df['salario_valor'].min()
    total_remoto = (filtered_df['uf'] == 'Remoto').sum()
    empresas_unicas = filtered_df['empresa'].nunique()
    cidades_unicas = filtered_df['cidade'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vagas", f"{total_vagas}")
    col2.metric("Vagas com Salário", f"{vagas_com_salario}")
    col3.metric("Empresas Únicas", f"{empresas_unicas}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Cidades Únicas", f"{cidades_unicas}")
    col5.metric("Vagas Remotas", f"{total_remoto}")
    col6.metric("Média Salarial (R$)", f"{media_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")

    col7, col8, col9 = st.columns(3)
    col7.metric("Mediana Salarial (R$)", f"{mediana_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")
    col8.metric("Maior Salário (R$)", f"{maior_salario:,.2f}" if vagas_com_salario > 0 else "N/A")
    col9.metric("Menor Salário (R$)", f"{menor_salario:,.2f}" if vagas_com_salario > 0 else "N/A")

    st.markdown("---")

    # --- Gráficos ---
    colA, colB = st.columns(2)

    with colA:
        st.subheader("Distribuição de Vagas por UF")
        vagas_por_uf = filtered_df['uf'].value_counts()
        fig = px.bar(vagas_por_uf, x=vagas_por_uf.index, y=vagas_por_uf.values,
                     labels={'x': 'UF', 'y': 'Quantidade de Vagas'}, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Salário Médio por UF")
        # salario_por_uf é uma Series: uf como index, média salarial como valor
        salario_df = salario_por_uf.reset_index()
        salario_df.columns = ['UF', 'Salario_Medio']

        fig2 = px.bar(
            salario_df,
            x='UF',
            y='Salario_Medio',
            labels={'UF': 'UF', 'Salario_Medio': 'Salário Médio'},
            text_auto='.2f'
        )
        st.plotly_chart(fig2, use_container_width=True)


        st.subheader("Top 5 Empresas que Mais Pagam (Média Salarial)")
        top_empresas_salario = filtered_df.groupby('empresa')['salario_valor'].mean().dropna().sort_values(ascending=False).head(5)
        fig4 = px.bar(top_empresas_salario, x=top_empresas_salario.values, y=top_empresas_salario.index,
                      orientation='h', labels={'x': 'Salário Médio', 'y': 'Empresa'}, text_auto='.2f')
        st.plotly_chart(fig4, use_container_width=True)

    with colB:
        st.subheader("Distribuição de Vagas por Cidade")
        top_cidades = filtered_df['cidade'].value_counts().head(10)
        fig3 = px.bar(top_cidades, x=top_cidades.values, y=top_cidades.index, orientation='h',
                      labels={'x': 'Quantidade de Vagas', 'y': 'Cidade'}, text_auto=True)
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Boxplot de Salários por UF")
        df_boxplot = filtered_df.dropna(subset=['salario_valor'])
        if not df_boxplot.empty:
            fig5 = px.box(df_boxplot, x='uf', y='salario_valor',
                          labels={'uf': 'UF', 'salario_valor': 'Salário'}, points="all")
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Nenhuma vaga com salário informado para a seleção atual.")

        st.subheader("Modalidade da Vaga")
        modalidade = filtered_df['uf'].apply(lambda x: 'Remoto' if x == 'Remoto' else 'Presencial')
        fig6 = px.pie(modalidade.value_counts(), values=modalidade.value_counts(), names=modalidade.value_counts().index, hole=.3)
        st.plotly_chart(fig6, use_container_width=True)

    # --- Histograma dos salários (continua) ---
    st.markdown("---")
    st.subheader("Distribuição de Salários")
    df_salario = filtered_df.dropna(subset=['salario_valor'])
    if not df_salario.empty:
        fig = px.histogram(df_salario, x="salario_valor", nbins=20, title="Distribuição de Salários")
        fig.update_layout(xaxis_title="Salário (R$)", yaxis_title="Quantidade de Vagas")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma vaga com salário informado para a seleção atual.")

    st.markdown("---")
    st.subheader("Dados Brutos")
    st.dataframe(filtered_df)
