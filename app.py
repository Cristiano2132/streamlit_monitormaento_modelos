import streamlit as st
from streamlit_option_menu import option_menu

# Importa as páginas
import pages.risco as risco
import pages.performance as performance
import pages.estabilidade as estabilidade

# Função utilitária para carregar CSS
from utils.utils import load_css  
import pandas as pd

# -----------------------------
# Aplicar estilo global
# -----------------------------
load_css("styles/styles.css")

# -----------------------------
# Configuração do Streamlit
# -----------------------------
st.set_page_config(
    page_title="Monitoramento de Modelos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Inicializar datasets no session_state
# -----------------------------
if "models" not in st.session_state:
    st.session_state["models"] = pd.read_csv("data/models.csv")

if "metrics" not in st.session_state:
    st.session_state["metrics"] = pd.read_csv("data/metrics.csv")

if "metricas_info" not in st.session_state:
    st.session_state["metricas_info"] = pd.read_csv("data/metricas_descricao.csv")

# -----------------------------
# Menu lateral
# -----------------------------
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["Risco", "Performance", "Estabilidade"],
        icons=["shield-check", "bar-chart", "activity"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# -----------------------------
# Roteamento para páginas
# -----------------------------
if selected == "Risco":
    risco.run()
elif selected == "Performance":
    performance.run()
elif selected == "Estabilidade":
    estabilidade.run()