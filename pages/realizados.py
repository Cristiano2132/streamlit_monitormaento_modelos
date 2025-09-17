import streamlit as st
import pandas as pd
import plotly.express as px
from utils.utils import format_brl_volume

# -----------------------------
# Função de plot para taxas de default em %
# -----------------------------
def plot_default_rates(df):
    """
    Gráfico de linha: taxa realizada em cinza contínua e estimada em azul pontilhada.
    Valores convertidos para %
    """
    df_pivot = df.pivot(index="date", columns="metric_name", values="metric_value").reset_index()

    for col in ["taxa_default_realizada", "taxa_default_estimada"]:
        df_pivot[col] = df_pivot[col].astype(float) * 100

    fig = px.line(
        df_pivot,
        x="date",
        y=["taxa_default_realizada", "taxa_default_estimada"],
        markers=True,
        labels={"date": "Data", "value": "Taxa de Default (%)", "variable": "Métrica"}
    )

    fig.update_traces(
        selector=dict(name="taxa_default_realizada"),
        line=dict(color="gray"),
        name="Realizada (%)"
    )
    fig.update_traces(
        selector=dict(name="taxa_default_estimada"),
        line=dict(color="blue", dash="dot"),
        name="Estimada (%)"
    )

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Taxa de Default (%)",
        template="plotly_white",
        hovermode="x unified"
    )
    fig.update_yaxes(ticksuffix="%")

    return fig

# -----------------------------
# Função de plot para erro de PD
# -----------------------------
def plot_pd_error(df, vol, error_view="Taxa (%)", graph_height=350):
    """
    Gráfico de linha: erro de PD
    Pode ser exibido em Taxa (%) ou Valor Monetário (R$)
    """
    df_pivot = df.pivot(index="date", columns="metric_name", values="metric_value").reset_index()

    for col in ["taxa_default_realizada", "taxa_default_estimada"]:
        df_pivot[col] = df_pivot[col].astype(float)

    if error_view == "Taxa (%)":
        df_pivot["erro_pd"] = (df_pivot["taxa_default_estimada"] - df_pivot["taxa_default_realizada"]) * 100
        yaxis_title = "Erro de PD (%)"
        yaxis_range = [-5, 5]
        ticksuffix = "%"
    else:
        df_pivot["erro_pd"] = (df_pivot["taxa_default_estimada"] - df_pivot["taxa_default_realizada"]) * vol
        yaxis_title = "Erro de PD (R$)"
        yaxis_range = None
        ticksuffix = ""

    fig = px.line(
        df_pivot,
        x="date",
        y="erro_pd",
        markers=True,
        labels={"date": "Data", "erro_pd": yaxis_title}
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Erro zero", annotation_position="bottom left")
    fig.update_traces(line=dict(color="blue"), marker=dict(size=8), name="Erro")
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title=yaxis_title,
        template="plotly_white",
        hovermode="x unified",
        height=graph_height,
    )
    fig.update_yaxes(range=yaxis_range, ticksuffix=ticksuffix)

    return fig

# -----------------------------
# Função principal da página
# -----------------------------
def run():
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    df_models = st.session_state.get("models")
    df_metrics = st.session_state.get("metrics")

    if df_models is None or df_metrics is None:
        st.warning("⚠️ Dados não disponíveis. Verifique o carregamento no app principal.")
        return

    # -----------------------------
    # Sidebar: filtros
    # -----------------------------
    st.sidebar.header("⚙️ Filtros")
    model_options = df_models["name"].tolist()
    selected_model = st.sidebar.selectbox("Selecione o Modelo", model_options)
    model_id = df_models[df_models["name"] == selected_model]["id"].values[0]
    # Seleção do tipo de erro
    error_view = st.sidebar.selectbox("Exibir erro em:", ["Taxa (%)", "Valor Monetário (R$)"])
    st.sidebar.markdown("### Período de Visualização")
    df_metrics["date"] = pd.to_datetime(df_metrics["date"])
    start_date = st.sidebar.date_input("Data Início", value=df_metrics["date"].min())
    end_date = st.sidebar.date_input("Data Fim", value=df_metrics["date"].max())
    if start_date > end_date:
        st.sidebar.warning("⚠️ Data Início não pode ser maior que Data Fim.")


    # -----------------------------
    # Filtrar métricas de default
    # -----------------------------
    df_filtered = df_metrics[
        (df_metrics["model_id"] == model_id) &
        (df_metrics["metric_name"].isin(["taxa_default_realizada", "taxa_default_estimada"])) &
        (df_metrics["date"] >= pd.to_datetime(start_date)) &
        (df_metrics["date"] <= pd.to_datetime(end_date))
    ].sort_values("date")

    if df_filtered.empty:
        st.warning("⚠️ Não há dados disponíveis para este modelo.")
        return

    vol = df_models[df_models["name"] == selected_model]["vol_carteira"].values[0]

    # -----------------------------
    # Layout com 2 colunas
    # -----------------------------
    col1, col2 = st.columns([1, 3], gap="medium")

    # -----------------------------
    # Coluna esquerda: cards de informação
    # -----------------------------
    with col1:
        df_pivot = df_filtered.pivot(index="date", columns="metric_name", values="metric_value").reset_index()
        last_real_float = float(df_pivot["taxa_default_realizada"].values[-1])
        last_est_float = float(df_pivot["taxa_default_estimada"].values[-1])

        st.metric(label="Volume de Carteira", value=format_brl_volume(vol))
        st.metric(label="Última Taxa Realizada", value=f"{last_real_float*100:.2f}% | {format_brl_volume(last_real_float*vol)}")
        st.metric(label="Última Taxa Estimada", value=f"{last_est_float*100:.2f}% | {format_brl_volume(last_est_float*vol)}")

    # -----------------------------
    # Coluna direita: gráficos
    # -----------------------------
    with col2:
        graph_height = 350

        # Gráfico de taxas de default
        fig_rates = plot_default_rates(df_filtered)
        fig_rates.update_layout(height=graph_height)
        st.plotly_chart(fig_rates, use_container_width=True)

        # Gráfico de erro de PD
        fig_error = plot_pd_error(df_filtered, vol, error_view, graph_height)
        st.plotly_chart(fig_error, use_container_width=True)

    # -----------------------------
    # Tabela expandível
    # -----------------------------
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    with st.expander(f"Tabela completa de taxas de default: {selected_model}", expanded=False):
        st.dataframe(df_filtered, use_container_width=True)