import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff  
import streamlit as st
import os

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Dashboard del Ranking ATP",
    page_icon="🎾",
    layout="wide"
)

# TÍTULO
st.title("🎾 Dashboard del Ranking ATP (2016-2025) 🎾")
st.markdown("---")

# FUNCIÓN DE CARGA DE DATOS 
@st.cache_data
def load_and_clean_tennis_data(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)
    
    # Cargamos el raw solo para tenerlo disponible
    df_raw = pd.read_csv(full_path)
    
    df = df_raw.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filtros de tiempo y ranking
    df = df[(df['Date'].dt.year >= 2016) & (df['Date'].dt.year <= 2025)].copy()
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    # CREACIÓN DE LAS COLUMNAS DE RANKING DEL GANADOR Y PERDEDOR
    df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
    df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1'])
    
    return df_raw, df

# Carga de datos única
df_raw, df = load_and_clean_tennis_data('Tenis.csv')

# CREACIÓN DE PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢 Estadísticos", 
    "📊 Comparación", 
    "💻 Distribución",  
    "🏆 Victorias"
])

# PESTAÑA 1: ESTADÍSTICOS
with tab1:
    st.header("🔢 Estadísticos de Ranking: Ganadores vs Perdedores")
    st.info("De la data original a las métricas de éxito (2016-2025)")

    # SECCIÓN DATA ORIGINAL
    st.subheader("📂 Data Original (Sin filtrar)")
    with st.expander("🔍 Ver Datos Crudos (Dataset Original Completo)"):
        st.write(f"Mostrando el dataset total: {df_raw.shape[0]} registros.")
        st.dataframe(df_raw, use_container_width=True)
    st.caption(f"El archivo original contiene {df_raw.shape[0]} registros (partidos).")

    st.divider()

    # SECCIÓN DATA FILTRADA
    st.subheader("🧹 Data Procesada (Con Filtros)")
    with st.expander("🧪 Ver Datos Crudos Filtrados (Procesados)"):
        st.write(f"Mostrando la muestra de estudio: {df.shape[0]} registros (Top 50 / 2016-2025).")
        st.dataframe(df, use_container_width=True)
    st.caption(f"Población de estudio final: {df.shape[0]} partidos de élite.")

    st.divider()

    # 3. ANÁLISIS INTERACTIVO (Corregida la indentación para que esté dentro de tab1)
    st.subheader("📊 Análisis Detallado: Winner vs Loser")

    opcion_analisis = st.radio(
        "Selecciona la métrica para profundizar en los datos:",
        options=["Ganadores (winner_rank)", "Perdedores (loser_rank)"],
        horizontal=True
    )

    col_seleccionada = 'winner_rank' if "Ganadores" in opcion_analisis else 'loser_rank'
    color_tema = '#00CC96' if col_seleccionada == 'winner_rank' else '#EF553B'

    if col_seleccionada in df.columns:
        stats = df[col_seleccionada].describe()
        
        col_graf, col_info = st.columns([1.5, 1])

        with col_graf:
            fig_interactiva = px.histogram(
                df, 
                x=col_seleccionada, 
                nbins=25,
                title=f"Distribución de Frecuencia: {opcion_analisis}",
                color_discrete_sequence=[color_tema],
                labels={col_seleccionada: 'Puesto en el Ranking'},
                template="plotly_dark"
            )
            fig_interactiva.update_layout(bargap=0.1, xaxis_range=[1, 51])
            st.plotly_chart(fig_interactiva, use_container_width=True)

        with col_info:
            st.write(f"### Resumen de {opcion_analisis}")
            resumen_vista = stats.to_frame()
            resumen_vista.index = [
                'Cantidad', 'Promedio', 'Desv. Estándar', 
                'Mínimo', '25% (Q1)', '50% (Mediana)', 
                '75% (Q3)', 'Máximo'
            ]
            st.dataframe(resumen_vista, use_container_width=True)

        promedio = round(stats['mean'], 1)
        mediana = int(stats['50%'])
        
        if col_seleccionada == 'winner_rank':
            st.success(f"""
                **Interpretación para Ganadores:**
                * El éxito está altamente concentrado en la parte superior: el **50% de los ganadores** se encuentran por debajo del puesto **{mediana}**.
                * El promedio de **{promedio}** confirma que el ranking es un predictor sólido de victoria.
            """)
        else:
            st.warning(f"""
                **Interpretación para Perdedores:**
                * La distribución es más dispersa. Aunque el promedio es de **{promedio}**, se observa que incluso jugadores de élite pierden con regularidad.
                * La frecuencia de derrotas aumenta a medida que el ranking se aleja del Top 10.
            """)

