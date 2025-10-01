import streamlit as st
import pandas as pd
from utils.utils import format_brl_volume
from modules.metrics import prepare_default_rates, calculate_error
from modules.graficos import plot_default_rates, plot_n_contratos, plot_pd_error

def run():
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    df_models = st.session_state.get("models")
    df_metrics = st.session_state.get("metrics")

    if df_models is None or df_metrics is None:
        st.warning("⚠️ Dados não disponíveis.")
        return

    # --- Sidebar ---
    st.sidebar.header("⚙️ Filtros")
    model_options = df_models["name"].tolist()
    selected_model = st.sidebar.selectbox("Selecione o Modelo", model_options)
    model_id = df_models.query("name == @selected_model")["id"].values[0]

    error_view = st.sidebar.selectbox("Exibir erro em:", ["Taxa (%)", "Valor Monetário (R$)"])
    st.sidebar.markdown("### Período")
    df_metrics["date"] = pd.to_datetime(df_metrics["date"])
    start_date = st.sidebar.date_input("Início", value=df_metrics["date"].min())
    end_date = st.sidebar.date_input("Fim", value=df_metrics["date"].max())

    if start_date > end_date:
        st.sidebar.warning("⚠️ Data Início > Data Fim.")
        return

    # --- Filtragem ---
    df_filtered = df_metrics.query(
        "model_id == @model_id and metric_name in ['taxa_default_realizada','taxa_default_estimada'] "
        "and @start_date <= date <= @end_date"
    ).sort_values("date")

    if df_filtered.empty:
        st.warning("⚠️ Sem dados para este modelo.")
        return

    vol = df_models.query("name == @selected_model")["vol_carteira"].values[0]

    # --- Layout principal ---
    col1, col2 = st.columns([1, 3], gap="medium")

    with col1:
        df_pivot = df_filtered.pivot(index="date", columns="metric_name", values="metric_value").reset_index()
        last_real = float(df_pivot["taxa_default_realizada"].values[-1])
        last_est = float(df_pivot["taxa_default_estimada"].values[-1])

        st.metric("Volume Carteira", format_brl_volume(vol))
        st.metric("Última Realizada", f"{last_real*100:.2f}% | {format_brl_volume(last_real*vol)}")
        st.metric("Última Estimada", f"{last_est*100:.2f}% | {format_brl_volume(last_est*vol)}")

    with col2:
        df_rates = prepare_default_rates(df_filtered)
        st.plotly_chart(plot_default_rates(df_rates), use_container_width=True)

        df_error, ytitle, yrange, tsuffix = calculate_error(df_filtered, vol, error_view)
        st.plotly_chart(plot_pd_error(df_error, ytitle, yrange, tsuffix), use_container_width=True)
        

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    with st.expander(f"Tabela completa de taxas: {selected_model}", expanded=False):
        st.dataframe(df_filtered, use_container_width=True)