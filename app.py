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

# TÍTULO Y ESTÉTICA
st.title("🎾 Dashboard del Ranking ATP (2016-2025) 🎾")
st.markdown("---")

#FUNCIÓN DE CARGA Y LIMPIEZA 
@st.cache_data # Cache para no recargar el CSV con cada clic
def load_and_clean_tennis_data(filename):
    # Localización del archivo en el directorio del script
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)
    
    # Lectura inicial
    df_raw = pd.read_csv(full_path)
    
    df = df_raw.copy()
    # Conversión de fechas a formato datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Filtro temporal: Rango de estudio 2016-2025
    df = df[(df['Date'].dt.year >= 2016) & (df['Date'].dt.year <= 2025)].copy()
    
    # Filtro de Calidad: Solo partidos donde ambos sean Top 50
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    # Lógica para asignar quién ganó y quién perdió según la columna 'Winner'
    df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
    df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1'])
    
    return df_raw, df

# Ejecución de la carga
df_raw, df = load_and_clean_tennis_data('Tenis.csv')

# ESTRUCTURA DE NAVEGACIÓN (PESTAÑAS)
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢 Estadísticos", 
    "📊 Comparación", 
    "💻 Distribución",  
    "🏆 Victorias"
])

#PESTAÑA 1: ANALISIS DESCRIPTIVO
with tab1:
    st.header("🔢 Estadísticos de Ranking: Ganadores vs Perdedores")
    st.info("De la data original a las métricas de éxito (2016-2025)")

    # Visualización de Dataframes crudos
    st.subheader("📂 Data Original (Sin filtrar)")
    with st.expander("🔍 Ver Datos Crudos (Dataset Original Completo)"):
        st.dataframe(df_raw, width='stretch')

    st.divider()

    st.subheader("🧹 Data Procesada (Con Filtros)")
    with st.expander("🧪 Ver Datos Crudos Filtrados (Procesados)"):
        st.dataframe(df, width='stretch')

    st.divider()

    # Histrogramas interactivos
    st.subheader("📊 Análisis Detallado: Winner vs Loser")
    opcion_analisis = st.radio(
        "Métrica para profundizar:",
        options=["Ganadores (winner_rank)", "Perdedores (loser_rank)"],
        horizontal=True,
        key="radio_stats"
    )

    # Configuración dinámica de colores según selección
    col_seleccionada = 'winner_rank' if "Ganadores" in opcion_analisis else 'loser_rank'
    color_tema = 'lightgreen' if col_seleccionada == 'winner_rank' else 'red'

    if col_seleccionada in df.columns:
        stats = df[col_seleccionada].describe()
        col_graf, col_info = st.columns([1.5, 1])

        with col_graf:
            # Creación del histograma de frecuencias
            fig_interactiva = px.histogram(
                df, x=col_seleccionada, nbins=25,
                title=f"Distribución de Frecuencia: {opcion_analisis}",
                color_discrete_sequence=[color_tema],
                labels={col_seleccionada: 'Puesto en el Ranking'},
                template="plotly_dark"
            )
            fig_interactiva.update_layout(bargap=0.1, xaxis_range=[1, 51])
            st.plotly_chart(fig_interactiva, width='stretch')

        with col_info:
            # Tabla de resumen estadístico (Media, Mediana, etc.)
            st.write(f"### Resumen de {opcion_analisis}")
            resumen_vista = stats.to_frame()
            resumen_vista.index = ['Cantidad', 'Promedio', 'Desv. Estándar', 'Mínimo', 'Q1', 'Mediana', 'Q3', 'Máximo']
            st.dataframe(resumen_vista, width='stretch')

        # Bloque de conclusiones automáticas
        promedio = round(stats['mean'], 1)
        mediana = int(stats['50%'])
        if col_seleccionada == 'winner_rank':
            st.success(f"**Interpretación:** El 50% de los ganadores son Top {mediana}. El ranking es un gran predictor.")
        else:
            st.warning(f"**Interpretación:** Dispersión alta. El promedio de {promedio} indica que la élite también cae.")

