import streamlit as st
from modules.risk_matrix import plot_risk_matrix

# -----------------------------
# Função principal da página
# -----------------------------
def run():
    """
    Página: Risco dos Modelos
    Exibe uma matriz de risco e permite visualizar a tabela de modelos.
    """
    st.title("Risco dos Modelos")

    # -----------------------------
    # Usar dados carregados no session_state
    # -----------------------------
    df = st.session_state.get("models")
    if df is None or df.empty:
        st.warning("⚠️ Não há dados de modelos disponíveis.")
        return

    # -----------------------------
    # Exibir tabela expandível
    # -----------------------------

    with st.expander("Ver tabela de modelos", expanded=False):
        st.dataframe(df.set_index("name"), use_container_width=True)

    # -----------------------------
    # Gerar e exibir a matriz de risco
    # -----------------------------
    fig = plot_risk_matrix(df)
    st.plotly_chart(fig, use_container_width=True)