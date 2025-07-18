# scraper.py
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configuração do logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# URL alvo (exemplo, precisa ser ajustada para o site real)
URL = "https://www.vagas.com.br/vagas-de-analista-de-dados-em-sao-paulo" # URL de exemplo

def fetch_jobs():
    """Busca dados de vagas e salva em um CSV."""
    logging.info("Iniciando o processo de web scraping.")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(URL, headers=headers)
        response.raise_for_status() # Lança um erro para respostas ruins (4xx ou 5xx)
        
        logging.info("Página carregada com sucesso.")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ATENÇÃO: As classes abaixo são exemplos! Você deve inspecionar o site
        # para encontrar as classes e tags corretas.
        job_cards = soup.find_all('li', class_='vaga odd ') 
        
        job_list = []
        for card in job_cards:
            title = card.find('h2', class_='cargo').text.strip()
            company = card.find('span', class_='emprVaga').text.strip()
            location = card.find('div', class_='vaga-local').text.strip()
            
            job_list.append({'titulo': title, 'empresa': company, 'localizacao': location})
            
        logging.info(f"{len(job_list)} vagas encontradas.")
        
        # Salva em um DataFrame e depois em CSV
        df = pd.DataFrame(job_list)
        df.to_csv('vagas_dados.csv', index=False)
        logging.info("Dados salvos com sucesso em vagas_dados.csv.")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao fazer a requisição HTTP: {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    fetch_jobs()