# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import re
from typing import Optional

# --- Configuração da Página e Logging ---
st.set_page_config(layout="wide", page_title="Dashboard de Vagas de Dados - Brasil")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- FUNÇÃO CORRIGIDA E MAIS ROBUSTA ---
def get_region_from_location(location_str: str) -> str:
    """
    Mapeia a string de localização para uma região do Brasil de forma mais robusta.
    Identifica vagas remotas e busca pela sigla do estado no texto.
    """
    if not isinstance(location_str, str):
        return "Não especificada"

    # 1. Lida com vagas remotas primeiro
    if "home office" in location_str.lower() or "remoto" in location_str.lower():
        return "Remoto"

    # 2. Normaliza os separadores para um padrão único
    normalized_location = location_str.replace("/", "-")
    parts = [part.strip() for part in normalized_location.split('-')]

    # 3. Define todos os estados para uma busca eficiente
    all_states = {
        'SP', 'RJ', 'ES', 'MG', 'PR', 'SC', 'RS', 'MT', 'MS', 'GO', 'DF',
        'BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA', 'AM', 'RR',
        'AP', 'PA', 'TO', 'RO', 'AC'
    }

    # 4. Procura por uma sigla de estado válida em qualquer parte da localização
    found_state = None
    for part in parts:
        if part in all_states:
            found_state = part
            break  # Para a busca assim que encontrar o primeiro estado válido

    if not found_state:
        return "Não especificada"

    # 5. Mapeia o estado encontrado para a sua região
    sudeste = ['SP', 'RJ', 'ES', 'MG']
    sul = ['PR', 'SC', 'RS']
    centro_oeste = ['MT', 'MS', 'GO', 'DF']
    nordeste = ['BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE', 'PI', 'MA']
    norte = ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC']

    if found_state in sudeste: 
        return "Sudeste"
    if found_state in sul: 
        return "Sul"
    if found_state in centro_oeste: 
        return "Centro-Oeste"
    if found_state in nordeste: 
        return "Nordeste"
    if found_state in norte: 
        return "Norte"
    
    return "Não especificada"


def clean_salary(salary_str: str) -> Optional[float]:
    """Limpa a string de salário e a converte para um valor numérico (float)."""
    if not isinstance(salary_str, str) or "R$" not in salary_str:
        return None
    
    numbers = re.findall(r'\d+\.?\d*', salary_str.replace('.', '').replace(',', '.'))
    if numbers:
        return float(numbers[0])
    return None

@st.cache_data
def load_and_process_data() -> pd.DataFrame:
    """Carrega e processa os dados do CSV."""
    try:
        df = pd.read_csv('vagas_consolidadas.csv')
        df['regiao'] = df['localizacao'].apply(get_region_from_location)
        df['salario_valor'] = df['salario'].apply(clean_salary)
        logging.info("Dados carregados e processados com sucesso.")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'vagas_consolidadas.csv' não encontrado. Execute o scraper primeiro.")
        return pd.DataFrame()

# --- Layout do Dashboard ---

st.title("📊 Dashboard de Vagas de Dados no Brasil (Vagas.com)")

df: pd.DataFrame = load_and_process_data()

if not df.empty:
    # --- Barra Lateral com Filtros ---
    st.sidebar.header("Filtros")
    # A nova categoria "Remoto" será incluída automaticamente no filtro
    all_regions = sorted(df['regiao'].unique())
    selected_regions = st.sidebar.multiselect(
        "Selecione a Região",
        options=all_regions,
        default=all_regions
    )
    
    filtered_df = df[df['regiao'].isin(selected_regions)]

    # --- KPIs ---
    total_vagas = len(filtered_df)
    vagas_com_salario = filtered_df['salario_valor'].notna().sum()
    media_salarial = filtered_df['salario_valor'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vagas", f"{total_vagas}")
    col2.metric("Vagas com Salário", f"{vagas_com_salario}")
    col3.metric("Média Salarial (R$)", f"{media_salarial:,.2f}" if vagas_com_salario > 0 else "N/A")
    
    st.markdown("---")

    # --- Gráficos ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Empresas Contratando")
        top_empresas = filtered_df['empresa'].value_counts().nlargest(10)
        fig = px.bar(x=top_empresas.values, y=top_empresas.index, orientation='h', text_auto=True)
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Quantidade de Vagas", yaxis_title="Empresa")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Distribuição de Vagas por Região")
        vagas_por_regiao = filtered_df['regiao'].value_counts()
        fig = px.pie(vagas_por_regiao, names=vagas_por_regiao.index, values=vagas_por_regiao.values, hole=.3)
        st.plotly_chart(fig, use_container_width=True)

    # --- Análise de Salários ---
    st.markdown("---")
    st.subheader("Análise de Salários")
    df_salario = filtered_df.dropna(subset=['salario_valor'])
    
    if not df_salario.empty:
        fig = px.histogram(df_salario, x="salario_valor", nbins=20, title="Distribuição de Salários")
        fig.update_layout(xaxis_title="Salário (R$)", yaxis_title="Quantidade de Vagas")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma vaga com salário informado para a seleção atual.")


    # --- Tabela de Dados ---
    st.markdown("---")
    st.subheader("Dados Brutos")
    st.dataframe(filtered_df)
