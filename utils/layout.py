import streamlit as st

def setup_page(page_title: str, page_icon: str):
    """Configuração padrão para todas as páginas"""
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar comum a todas as páginas
    with st.sidebar:
        st.title("📌 Dashboard Multipage")
        st.markdown("---")
        st.write("Selecione uma página no menu acima 👆")
