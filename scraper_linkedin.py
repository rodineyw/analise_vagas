# scraper_linkedin.py
import logging
import os
import time

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração do Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constantes ---
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/?currentJobId=4266438599&geoId=106057199&keywords=analista%20de%20dados&origin=JOB_SEARCH_PAGE_LOCATION_AUTOCOMPLETE&originalSubdomain=br&refresh=true"

def fetch_linkedin_jobs():
    """
    Busca dados de vagas no LinkedIn, realizando login e navegando pela paginação.
    """
    logging.info("Iniciando o scraping do LinkedIn com Selenium.")
    
    # --- Pega as credenciais do ambiente ---
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    if not linkedin_email or not linkedin_password:
        logging.error("Credenciais do LinkedIn não encontradas. Verifique seu arquivo .env ou os Secrets do GitHub.")
        return []

    # --- Configurações do Selenium ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    all_jobs_list = []
    
    try:
        # --- ETAPA DE LOGIN ---
        driver.get("https://www.linkedin.com/login")
        logging.info("Página de login carregada. Tentando logar...")

        wait = WebDriverWait(driver, 10)
        
        email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_field.send_keys(linkedin_email)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(linkedin_password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        wait.until(EC.presence_of_element_located((By.ID, "global-nav-search")))
        logging.info("Login realizado com sucesso!")

        # --- FIM DA ETAPA DE LOGIN ---

        driver.get(LINKEDIN_URL)
        logging.info("Página de busca de vagas carregada.")
        
        page_num = 1
        while page_num <= 15:
            logging.info(f"Coletando vagas da página {page_num}...")
            
            # Rola a página para garantir que todos os cards estejam visíveis
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 

            job_cards = driver.find_elements(By.CSS_SELECTOR, "li.ember-view.SmCOUmLhQcYHCWzDxjUbFhltcDyHyxQmb.occludable-update.p0.relative.scaffold-layout__list-item")
            logging.info(f"Analisando {len(job_cards)} cards encontrados na página {page_num}...")

            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, 'div.full-width.artdeco-entity-lockup__title.ember-view').text.strip()
                    company = card.find_element(By.CSS_SELECTOR, 'div.artdeco-entity-lockup__subtitle.ember-view').text.strip()
                    location = card.find_element(By.CSS_SELECTOR, 'ul.job-card-container__metadata-wrapper').text.strip()
                    
                    if title and company and location:
                        all_jobs_list.append({'titulo': title, 'empresa': company, 'localizacao': location, 'salario': "A combinar", 'fonte': 'LinkedIn'})
                except NoSuchElementException:
                    continue
            
            try:
                next_button_selector = 'button[aria-label="Avançar"], button[aria-label="Ver próxima página"]'
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
                )
                driver.execute_script("arguments[0].click();", next_button)
                page_num += 1
            except TimeoutException:
                logging.info("Nenhum botão de próxima página encontrado. Fim da busca.")
                break 

    except Exception as e:
        logging.error(f"Ocorreu um erro durante o scraping do LinkedIn: {e}", exc_info=True)
    finally:
        driver.quit()

    if all_jobs_list:
        # Remove duplicatas que podem ocorrer entre as páginas
        df = pd.DataFrame(all_jobs_list).drop_duplicates()
        logging.info(f"Extração concluída. {len(df)} vagas válidas encontradas no total.")
        df.to_csv('vagas_linkedin.csv', index=False, encoding='utf-8')
        logging.info("Dados do LinkedIn salvos com sucesso.")
    else:
        logging.warning("Nenhuma vaga encontrada no LinkedIn. Criando arquivo vazio.")
        pd.DataFrame(columns=['titulo', 'empresa', 'localizacao', 'salario', 'fonte']).to_csv('vagas_linkedin.csv', index=False, encoding='utf-8')

    return all_jobs_list

if __name__ == '__main__':
    fetch_linkedin_jobs()
