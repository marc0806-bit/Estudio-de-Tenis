import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard del Ranking ATP como Indicador de Éxito en el Tenis",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. TÍTULO Y DESCRIPCIÓN
st.title("🎾 Dashboard del Ranking ATP como Indicador de Éxito en el Tenis de Elite (2016-2025) 🎾")
st.markdown("---")
st.markdown("Evaluar la robustez del ranking ATP como un descriptor del desempeño real en el tenis de élite.")


@st.cache_data
def load_and_clean_tennis_data(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)
    
    df = pd.read_csv(full_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filtros de tiempo y ranking (Top 50)
    df = df[(df['Date'].dt.year >= 2016) & (df['Date'].dt.year <= 2025)].copy()
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    return df


try:
    df = load_and_clean_tennis_data('Tenis.csv')

    # 4. CREACIÓN DE PESTAÑAS (Corregido el anidamiento)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔢 Estadísticos", 
        "📊 Comparación", 
        "💻 Distribución",  
        "🏆 Victorias"
    ])

    with tab1:
        st.header("🔢 Estadísticos de los Ganadores del Top 50")
       

    with tab2:
        st.header("📊 Comparación de Promedios por Superficie")
        

    with tab3:
        st.header("💻 Distribución de Rankings")
        
    with tab4:
        st.header("🏆 Número de victorias de los jugadores top50")
        
except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {e}")
        






    