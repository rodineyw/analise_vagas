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
# URL base, sem o número da página
BASE_URL = "https://www.vagas.com.br/vagas-de-analista-de-dados-em-sao-paulo"

def fetch_jobs():
    """
    Busca dados de vagas em TODAS as páginas do site, processa e salva em um arquivo CSV.
    """
    logging.info("Iniciando o processo de web scraping multi-página.")
    
    all_jobs_list = []
    page_num = 1
    
    while True:
        # Monta a URL para a página atual. Para a primeira página, não precisa do parâmetro.
        current_url = BASE_URL if page_num == 1 else f"{BASE_URL}?pagina={page_num}"
        logging.info(f"Buscando vagas na página: {current_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(current_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Usando o seletor que você mesmo ajustou: 'li' com a classe 'vaga'
            # Isso funciona para 'vaga odd' e 'vaga even'
            job_cards = soup.find_all('li', class_='vaga')
            
            # CONDIÇÃO DE PARADA: Se a página não tiver mais vagas, interrompe o loop.
            if not job_cards:
                logging.info(f"Nenhuma vaga encontrada na página {page_num}. Fim do scraping.")
                break

            page_jobs_found = 0
            for card in job_cards:
                title_element = card.find('h2', class_='cargo')
                company_element = card.find('span', class_='emprVaga')
                # O seletor correto para o local, que pode estar dentro de um span ou div
                location_element = card.find('span', class_='local') or card.find('div', class_='vaga-local')

                title = title_element.text.strip() if title_element else "N/A"
                company = company_element.text.strip() if company_element else "N/A"
                location = location_element.text.strip() if location_element else "N/A"

                if title != "N/A":
                    all_jobs_list.append({
                        'titulo': title,
                        'empresa': company,
                        'localizacao': location,
                        'data_coleta': pd.to_datetime('today').strftime('%Y-%m-%d')
                    })
                    page_jobs_found += 1
            
            logging.info(f"{page_jobs_found} vagas encontradas na página {page_num}.")
            
            # Prepara para buscar a próxima página
            page_num += 1
            
            # Boa prática: uma pequena pausa para não sobrecarregar o servidor do site.
            time.sleep(1) 

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro de rede na página {page_num}: {e}. Interrompendo.")
            break
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado na página {page_num}: {e}", exc_info=True)
            break

    # --- Processamento final após coletar de todas as páginas ---
    if not all_jobs_list:
        logging.warning("Nenhuma vaga foi coletada no total. Verifique os seletores e a estrutura do site.")
        return

    logging.info(f"Processamento final: {len(all_jobs_list)} vagas totais encontradas em {page_num - 1} páginas.")

    df = pd.DataFrame(all_jobs_list)
    df.drop_duplicates(subset=['titulo', 'empresa', 'localizacao'], inplace=True)
    
    logging.info(f"Após remoção de duplicatas, restaram {len(df)} vagas únicas.")
    
    df.to_csv('vagas_sp.csv', index=False, encoding='utf-8')
    logging.info("Dados salvos com sucesso em 'vagas_sp.csv'.")


if __name__ == '__main__':
    fetch_jobs()
