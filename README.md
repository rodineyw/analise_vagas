# 📊 Dashboard de Análise de Vagas de Dados no Brasil

![Status do Projeto](https://img.shields.io/badge/status-ativo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-ff4b4b.svg)

## 🚀 Visão Geral do Projeto

Este projeto é uma solução completa de análise de dados que realiza web scraping diário no portal Vagas.com para coletar oportunidades de "Analista de Dados" em todo o Brasil. Os dados coletados são processados e apresentados em um dashboard interativo construído com Streamlit, que permite a visualização de insights sobre o mercado de trabalho, como distribuição de vagas por região, senioridade e tecnologias mais requisitadas.

---

### ✨ **[Acesse o Dashboard Ao Vivo](https://vagasad.streamlit.app/)** ✨


---

## 🎯 Principais Funcionalidades

* **Coleta de Dados Automatizada:** Um robô (scraper) desenvolvido com Python e Selenium visita o site Vagas.com diariamente.
* **Extração de Detalhes:** O scraper não só coleta os dados principais, mas também visita a página de cada vaga para extrair a descrição completa, permitindo uma análise de texto mais aprofundada.
* **Dashboard Interativo:** Uma interface amigável construída com Streamlit permite que os usuários filtrem os dados por UF, região e empresa.
* **Análises Relevantes:** O dashboard apresenta visualizações claras sobre:
  * Distribuição de vagas por estado e cidade.
  * Níveis de senioridade mais demandados (Júnior, Pleno, Sênior).
  * Tecnologias e ferramentas mais mencionadas nas descrições das vagas.
* **Atualização Diária:** O processo é 100% automatizado com GitHub Actions, garantindo que os dados estejam sempre atualizados.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **Linguagem:** Python 3.13
* **Web Scraping:** Selenium e BeautifulSoup4
* **Análise e Manipulação de Dados:** Pandas
* **Dashboard e Visualização:** Streamlit e Plotly Express
* **Automação (CI/CD):** GitHub Actions
* **Gerenciador de Pacotes:** UV

## ⚙️ Como Funciona (Arquitetura)

O projeto opera em um ciclo diário automatizado:

1. **Gatilho (Trigger):** Diariamente, um workflow do **GitHub Actions** é acionado.
2. **Execução do Scraper:** A automação executa o script `scraper_vagas.py`.
3. **Coleta de Dados:** O script utiliza o **Selenium** para abrir o site Vagas.com, simular a ação de clicar em "Carregar mais vagas" para expor todos os resultados e, em seguida, visita o link de cada vaga para extrair a descrição completa.
4. **Armazenamento:** Os dados limpos e estruturados são salvos em um arquivo `vagas_consolidadas.csv`.
5. **Commit Automático:** O GitHub Actions faz o commit e push do novo arquivo CSV para o repositório.
6. **Visualização:** O aplicativo **Streamlit** (`dashboard.py`), hospedado no Streamlit Community Cloud, lê o arquivo `vagas_consolidadas.csv` atualizado e exibe os dados no dashboard.

## 🔧 Configuração e Instalação Local

Para executar este projeto na sua máquina local, siga os passos abaixo.

**Pré-requisitos:**

* Python 3.10+
* [UV](https://github.com/astral-sh/uv) (gerenciador de pacotes) instalado.

**Passos:**

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/rodineyw/analise_vagas.git
    cd analise_vagas
    ```

2. **Crie e ative o ambiente virtual:**

    ```bash
    uv v .venv
    source .venv/bin/activate  # No Windows, use: .venv\Scripts\activate
    ```

3. **Instale as dependências:**

    ```bash
    uv pip install -r requirements.txt
    ```

## ▶️ Como Executar

Com o ambiente configurado, você pode rodar as duas partes do projeto:

1. **Para executar o scraper e coletar os dados mais recentes:**

    ```bash
    python scraper_vagas.py
    ```

    Aguarde a execução terminar. Um arquivo `vagas_consolidadas.csv` será criado ou atualizado.

2. **Para visualizar o dashboard:**

    ```bash
    streamlit run dashboard.py
    ```

    O Streamlit iniciará um servidor local e abrirá o dashboard no seu navegador.

## ✒️ Autor

* **Ródiney W.** - *Consultor de Software & Análise de Dados*
* **LinkedIn:** [https://www.linkedin.com/in/rodineyw/](https://www.linkedin.com/in/rodineyw/)
* **GitHub:** [https://github.com/rodineyw](https://github.com/rodineyw)

*(Sinta-se à vontade para adicionar seu email ou outras formas de contato)*

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
