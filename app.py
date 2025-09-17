import streamlit as st
from streamlit_option_menu import option_menu

# Importa as páginas
import pages.risco as risco
import pages.performance as performance
import pages.estabilidade as estabilidade
import pages.realizados as realizados

import pandas as pd

# -----------------------------
# Configurações iniciais
# -----------------------------
# Aplica CSS global
css_file = "styles/light.css"
# Carrega CSS apenas para detalhes que o Streamlit não cobre
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Configuração da página
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
        options=["Risco", "Realizados","Performance", "Estabilidade"],
        icons=["shield-check", "bar-chart", "bar-chart", "activity"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# -----------------------------
# Roteamento para páginas
# -----------------------------
if selected == "Risco":
    risco.run()
elif selected == "Realizados":
    realizados.run()
elif selected == "Performance":
    performance.run()
elif selected == "Estabilidade":
    estabilidade.run()