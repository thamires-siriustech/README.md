# Dashboard de anúncios de veículos

Aplicativo de análise exploratória desenvolvido com **Python, Pandas, Plotly e Streamlit**. O painel permite explorar uma base de anúncios de veículos usados nos Estados Unidos, filtrando os registros e comparando preço, quilometragem, ano e condição do veículo.

**Aplicativo publicado:** [Abrir o dashboard](https://dashboard-carros-4rpk.onrender.com)

## Pergunta de análise

Como os preços anunciados variam entre os veículos da amostra e como se relacionam com quilometragem, ano do modelo e condição informada?

## O que o painel oferece

- Filtros por faixa de preço, ano do modelo, modelo e condição.
- Indicadores da seleção: número de anúncios, preço mediano, quilometragem mediana e ano mediano.
- Histograma para investigar a distribuição de preços.
- Gráfico de dispersão para explorar a relação entre preço e quilometragem.
- Comparação do preço mediano por condição informada.
- Área de qualidade dos dados, com valores ausentes e tabela filtrada.

## Tecnologias

- **Python** — lógica e tratamento de dados
- **Pandas** — limpeza e análise
- **Plotly Express** — visualizações interativas
- **Streamlit** — interface do dashboard

## Como executar localmente

```bash
git clone https://github.com/thamires-siriustech/README.md.git
cd README.md
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O arquivo `vehicles_us.csv` deve ficar na mesma pasta que `app.py`. O caminho do arquivo é resolvido a partir da localização do próprio script, portanto o app não depende da pasta em que o terminal foi aberto.

## Interpretação e limitações

- A base representa **preços anunciados**, não valores finais de transação.
- A análise é descritiva: uma associação entre quilometragem e preço não prova causalidade.
- Campos ausentes podem reduzir a quantidade de registros disponíveis em algumas visualizações.
- Os resultados representam apenas a amostra incluída no arquivo `vehicles_us.csv`; não devem ser generalizados automaticamente para todo o mercado de usados.

## Estrutura

```
.
├── app.py
├── vehicles_us.csv
├── requirements.txt
└── notebooks/
    └── EDA.ipynb
```

---

Projeto de portfólio em análise de dados.
