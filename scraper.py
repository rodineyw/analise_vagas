# scraper.py
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Configuração do Logging ---
# Configura o logger para registrar informações úteis durante a execução.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"), # Salva logs em um arquivo
        logging.StreamHandler() # Mostra logs no console
    ]
)

# --- Constantes ---
URL = "https://www.vagas.com.br/vagas-de-analista-de-dados-em-sao-paulo"

def fetch_jobs():
    """
    Busca dados de vagas no site, processa e salva em um arquivo CSV.
    """
    logging.info("Iniciando o processo de web scraping.")
    try:
        # Usar um User-Agent comum para simular um navegador e evitar bloqueios.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        logging.info(f"Página '{URL}' carregada com sucesso.")

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- SELETOR CORRIGIDO ---
        # Em vez de 'li' com classe 'vaga odd', buscamos por 'section' com a classe 'vaga'.
        # Isso é mais geral e captura todas as vagas na página.
        job_cards = soup.find_all('li', class_='vaga')
        
        if not job_cards:
            logging.warning("Nenhum card de vaga encontrado. A estrutura do site pode ter mudado.")
            return

        job_list = []
        for card in job_cards:
            
            title_element = card.find('h2', class_='cargo')
            company_element = card.find('span', class_='emprVaga')
            location_element = card.find('div', class_='vaga-local')

            title = title_element.text.strip() if title_element else "N/A"
            company = company_element.text.strip() if company_element else "N/A"
            location = location_element.text.strip() if location_element else "N/A"

            if title != "N/A":
                job_list.append({
                    'titulo': title,
                    'empresa': company,
                    'localizacao': location,
                    'data_coleta': pd.to_datetime('today').strftime('%Y-%m-%d')
                })

        # A lógica de log e salvamento foi movida para fora do loop
        if not job_list:
            logging.info("Nenhuma vaga válida foi extraída nesta execução.")
            return

        logging.info(f"{len(job_list)} vagas encontradas e processadas.")

        df = pd.DataFrame(job_list)
        # Remove duplicatas para garantir dados limpos
        df.drop_duplicates(subset=['titulo', 'empresa', 'localizacao'], inplace=True)
        
        # Salva o arquivo com o nome correto para o dashboard
        df.to_csv('vagas_sp.csv', index=False, encoding='utf-8')
        logging.info("Dados salvos com sucesso em 'vagas_sp.csv'.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de rede ao tentar acessar a URL: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado durante o scraping: {e}", exc_info=True)

if __name__ == '__main__':
    fetch_jobs()