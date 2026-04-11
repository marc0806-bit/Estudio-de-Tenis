import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import plotly.express as px
import os

#CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard del Ranking ATP",
    page_icon="🎾",
    layout="wide"
)

#TÍTULO
st.title("🎾 Dashboard del Ranking ATP (2016-2025) 🎾")
st.markdown("---")

#FUNCIÓN DE CARGA DE DATOS 
@st.cache_data
def load_and_clean_tennis_data(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)
    
    df = pd.read_csv(full_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filtros de tiempo y ranking
    df = df[(df['Date'].dt.year >= 2016) & (df['Date'].dt.year <= 2025)].copy()
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    # CREACIÓN DE LAS COLUMNAS DE RANKING DEL GANADOR Y PERDEDOR
    df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
    df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1'])
    
    return df

# Carga de datos

df = load_and_clean_tennis_data('Tenis.csv')
# CREACIÓN DE PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢 Estadísticos", 
    "📊 Comparación", 
    "💻 Distribución",  
    "🏆 Victorias"
])

# FUNCIONES PARA LAS PESTAÑAS 

with tab1:
  with tab1:
    st.header("🔢 Flujo de Procesamiento y Estadísticos")
    st.info("De la data original a las métricas de éxito (2016-2025)")

    # DATA ORIGINAL
    st.subheader("📂  Data Original (Sin filtrar)")
    df_raw = pd.read_csv('Tenis.csv') 
    st.dataframe(df_raw.head(5), use_container_width=True)
    st.caption(f"El archivo original contiene {df_raw.shape[0]} registros (partidos).")

    st.divider()

    # DATA FILTRADA
    st.subheader("🧹 Data Filtrada y Columnas Calculadas")
    columnas_clave = ['Date', 'Tournament', 'Winner', 'winner_rank', 'loser_rank']
    st.dataframe(df[columnas_clave].head(5), use_container_width=True)
    st.caption(f"Muestra de la población de estudio: {df.shape[0]} partidos de élite.")

    st.divider()

    # DATOS ESTADÍSTICOS CON UNIDADES
    st.subheader("📊 3. Estadísticos: Winner vs Loser")
    
    columnas_finales = ['winner_rank', 'loser_rank']
    
    if all(col in df.columns for col in columnas_finales):
        resumen_final = df[columnas_finales].describe()
        
        # Renombramos el índice para reflejar las unidades
        resumen_final.index = [
            'N° de Partidos (Frecuencia)', 
            'Promedio (Puesto en Ranking)', 
            'Desviación Estándar (Puestos)', 
            'Mínimo (Mejor Puesto)', 
            '25% (Cuartil 1)', 
            '50% (Mediana)', 
            '75% (Cuartil 3)', 
            'Máximo (Peor Puesto)'
        ]
        
        # Mostramos la tabla
        st.table(resumen_final)

        # INTERPRETACIÓN CON UNIDADES
        m_w = round(resumen_final.loc['Promedio (Puesto en Ranking)', 'winner_rank'], 1)
        m_l = round(resumen_final.loc['Promedio (Puesto en Ranking)', 'loser_rank'], 1)
        diff = round(m_l - m_w, 1)
        
        st.success(f"""
            **Interpretación de Unidades:**
            * El **ganador** promedio se ubica en el **puesto {m_w}** del ranking ATP.
            * El **perdedor** promedio se ubica en el **puesto {m_l}** del ranking ATP.
            * Existe una brecha de rendimiento de **{diff} puestos** de diferencia a favor del ganador.
            
            **Análisis de Dispersión:** La desviación estándar nos indica cuántos **puestos** suele alejarse el jugador del promedio; una desviación menor en los ganadores indicaría que el éxito está más concentrado en la cima del ranking.
        """)
    else:
        st.error("Error: Las columnas calculadas no están disponibles.")

   

with tab2:
    st.header("📊 Comparación de Promedios")
    st.write("Contenido para la comparación de promedios aquí...")
    
with tab3:
    st.header("💻 Distribución de Rankings")
    st.write("Contenido para la distribución aquí")
    
with tab4:
   #GRÁFICO GLOBAL DE VICTORIAS Y BUSCADOR DE JUGADORES
    st.header("🏆 Top 50 Jugadores con más Victorias (2016-2025)")
    
    top_vics = df['Winner'].value_counts().head(50).reset_index()
    top_vics.columns = ['Jugador', 'Victorias']

    fig_global = px.bar(
        top_vics, 
        x='Jugador', 
        y='Victorias',
        color='Victorias',
        color_continuous_scale='Blues', 
        template='plotly_white'
    )
    fig_global.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_global, use_container_width=True)

    st.divider() # Separa el gráfico global del buscador

    # BUSCADOR DE JUGADORES
    st.header("🏆 Consulta de Victorias por Jugador del top 50")
    st.info("Solo se muestran jugadores que estuvieron en el Top 50 al momento del partido.")

    lista_jugadores = sorted(df['Winner'].dropna().unique())

    jugador_seleccionado = st.selectbox(
        "Busca o selecciona un jugador del Top 50:",
        options=lista_jugadores
    )

    if jugador_seleccionado:
        df_jugador = df[df['Winner'] == jugador_seleccionado].copy()
        num_victorias = len(df_jugador)

        st.divider() 

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Victorias Totales", value=num_victorias)
        with col2:
            ranking_promedio = round(df_jugador['Rank_1'].mean(), 1)
            st.metric(label="Ranking Promedio al ganar", value=ranking_promedio)

        st.subheader(f"📈 Evolución de victorias: {jugador_seleccionado}")
        
        victorias_anuales = df_jugador.groupby(df_jugador['Date'].dt.year).size().reset_index(name='Victorias')
        victorias_anuales.columns = ['Año', 'Cant. Victorias']

        if not victorias_anuales.empty:
            fig_evolucion = px.line(
                victorias_anuales, 
                x='Año', 
                y='Cant. Victorias',
                markers=True,
                color_discrete_sequence=['#00CC96']
            )
            st.plotly_chart(fig_evolucion, use_container_width=True)
        else:
            st.warning("No hay datos cronológicos suficientes para este jugador.")
   
        






    