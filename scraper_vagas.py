# scraper.py
import logging
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

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
# URL alterada para buscar em todo o Brasil
BASE_URL = "https://www.vagas.com.br/vagas-de-analista-de-dados"

def fetch_jobs():
    """
    Busca dados de vagas em TODAS as páginas do site, processa e salva em um arquivo CSV.
    """
    logging.info("Iniciando o processo de web scraping multi-página para todo o Brasil.")
    
    all_jobs_list = []
    page_num = 1
    
    while True:
        # Monta a URL para a página atual.
        current_url = f"{BASE_URL}?pagina={page_num}"
        logging.info(f"Buscando vagas na página: {current_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(current_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('li', class_='vaga')
            
            if not job_cards:
                logging.info(f"Nenhuma vaga encontrada na página {page_num}. Fim do scraping.")
                break

            page_jobs_found = 0
            for card in job_cards:
                title_element = card.find('h2', class_='cargo')
                company_element = card.find('span', class_='emprVaga')
                location_element = card.find('div', class_='vaga-local')
                # NOVO: Seletor para o salário
                salary_element = card.find('span', class_='remuneracao')

                title = title_element.text.strip() if title_element else "N/A"
                company = company_element.text.strip() if company_element else "N/A"
                location = location_element.text.strip() if location_element else "N/A"
                # NOVO: Extrai o texto do salário ou define como "A combinar"
                salary = salary_element.text.strip() if salary_element else "A combinar"

                if title != "N/A":
                    all_jobs_list.append({
                        'titulo': title,
                        'empresa': company,
                        'localizacao': location,
                        'salario': salary, # NOVO: Adiciona o salário na lista
                        'data_coleta': pd.to_datetime('today').strftime('%Y-%m-%d')
                    })
                    page_jobs_found += 1
            
            logging.info(f"{page_jobs_found} vagas encontradas na página {page_num}.")
            page_num += 1
            time.sleep(1) 

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de rede na página {page_num}: {e}. Interrompendo.")
            break
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado na página {page_num}: {e}", exc_info=True)
            break

    if not all_jobs_list:
        logging.warning("Nenhuma vaga foi coletada no total.")
        return

    logging.info(f"Processamento final: {len(all_jobs_list)} vagas totais encontradas.")

    df = pd.DataFrame(all_jobs_list)
    df.drop_duplicates(subset=['titulo', 'empresa', 'localizacao'], inplace=True)
    
    logging.info(f"Após remoção de duplicatas, restaram {len(df)} vagas únicas.")
    
    df.to_csv('vagas_brasil.csv', index=False, encoding='utf-8')
    logging.info("Dados salvos com sucesso em 'vagas_brasil.csv'.")


if __name__ == '__main__':
    fetch_jobs()