#PESTAÑA 2: COMPARACIÓN DE SERIES (DENSIDAD)
with tab2:
   
    st.header("🎾 Densidad de Ganadores: ¿Dónde se concentra el talento?")
    
    # Segmentación de datos por tipo de torneo
    series_atp = {
        'Grand Slam': df[df['Series'] == 'Grand Slam']['winner_rank'].dropna(),
        'Masters 1000': df[df['Series'] == 'Masters 1000']['winner_rank'].dropna(),
        'ATP500': df[df['Series'] == 'ATP500']['winner_rank'].dropna(),
        'ATP250': df[df['Series'] == 'ATP250']['winner_rank'].dropna()
    }

    hist_data = [v for v in series_atp.values() if not v.empty]
    group_labels = [k for k, v in series_atp.items() if not v.empty]
    
    if hist_data:
        fig_densidad = ff.create_distplot(hist_data, group_labels, show_hist=False, colors=['green', 'blue', 'red', 'orange'][:len(group_labels)])
        fig_densidad.update_layout(xaxis_title='Ranking', yaxis_title='Densidad', template='plotly_white', xaxis=dict(range=[1, 50]))
        st.plotly_chart(fig_densidad, use_container_width=True)

    st.divider()

    st.markdown("### 📌 Conclusión: La élite se concentra en los Grand Slams, pero los Masters 1000 también muestran una alta densidad de talento. ATP500 y ATP250 tienen una distribución más dispersa.")
# PESTAÑA 3: DISTRIBUCIÓN DE ÉLITE (BOXPLOTS)

