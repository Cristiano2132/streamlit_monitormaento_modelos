import streamlit as st
from utils.utils import format_brl_volume
from modules.graficos import plot_metric_interactive
import pandas as pd

# -----------------------------
# Função principal da página
# -----------------------------
def run():
    """
    Página: Performance de Modelos
    Inclui sidebar de filtros (modelo, métrica, período), cards de informações,
    gráfico interativo e tabela completa de métricas.
    """
    
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)  # Espaçamento superior

    # -----------------------------
    # Obter dados do session_state
    # -----------------------------
    df_models = st.session_state.get("models")
    df_metrics = st.session_state.get("metrics")
    df_metrics_desc = st.session_state.get("metricas_info")

    if df_models is None or df_metrics is None or df_metrics_desc is None:
        st.warning("⚠️ Dados não disponíveis. Verifique o carregamento no app principal.")
        return

    # -----------------------------
    # Sidebar: filtros
    # -----------------------------
    st.sidebar.header("⚙️ Filtros")

    # Seleção do modelo
    model_options = df_models["name"].tolist()
    selected_model = st.sidebar.selectbox("Selecione o Modelo", model_options)
    model_id = df_models[df_models["name"] == selected_model]["id"].values[0]
    
    # -----------------------------
    # Seleção da métrica (apenas do tipo "performance")
    # -----------------------------
    metrics_desc_performance = df_metrics_desc[df_metrics_desc["type"] == "stability"]["metric_name"].tolist()

    metrics_model = df_metrics[
        (df_metrics["model_id"] == model_id) &
        (df_metrics["metric_name"].isin(metrics_desc_performance))
    ]["metric_name"].unique().tolist()

    selected_metric = st.sidebar.selectbox("Selecione a Métrica", metrics_model)
    
    # -----------------------------
    # Seleção do período
    # -----------------------------
    st.sidebar.markdown("### Período de Visualização")
    df_metrics["date"] = pd.to_datetime(df_metrics["date"])
    start_date = st.sidebar.date_input("Data Início", value=df_metrics["date"].min())
    end_date = st.sidebar.date_input("Data Fim", value=df_metrics["date"].max())

    if start_date > end_date:
        st.sidebar.warning("⚠️ Data Início não pode ser maior que Data Fim.")

    # -----------------------------
    # Filtrar dados pelo modelo, métrica e período
    # -----------------------------
    df_filtered = df_metrics[
        (df_metrics["model_id"] == model_id) &
        (df_metrics["metric_name"] == selected_metric) &
        (df_metrics["date"] >= pd.to_datetime(start_date)) &
        (df_metrics["date"] <= pd.to_datetime(end_date))
    ].sort_values("date")

    # -----------------------------
    # Layout com 2 colunas
    # -----------------------------
    col1, col2 = st.columns([1, 3], gap="medium")

    # -----------------------------
    # Coluna esquerda: cards de informação
    # -----------------------------
    with col1:
        # Último valor da métrica
        last_metric_val = df_filtered["metric_value"].values[-1] if not df_filtered.empty else None

        # Volume de carteira do modelo
        vol = df_models[df_models["name"] == selected_model]["vol_carteira"].values[0]
        st.metric(label="Volume de Carteira", value=format_brl_volume(vol))

        if last_metric_val is not None:
            st.metric(label=f"{selected_metric}", value=last_metric_val, delta=None)
        else:
            st.warning("⚠️ Não há dados disponíveis para este modelo/métrica.")

    # -----------------------------
    # Coluna direita: gráfico interativo
    # -----------------------------
    with col2:
        st.subheader(f"Performance do Modelo: {selected_model}")

        if df_filtered.empty:
            st.warning("⚠️ Não há dados disponíveis para este modelo/métrica.")
        else:
            # Obter thresholds da métrica, se existirem
            thresholds_row = df_metrics_desc[df_metrics_desc["metric_name"] == selected_metric]
            thresholds = {}
            if not thresholds_row.empty:
                thresholds["attention"] = thresholds_row["attention"].values[0]
                thresholds["alert"] = thresholds_row["alert"].values[0]

            # Gerar gráfico interativo Plotly
            fig = plot_metric_interactive(df_filtered, selected_metric, thresholds)
            st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Tabela expandível de métricas
    # -----------------------------
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    with st.expander(f"Tabela completa das métricas do modelo: {selected_model}", expanded=False):
        if df_filtered.empty:
            st.warning("⚠️ Não há métricas disponíveis para este modelo.")
        else:
            st.dataframe(df_filtered, use_container_width=True)

    # -----------------------------
    # CSS personalizado para os cards
    # -----------------------------
    st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #393939;
        text-align: center;
        padding: 25px 0;
        border-radius: 0px;
        margin-bottom: 15px;
        min-width: 180px;
        color: white;
    }
    [data-testid="stMetricLabel"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)