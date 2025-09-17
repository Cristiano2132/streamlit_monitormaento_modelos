import streamlit as st

def load_css(file_name: str):
    """Carrega um arquivo CSS externo e aplica no app Streamlit"""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Função para formatar valores monetários ---
def format_brl_volume(value):
    """
    Formata um valor numérico em R$ com K, M, Bi
    """
    abs_val = abs(value)
    if abs_val >= 1_000_000_000:
        formatted = f"R$ {value/1_000_000_000:.1f} Bi"
    elif abs_val >= 1_000_000:
        formatted = f"R$ {value/1_000_000:.1f} M"
    elif abs_val >= 1_000:
        formatted = f"R$ {value/1_000:.1f} K"
    else:
        formatted = f"R$ {value}"
    return formatted