with tab3:
    st.header("💻 Nivel de Élite: Rondas Finales")
    
    # 1. Cambio de nombre antes de procesar para que aparezca "Roland Garros" en la leyenda
    df['Tournament'] = df['Tournament'].replace('French Open', 'Roland Garros')
    
    # Cálculo del nivel de jerarquía del partido (Promedio de ambos jugadores)
    df['rank_medio'] = (df['winner_rank'] + df['loser_rank']) / 2
    rondas_clave = ['Quarterfinals', 'Semifinals', 'The Final']
    df_elite = df[df['Round'].isin(rondas_clave)].copy()
    
    # Filtro dinámico por categoría de torneo
    opciones_series = sorted(df_elite['Series'].unique())
    cat = st.selectbox("Selecciona la Categoría:", options=opciones_series, key="cat_tab3")
    df_cat = df_elite[df_elite['Series'] == cat]

    if not df_cat.empty:
        # Burbujas: Tamaño = Cantidad de partidos, Eje Y = Ranking promedio
        df_agrupado = df_cat.groupby(['Tournament', 'Round']).agg(
            promedio_rank=('rank_medio', 'mean'), 
            num_partidos=('rank_medio', 'count')
        ).reset_index()

        fig_burbuja = px.scatter(
            df_agrupado, x="Round", y="promedio_rank", size="num_partidos",
            color="Tournament", category_orders={"Round": rondas_clave},
            template="plotly_dark", size_max=30, 
            title=f"Concentración de Élite en {cat}"
        )
        
        # Invertimos eje Y (1 es mejor que 50)
        fig_burbuja.update_yaxes(autorange="reversed") 
        st.plotly_chart(fig_burbuja, use_container_width=True)

        st.divider()

        # Boxplot interactivo por superficie
        st.subheader(f"📊 Distribución de Rankings en {cat} por Superficie")
        lista_jugadores_en_cat = sorted(df_cat['Winner'].unique())
        jugador_foco = st.selectbox(
            "Resaltar un jugador:", 
            options=["Mostrar Solo Cajas (Limpio)"] + lista_jugadores_en_cat,
            key="jugador_tab3"
        )

        color_map = {'Clay': 'red', 'Grass': 'lightgreen', 'Hard': 'lightblue', 'Carpet': 'orange'}

        # Lógica boxplot
        fig_box = px.box(
            df_cat, x="Surface", y="rank_medio", color="Surface", 
            points=False, color_discrete_map=color_map, template="plotly_dark"
        )
        
        # Si se selecciona jugador, se añade una capa de puntos 
        if jugador_foco != "Mostrar Solo Cajas (Limpio)":
            df_solo_jugador = df_cat[df_cat['Winner'] == jugador_foco]
            fig_box.add_trace(px.scatter(df_solo_jugador, x="Surface", y="rank_medio").data[0])
            # Formato de los puntos: Círculos blancos
            fig_box.update_traces(
                marker=dict(size=12, symbol="circle", line=dict(width=2, color="white")), 
                selector=dict(type='scatter')
            )

        fig_box.update_layout(yaxis=dict(autorange="reversed", title="Ranking ATP"), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

        # Interpretación basada en el rendimiento del jugador seleccionado
        if jugador_foco != "Mostrar Solo Cajas (Limpio)":
            df_resumen = df_cat[df_cat['Winner'] == jugador_foco]
            prom_v = round(df_resumen['rank_medio'].mean(), 1)
            prom_cat = round(df_cat['rank_medio'].mean(), 1)
            st.markdown(f"### 🎯 Análisis: {jugador_foco}")
            col1, col2 = st.columns(2)
            col1.metric("Su Ranking Promedio", f"{prom_v}°")
            col2.metric("Promedio Categoría", f"{prom_cat}°")
            
            if prom_v <= 15: st.success("🚀 Dominio Absoluto.")
            elif prom_v <= prom_cat: st.info("⚖️ Consistencia.")
            else: st.warning("⚠️ Efecto Sorpresa.")

# PESTAÑA 4: ESTADÍSTICAS POR JUGADOR 
with tab4:

    st.header("🏆 Top 50 Jugadores con más Victorias (2016-2025)")
    
    # Conteo de victorias globales
    top_vics = df['Winner'].value_counts().head(50).reset_index()
    top_vics.columns = ['Jugador', 'Victorias']

    # Gráfico de barras global
    fig_global = px.bar(
        top_vics, x='Jugador', y='Victorias', 
        color='Victorias', color_continuous_scale='Blues', 
        template='plotly_dark' 
    )
    fig_global.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_global, use_container_width=True)

    st.divider() 
    
    # 2. Buscador individual de evolución
    st.header("🏆 Consulta de Victorias Individual")

    # Corrección de nombres repetidos
    # Limpiamos espacios en blanco y extraemos valores únicos de forma segura
    df['Winner'] = df['Winner'].str.strip() 
    lista_jugadores_v = sorted(df['Winner'].dropna().unique())
   

    jugador_sel = st.selectbox(
        "Selecciona un jugador:", 
        options=lista_jugadores_v, 
        key="jugador_tab4"
    )

    if jugador_sel:
        # Filtrado de datos del jugador
        df_j = df[df['Winner'] == jugador_sel].copy()
        
        # Métricas principales
        c1, c2 = st.columns(2)
        c1.metric("Victorias Totales", len(df_j))
        
        # Verificamos si hay datos de ranking para evitar errores de cálculo
        if not df_j['winner_rank'].dropna().empty:
            rank_prom = round(df_j['winner_rank'].mean(), 1)
            c2.metric("Ranking Promedio", f"{rank_prom}°")
        else:
            c2.metric("Ranking Promedio", "N/A")
        
        # Línea de tiempo de victorias por año
        # Aseguramos que la fecha sea datetime para el agrupamiento
        df_j['Date'] = pd.to_datetime(df_j['Date'])
        vict_anuales = df_j.groupby(df_j['Date'].dt.year).size().reset_index(name='Vics')
        
        fig_ev = px.line(
            vict_anuales, x='Date', y='Vics', 
            markers=True, 
            title=f"Evolución de Victorias: {jugador_sel}", 
            color_discrete_sequence=['green'], 
            template='plotly_dark'
        )
        
        # Ajustes estéticos al gráfico de línea
        fig_ev.update_layout(xaxis_title="Año", yaxis_title="Cantidad de Victorias")
        st.plotly_chart(fig_ev, use_container_width=True)