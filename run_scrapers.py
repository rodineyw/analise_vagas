# run_scrapers.py
import logging
import pandas as pd
from scraper_vagas import fetch_jobs as fetch_vagas_jobs
from scraper_linkedin import fetch_linkedin_jobs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Iniciando o processo de coleta de todas as fontes.")
    
    # Executa os scrapers
    fetch_vagas_jobs()
    fetch_linkedin_jobs()
    
    # Consolida os resultados
    logging.info("Consolidando os dados coletados.")
    try:
        df_vagas = pd.read_csv('vagas_brasil.csv')
        df_vagas['fonte'] = 'Vagas.com'
        
        df_linkedin = pd.read_csv('vagas_linkedin.csv')
        
        # Concatena os dois DataFrames
        df_final = pd.concat([df_vagas, df_linkedin], ignore_index=True)
        
        # Remove duplicatas
        df_final.drop_duplicates(subset=['titulo', 'empresa', 'localizacao'], inplace=True)
        
        df_final.to_csv('vagas_consolidadas.csv', index=False, encoding='utf-8')
        logging.info(f"Dados consolidados e salvos em 'vagas_consolidadas.csv'. Total de {len(df_final)} vagas únicas.")
        
    except FileNotFoundError:
        logging.error("Um dos arquivos de dados não foi encontrado. Abortando a consolidação.")
    except Exception as e:
        logging.error(f"Erro ao consolidar os dados: {e}", exc_info=True)

if __name__ == '__main__':
    main()
