# scraper_vagas.py
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
BASE_URL = "https://www.vagas.com.br/vagas-de-analista-de-dados"

def fetch_vagas_jobs():
    """
    Busca dados de vagas no Vagas.com, navegando por todas as páginas.
    """
    logging.info("Iniciando o scraping do Vagas.com.")
    
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
            
            # Usando um seletor que captura 'vaga odd' e 'vaga even'
            job_cards = soup.find_all('li', class_='vaga')
            
            if not job_cards:
                logging.info(f"Nenhuma vaga encontrada na página {page_num}. Fim do scraping.")
                break

            for card in job_cards:
                title_element = card.find('h2', class_='cargo')
                company_element = card.find('span', class_='emprVaga')
                location_element = card.find('span', class_='local')
                salary_element = card.find('span', class_='remuneracao')

                title = title_element.text.strip() if title_element else "N/A"
                company = company_element.text.strip() if company_element else "N/A"
                location = location_element.text.strip() if location_element else "N/A"
                salary = salary_element.text.strip() if salary_element else "A combinar"

                if title != "N/A":
                    all_jobs_list.append({
                        'titulo': title,
                        'empresa': company,
                        'localizacao': location,
                        'salario': salary,
                        'fonte': 'Vagas.com'
                    })
            
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

    df = pd.DataFrame(all_jobs_list).drop_duplicates()
    logging.info(f"Extração concluída. {len(df)} vagas válidas encontradas.")
    
    df.to_csv('vagas_consolidadas.csv', index=False, encoding='utf-8')
    logging.info("Dados salvos com sucesso em 'vagas_consolidadas.csv'.")

if __name__ == '__main__':
    fetch_vagas_jobs()
