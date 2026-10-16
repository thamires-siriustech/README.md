from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "vehicles_us.csv"

st.set_page_config(
    page_title="Análise de anúncios de veículos",
    page_icon="🚘",
    layout="wide",
)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Carrega a base e padroniza os campos numéricos usados na análise."""
    df = pd.read_csv(path)

    for column in ["price", "model_year", "odometer", "days_listed", "cylinders"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Registra dados sem preço para transparência; eles não entram nos gráficos de preço.
    df.attrs["rows_without_price"] = int(df["price"].isna().sum())
    return df


try:
    raw_data = load_data(str(DATA_PATH))
except (FileNotFoundError, pd.errors.ParserError, OSError) as error:
    st.error(
        "Não foi possível carregar a base de anúncios. "
        "Verifique se vehicles_us.csv está na mesma pasta de app.py."
    )
    st.exception(error)
    st.stop()

rows_without_price = int(raw_data.attrs.get("rows_without_price", 0))
data = raw_data.dropna(subset=["price"]).copy()

st.title("Análise exploratória de anúncios de veículos")
st.markdown(
    "Explore como **preço, ano do modelo, quilometragem e condição** "
    "variam na amostra de anúncios. Use os filtros laterais para investigar "
    "segmentos específicos."
)
st.caption(
    "Os valores são preços anunciados, não necessariamente preços finais de venda. "
    "Os resultados descrevem apenas os registros da base utilizada."
)

# Filtros
st.sidebar.header("Filtros")

price_min = int(data["price"].min())
price_max = int(data["price"].max())
if price_min < price_max:
    selected_price = st.sidebar.slider(
        "Faixa de preço (US$)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=max(1, int((price_max - price_min) / 100)),
    )
else:
    selected_price = (price_min, price_max)
    st.sidebar.caption(f"Preço disponível na base: US$ {price_min:,.0f}")

filtered = data[data["price"].between(*selected_price)].copy()

if "model_year" in filtered.columns:
    year_values = filtered["model_year"].dropna()
    if not year_values.empty:
        year_min = int(year_values.min())
        year_max = int(year_values.max())
        if year_min < year_max:
            selected_year = st.sidebar.slider(
                "Ano do modelo",
                min_value=year_min,
                max_value=year_max,
                value=(year_min, year_max),
            )
            # Mantém anúncios sem ano informado; valores ausentes ficam explícitos adiante.
            filtered = filtered[
                filtered["model_year"].between(*selected_year)
                | filtered["model_year"].isna()
            ]

if "model" in filtered.columns:
    models = sorted(filtered["model"].dropna().astype(str).unique().tolist())
    selected_models = st.sidebar.multiselect(
        "Modelo do veículo",
        options=models,
        default=[],
        help="Deixe vazio para incluir todos os modelos.",
    )
    if selected_models:
        filtered = filtered[filtered["model"].astype(str).isin(selected_models)]

if "condition" in filtered.columns:
    conditions = sorted(filtered["condition"].dropna().astype(str).unique().tolist())
    selected_conditions = st.sidebar.multiselect(
        "Condição informada no anúncio",
        options=conditions,
        default=conditions,
    )
    filtered = filtered[
        filtered["condition"].astype(str).isin(selected_conditions)
        | filtered["condition"].isna()
    ]

if filtered.empty:
    st.warning("Nenhum anúncio corresponde à combinação de filtros selecionada.")
    st.stop()

# Indicadores
st.subheader("Resumo da seleção")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Anúncios", f"{len(filtered):,}".replace(",", "."))
k2.metric("Preço mediano", f"US$ {filtered['price'].median():,.0f}")
if "odometer" in filtered.columns and filtered["odometer"].notna().any():
    k3.metric("Quilometragem mediana", f"{filtered['odometer'].median():,.0f} mi")
else:
    k3.metric("Quilometragem mediana", "Sem dados")
if "model_year" in filtered.columns and filtered["model_year"].notna().any():
    k4.metric("Ano mediano", f"{filtered['model_year'].median():.0f}")
else:
    k4.metric("Ano mediano", "Não disponível")

# Visualizações principais
left, right = st.columns(2)

with left:
    st.subheader("Distribuição dos preços")
    fig_price = px.histogram(
        filtered,
        x="price",
        nbins=40,
        labels={"price": "Preço anunciado (US$)", "count": "Número de anúncios"},
        title="Como os preços se distribuem na seleção",
    )
    fig_price.update_layout(
        yaxis_title="Número de anúncios",
        xaxis_title="Preço anunciado (US$)",
    )
    st.plotly_chart(fig_price, use_container_width=True)

with right:
    st.subheader("Preço × quilometragem")
    if "odometer" in filtered.columns:
        scatter_data = filtered.dropna(subset=["price", "odometer"]).copy()
    else:
        scatter_data = pd.DataFrame()

    if not scatter_data.empty:
        hover_columns = [
            c for c in ["model", "model_year", "condition", "transmission"]
            if c in scatter_data.columns
        ]
        scatter_kwargs = {}
        if "condition" in scatter_data.columns:
            scatter_kwargs["color"] = "condition"

        fig_scatter = px.scatter(
            scatter_data,
            x="odometer",
            y="price",
            opacity=0.55,
            hover_data=hover_columns,
            labels={
                "odometer": "Quilometragem (milhas)",
                "price": "Preço anunciado (US$)",
                "condition": "Condição",
            },
            title="Relação entre quilometragem e preço",
            **scatter_kwargs,
        )
        fig_scatter.update_layout(
            xaxis_title="Quilometragem (milhas)",
            yaxis_title="Preço anunciado (US$)",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Não há dados suficientes de quilometragem para montar o gráfico.")

if "condition" in filtered.columns:
    st.subheader("Preço mediano por condição")
    condition_summary = (
        filtered.dropna(subset=["condition"])
        .groupby("condition", as_index=False)
        .agg(preco_mediano=("price", "median"), anuncios=("price", "size"))
        .sort_values("preco_mediano", ascending=False)
    )
    if not condition_summary.empty:
        fig_condition = px.bar(
            condition_summary,
            x="condition",
            y="preco_mediano",
            text="preco_mediano",
            hover_data=["anuncios"],
            labels={
                "condition": "Condição",
                "preco_mediano": "Preço mediano (US$)",
                "anuncios": "Anúncios",
            },
            title="Comparação de preço por condição informada",
        )
        fig_condition.update_traces(
            texttemplate="US$ %{text:,.0f}",
            textposition="outside",
        )
        fig_condition.update_layout(
            yaxis_title="Preço mediano (US$)",
            xaxis_title="Condição",
        )
        st.plotly_chart(fig_condition, use_container_width=True)

# Transparência sobre os dados
with st.expander("Qualidade dos dados e tabela filtrada"):
    st.write(f"Linhas na base original: **{len(raw_data):,}**".replace(",", "."))
    st.write(
        f"Registros sem preço excluídos dos gráficos: **{rows_without_price:,}**".replace(",", ".")
    )
    missing = filtered.isna().sum().sort_values(ascending=False)
    st.write("Valores ausentes na seleção:")
    st.dataframe(
        missing.rename("Valores ausentes").reset_index().rename(
            columns={"index": "Coluna"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.dataframe(filtered.head(1000), use_container_width=True, hide_index=True)
