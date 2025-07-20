import streamlit as st
import pandas as pd
import plotly.express as px
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
    if uf in sudeste: return "Sudeste"
    if uf in sul: return "Sul"
    if uf in centro_oeste: return "Centro-Oeste"
    if uf in nordeste: return "Nordeste"
    if uf in norte: return "Norte"
    if uf == "Remoto": return "Remoto"
    return "Não especificada"

@st.cache_data
def load_and_process_data() -> pd.DataFrame:
    try:
        df = pd.read_csv('vagas_consolidadas.csv')
        df['salario_valor'] = df['salario'].apply(clean_salary)
        df['regiao'] = df['uf'].apply(map_uf_to_regiao)
        logging.info("Dados carregados e processados com sucesso.")
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

    # KPIs
    total_vagas = len(filtered_df)
    vagas_com_salario = filtered_df['salario_valor'].notna().sum()
    media_salarial = filtered_df['salario_valor'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vagas", f"{total_vagas}")
    col2.metric("Vagas com Salário", f"{vagas_com_salario}")
    col3.metric("Média Salarial (R$)", f"{media_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")

    st.markdown("---")

    # Gráficos e demais análises como antes...

    # Exemplo de distribuição por região
    with st.expander("Distribuição por Região"):
        vagas_por_regiao = filtered_df['regiao'].value_counts()
        fig = px.pie(vagas_por_regiao, names=vagas_por_regiao.index, values=vagas_por_regiao.values, hole=.3)
        st.plotly_chart(fig, use_container_width=True)

    # Restante do dashboard segue igual
    st.subheader("Dados Brutos")
    st.dataframe(filtered_df)
