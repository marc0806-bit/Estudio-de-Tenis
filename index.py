import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import plotly.express as px
st.set_page_config(
    page_title="Dashboard del Ranking ATP como Indicador de Éxito en el Tenis",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)
#TÍTULO Y DESCRIPCIÓN
st.title("🎾Dashboard del Ranking ATP como Indicador de Éxito en el Tenis de Elite (2016-2025) 🎾")
st.markdown("---") # Separador visual
st.markdown("Evaluar la robustez del ranking ATP como un descriptor del desempeño  real en el tenis de élite.")
# Función con CACHE para cargar y procesar datos
@st.cache_data
def load_and_clean_tennis_data(path):
    # Cargar el CSV
    df = pd.read_csv(path)
    
    # Convertir fechas (tratar errores para no romper la app)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Aplicar filtros de tiempo (2016-2025)
    df = df[(df['Date'].dt.year > 2015) & (df['Date'].dt.year <= 2025)].copy()
    
    # Aplicar filtros de ranking (Ambos jugadores en el Top 50)
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    return df

#CREACIÓN DE PESTAÑAS
# Definimos los nombres y los iconos dentro de una lista
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢Estadísticos de los ganadores del top50", 
    "📊Comparación de Promedios", 
    "💻 Distribución de Rankings",  
    "🏆 Número de victorias de los jugadores top50"
])
with tab1:
    st.header("🔢Estadísticos de los Ganadores del Top 50")
    st.markdown("Se presentan estadísticas descriptivas de los jugadores que han alcanzado el top 50 en el ranking ATP.")
    
with tab2:


    with tab2:



        with tab3:
            st.header("💻 Distribución de Rankings")
            st.markdown("Visualización de la distribución de los rankings de los jugadores en el top 50.")

        with tab4:
            st.header("🏆 Número de victorias de los jugadores top50")
            st.markdown("Análisis del número de victorias obtenidas por los jugadores que han alcanzado el top 50.")
   