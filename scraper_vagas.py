# scraper_vagas.py
import logging
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# --- Configuração do Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

# --- Constantes ---
BASE_URL = "https://www.vagas.com.br/vagas-de-analista-de-dados"


ufs: set[str] = {'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'}

def extrair_uf(location_raw: str) -> str:
    """
    Estrai a sigla da UF de qualquer localização ou retorna 'Remoto' ou 'Não especificada'.
    """
    if not isinstance(location_raw, str):
        return "Não especificada"
    txt = location_raw.lower()
    if "remoto" in txt or "home office" in txt:
        return "Remoto"
    # Pega todas as possíveis UFs e retorna a primeira encontrada
    candidates = re.findall(r"\b([A-Z]{2})\b", location_raw.upper())
    for cand in candidates:
        if cand in ufs:
            return cand
    return "Não especificada"

def fetch_vagas_jobs():
    """
    Busca dados de vagas no Vagas.com usando Selenium para clicar em "Carregar mais vagas".
    """
    logging.info("Iniciando o scraping do Vagas.com com Selenium.")
    
    # --- Configurações do Selenium ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_jobs_list = []
    
    try:
        driver.get(BASE_URL)
        logging.info("Página do Vagas.com carregada.")

        # --- Lógica para clicar em "Carregar mais vagas" ---
        while True:
            try:
                # Espera o botão estar visível e clicável
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "maisVagas"))
                )
                driver.execute_script("arguments[0].click();", load_more_button)
                logging.info("Botão 'Carregar mais vagas' clicado.")
                time.sleep(2) # Espera o conteúdo carregar
            except TimeoutException:
                logging.info("Botão 'Carregar mais vagas' não encontrado. Todas as vagas foram carregadas.")
                break # Sai do loop se o botão não for mais encontrado
            except ElementClickInterceptedException:
                logging.warning("Clique interceptado, rolando a página para tentar novamente.")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

        # --- Extração dos dados após carregar tudo ---
        logging.info("Extraindo dados de todas as vagas carregadas...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_cards = soup.find_all('li', class_='vaga')
        logging.info(f"Analisando {len(job_cards)} cards encontrados na página.")

        for card in job_cards:
            title_element = card.find('h2', class_='cargo')
            company_element = card.find('span', class_='emprVaga')
            location_element = card.find('div', class_='vaga-local')
            salary_element = card.find('span', class_='remuneracao')

            title = title_element.text.strip() if title_element else "N/A"
            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            uf: str = extrair_uf(location)
            salary = salary_element.text.strip() if salary_element else "A combinar"

            if title != "N/A":
                all_jobs_list.append({
                    'titulo': title,
                    'empresa': company,
                    'localizacao': location,
                    'uf': uf,
                    'salario': salary,
                    'fonte': 'Vagas.com'
                })

    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado durante o scraping: {e}", exc_info=True)
    finally:
        driver.quit() # Garante que o navegador seja fechado

    if not all_jobs_list:
        logging.warning("Nenhuma vaga foi coletada no total.")
        return

    df = pd.DataFrame(all_jobs_list).drop_duplicates()
    logging.info(f"Extração concluída. {len(df)} vagas válidas encontradas.")
    
    df.to_csv('vagas_consolidadas.csv', index=False, encoding='utf-8')
    logging.info("Dados salvos com sucesso em 'vagas_consolidadas.csv'.")

if __name__ == '__main__':
    fetch_vagas_jobs()
