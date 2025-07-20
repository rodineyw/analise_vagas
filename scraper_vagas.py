# scraper_vagas.py
import logging
import re  # Importa a biblioteca de expressões regulares
import time

import pandas as pd
import requests  # Importa a biblioteca requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

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

def fetch_vagas_jobs():
    """
    Busca dados de vagas no Vagas.com, clica em "Carregar mais" e depois visita cada vaga para extrair a descrição completa.
    """
    logging.info("Iniciando o scraping do Vagas.com com Selenium.")
    
    # --- Configurações do Selenium ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.page_load_strategy = 'eager'

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.set_page_load_timeout(60)
    
    all_jobs_list = []
    
    try:
        driver.get(BASE_URL)
        logging.info("Página do Vagas.com carregada.")

        # --- Etapa 1: Carregar todas as vagas na página principal ---
        while True:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "maisVagas"))
                )
                driver.execute_script("arguments[0].click();", load_more_button)
                logging.info("Botão 'Carregar mais vagas' clicado.")
                time.sleep(2) 
            except TimeoutException:
                logging.info("Botão 'Carregar mais vagas' não encontrado. Todas as vagas foram carregadas.")
                break 
            except (ElementClickInterceptedException, WebDriverException):
                logging.warning("Clique falhou, tentando rolar a página.")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

        # --- Etapa 2: Extrair links e visitar cada página de detalhe ---
        logging.info("Extraindo dados e links de todas as vagas carregadas...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_cards = soup.find_all('li', class_='vaga')
        logging.info(f"Analisando {len(job_cards)} cards encontrados na página.")

        for card in job_cards:
            title_element = card.find('h2', class_='cargo')
            company_element = card.find('span', class_='emprVaga')
            location_element = card.find('div', class_='vaga-local')
            link_element = card.find('a', class_='link-detalhes-vaga')

            title = title_element.text.strip() if title_element else "N/A"
            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"
            
            if title == "N/A" or not link_element:
                continue

            # Extrai o UF da localização
            uf = "Remoto"
            if "home office" not in location.lower() and "remoto" not in location.lower() and isinstance(location, str):
                uf_search = re.search(r'\b([A-Z]{2})\b', location)
                uf = uf_search.group(1) if uf_search else "N/A"

            # --- Visita a página de detalhes para pegar a descrição ---
            job_url = "https://www.vagas.com.br" + link_element['href']
            description = "Descrição não encontrada"
            try:
                job_page_response = requests.get(job_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                job_soup = BeautifulSoup(job_page_response.content, 'html.parser')
                description_element = job_soup.find('div', class_='job-description__text')
                if description_element:
                    description = description_element.get_text(separator='\n').strip()
                time.sleep(0.5) # Pausa para não sobrecarregar o servidor
            except Exception as e:
                logging.warning(f"Não foi possível buscar a descrição da vaga {title}: {e}")

            all_jobs_list.append({
                'titulo': title,
                'empresa': company,
                'localizacao': location,
                'uf': uf,
                'descricao': description, # Adiciona a descrição completa
                'fonte': 'Vagas.com'
            })

    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado durante o scraping: {e}", exc_info=True)
    finally:
        driver.quit() 

    if not all_jobs_list:
        logging.warning("Nenhuma vaga foi coletada no total.")
        return

    df = pd.DataFrame(all_jobs_list).drop_duplicates(subset=['titulo', 'empresa', 'localizacao'])
    logging.info(f"Extração concluída. {len(df)} vagas válidas encontradas.")
    
    df.to_csv('vagas_consolidadas.csv', index=False, encoding='utf-8')
    logging.info("Dados salvos com sucesso em 'vagas_consolidadas.csv'.")

if __name__ == '__main__':
    fetch_vagas_jobs()