# PESTAÑA 2: COMPARACIÓN DE SERIES
with tab2:
    st.header("🎾 Densidad de Ganadores: ¿Dónde se concentra el talento?")
    st.write("""
        Este gráfico muestra la **densidad de probabilidad** de victoria según el ranking del jugador. 
        Nota cómo en los **Grand Slams**, la curva es mucho más alta cerca del Puesto 1.
    """)

    series_atp = {
        'Grand Slam': df[df['Series'] == 'Grand Slam']['winner_rank'].dropna(),
        'Masters 1000': df[df['Series'] == 'Masters 1000']['winner_rank'].dropna(),
        'ATP500': df[df['Series'] == 'ATP500']['winner_rank'].dropna(),
        'ATP250': df[df['Series'] == 'ATP250']['winner_rank'].dropna()
    }

    hist_data = [v for v in series_atp.values() if not v.empty]
    group_labels = [k for k, v in series_atp.items() if not v.empty]
    colores = ['green', 'blue', 'red', 'orange']  # Colores para cada serie 

    if hist_data:
        fig_densidad = ff.create_distplot(
            hist_data, 
            group_labels, 
            show_hist=False, 
            colors=colores[:len(group_labels)],
            curve_type='kde'
        )
        fig_densidad.update_layout(
            xaxis_title='Ranking del Ganador (Puestos)',
            yaxis_title='Densidad (Concentración de Éxito)',
            template='plotly_white',
            xaxis=dict(range=[1, 50])
        )
        st.plotly_chart(fig_densidad, use_container_width=True)
        st.info("**Interpretación Interactiva:** Un pico elevado indica una mayor frecuencia relativa de éxitos en ese rango específico.")
# PESTAÑA 3: DISTRIBUCIÓN DE ÉLITE
with tab3:
   
   
    st.header("💻 Nivel de Élite: Rondas Finales")
    
    #Métrica: Ranking promedio del partido
    df['rank_medio'] = (df['winner_rank'] + df['loser_rank']) / 2
    
    #Filtros básicos
    rondas_clave = ['Quarterfinals', 'Semifinals', 'The Final']
    df_elite = df[df['Round'].isin(rondas_clave)].copy()
    
    #Selector de Serie
    cat = st.selectbox("Categoría del Torneo:", ["Grand Slam", "Masters 1000"])
    df_cat = df_elite[df_elite['Series'] == cat]

    #Agrupación: Promedio y Conteo (para el tamaño de las burbujas)
    df_agrupado = df_cat.groupby(['Tournament', 'Round']).agg(
        promedio_rank=('rank_medio', 'mean'),
        num_partidos=('rank_medio', 'count')
    ).reset_index()

    #Gráfico de Burbujas Interactivo
    fig = px.scatter(
        df_agrupado,
        x="Round",
        y="promedio_rank",
        size="num_partidos", # El tamaño indica cuántos datos respaldan ese punto
        color="Tournament",
        hover_name="Tournament",
        title=f"Concentración de Élite en {cat}",
        labels={"promedio_rank": "Ranking Promedio", "num_partidos": "Partidos Analizados"},
        category_orders={"Round": rondas_clave},
        template="plotly_dark",
        size_max=30
    )

    # Invertir eje Y (1 es mejor que 50)
    fig.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
        **¿Cómo leer este gráfico?**
        * **Posición vertical:** Mientras más arriba esté la burbuja, mayor es el nivel del partido (rankings más bajos).
        * **Tamaño de la burbuja:** Representa el volumen de partidos. Burbujas grandes indican datos más robustos para tu análisis.
    """)
    
# PESTAÑA 4: VICTORIAS POR JUGADOR
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
   
        
