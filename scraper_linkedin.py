# scraper_linkedin.py
import logging
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes ---
# URL de busca de vagas de "Analista de Dados" no Brasil
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/?keywords=analista%20de%20dados&location=Brasil"

def fetch_linkedin_jobs():
    """
    Busca dados de vagas no LinkedIn usando Selenium, rolando a página para carregar todos os resultados.
    """
    logging.info("Iniciando o scraping do LinkedIn com Selenium.")
    
    # --- Configurações do Selenium ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Roda o Chrome em modo "invisível"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Instala e gerencia o driver do Chrome automaticamente
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    job_list = []
    
    try:
        driver.get(LINKEDIN_URL)
        logging.info("Página do LinkedIn carregada.")
        
        # Espera inicial para a página carregar
        time.sleep(3)

        # --- Lógica de Scroll para carregar todas as vagas ---
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logging.info("Rolando a página para carregar mais vagas...")
            time.sleep(4)  # Espera para o conteúdo carregar
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Para de rolar se a altura da página não mudar mais
            last_height = new_height

        logging.info("Todos os resultados foram carregados. Iniciando extração.")
        
        # Encontra os cards de vagas
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        
        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, 'a.job-card-container__link').text.strip()
                company = card.find_element(By.CSS_SELECTOR, 'div.base-search-card__subtitle').text.strip()
                location = card.find_element(By.CSS_SELECTOR, 'ul.job-card-container__metadata-wrapper').text.strip()
                
                job_list.append({
                    'titulo': title,
                    'empresa': company,
                    'localizacao': location,
                    'salario': "A combinar", # LinkedIn raramente mostra salário na lista
                    'fonte': 'LinkedIn'
                })
            except Exception:
                # Ignora cards que não são vagas (ex: "veja mais vagas")
                continue
                
        logging.info(f"Encontradas {len(job_list)} vagas no LinkedIn.")

    except Exception as e:
        logging.error(f"Ocorreu um erro durante o scraping do LinkedIn: {e}", exc_info=True)
    finally:
        driver.quit() # Garante que o navegador seja fechado

    if job_list:
        df = pd.DataFrame(job_list)
        df.to_csv('vagas_linkedin.csv', index=False, encoding='utf-8')
        logging.info("Dados do LinkedIn salvos com sucesso em 'vagas_linkedin.csv'.")
    
    return job_list

if __name__ == '__main__':
    fetch_linkedin_jobs()
