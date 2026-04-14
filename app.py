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
    # ANÁLISIS DE SUPERVIVENCIA COMPLETA
    st.header("🎯 Consistencia de Élite: Trayectoria Completa")
    st.info("Evolución del ranking promedio desde las primeras rondas hasta la final (2016-2025).")

    # Definición de la secuencia completa de rondas (Orden Cronológico)
    rondas_completas = [
        '1st Round',
        '2nd Round',
        '3rd Round', 
        '4th Round', 
        'Quarterfinals', 
        'Semifinals', 
        'The Final'
    ]

    # 2. Identificación de jugadores constantes (Top 50 estable)
    df['Year'] = df['Date'].dt.year
    frecuencia_jugadores = df.groupby('Winner')['Year'].nunique()
    # Filtramos jugadores con presencia en al menos 7 años para asegurar datos sólidos
    jugadores_elite = frecuencia_jugadores[frecuencia_jugadores >= 7].index.tolist()

    # selección múltiple
    seleccionados = st.multiselect(
        "Selecciona jugadores para comparar su supervivencia en todos los rounds:",
        options=sorted(jugadores_elite),
        default=["Djokovic N.", "Nadal R.", "Zverev A."] if "Djokovic N." in jugadores_elite else None,
        key="supervivencia_total"
    )

    if seleccionados:
        # Filtrar el DataFrame por los seleccionados y las rondas definidas
        df_trayectoria = df[
            (df['Winner'].isin(seleccionados)) & 
            (df['Round'].isin(rondas_completas))
        ].copy()

        # Agrupar para obtener el promedio por jugador y ronda
        df_evolucion = df_trayectoria.groupby(['Winner', 'Round'])['winner_rank'].mean().reset_index()

        # Gráfico de líneas (Evolución en todos los rounds)
        fig_evol = px.line(
            df_evolucion, 
            x='Round', 
            y='winner_rank', 
            color='Winner',
            markers=True,
            category_orders={"Round": rondas_completas},
            template="plotly_dark",
            title="Supervivencia: Del inicio a la Final",
            labels={'winner_rank': 'Ranking Promedio', 'Round': 'Etapa del Torneo'}
        )

        # Configuración: Invertir eje Y (1 arriba es mejor)
        fig_evol.update_yaxes(autorange="reversed", gridcolor="midnightblue")
        fig_evol.update_xaxes(gridcolor="midnightblue")
        
        st.plotly_chart(fig_evol, use_container_width=True)

        #  Evidencia numérica (Tabla Pivote)
        st.subheader("📊 Tabla de Desempeño por Ronda")
        resumen_pivot = df_evolucion.pivot(index='Winner', columns='Round', values='winner_rank')
        
        # Reordenar columnas para que coincidan con el avance del torneo
        cols_finales = [r for r in rondas_completas if r in resumen_pivot.columns]
        resumen_pivot = resumen_pivot[cols_finales]
        
        # Resaltamos el mejor ranking (valor mínimo) en amarillo
        st.dataframe(resumen_pivot.style.highlight_min(axis=1, color='yellow'), width='stretch')
# PESTAÑA 3: DISTRIBUCIÓN DE ÉLITE (BOXPLOTS)

with tab3:
   
    st.header("💻 Nivel de Élite: Rondas Finales")
    
    df['Tournament'] = df['Tournament'].replace('French Open', 'Roland Garros')
    df['rank_medio'] = (df['winner_rank'] + df['loser_rank']) / 2
    rondas_clave = ['Quarterfinals', 'Semifinals', 'The Final']
    df_elite = df[df['Round'].isin(rondas_clave)].copy()
    
    cat = st.selectbox("Categoría:", options=sorted(df_elite['Series'].unique()), key="cat_tab3")
    df_cat = df_elite[df_elite['Series'] == cat]

    if not df_cat.empty:
        # Gráfico de Burbujas 
        df_agrupado = df_cat.groupby(['Tournament', 'Round'])['rank_medio'].agg(['mean', 'count']).reset_index()
        fig_burbuja = px.scatter(df_agrupado, x="Round", y="mean", size="count", color="Tournament", 
                                 category_orders={"Round": rondas_clave}, template="plotly_dark", 
                                 title=f"Élite en {cat}", size_max=25).update_yaxes(autorange="reversed")
        st.plotly_chart(fig_burbuja, use_container_width=True)

        # Boxplot y Selección de Jugador
        st.subheader(f"📊 Distribución en {cat}")
        jugador_foco = st.selectbox("Resaltar jugador:", ["Limpio"] + sorted(df_cat['Winner'].unique()), key="jug_t3")

        fig_box = px.box(df_cat, x="Surface", y="rank_medio", color="Surface", points=False,
                         color_discrete_map={'Clay': 'red', 'Grass': 'lightgreen', 'Hard': 'lightblue'}, 
                         template="plotly_dark").update_layout(yaxis=dict(autorange="reversed"), showlegend=False)
        
        if jugador_foco != "Limpio":
            df_solo = df_cat[df_cat['Winner'] == jugador_foco]
            fig_box.add_trace(px.scatter(df_solo, x="Surface", y="rank_medio").data[0])
            fig_box.update_traces(marker=dict(size=10, color="white", line=dict(width=1)))

        st.plotly_chart(fig_box, use_container_width=True)

        # SECCIÓN DE MÉTRICAS
        if jugador_foco != "Limpio":
            # Cálculos rápidos
            p_cat = round(df_cat[df_cat['Winner'] == jugador_foco]['rank_medio'].mean(), 1)
            p_global = round(df[df['Winner'] == jugador_foco]['winner_rank'].mean(), 1)
            
            st.markdown(f"### 🎯 Análisis: {jugador_foco}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Promedio en Cat.", f"{p_cat}°")
            c2.metric("Promedio Global", f"{p_global}°")
            c3.metric("Diferencia", f"{round(p_cat - p_global, 1)}")
            
            # Nota rápida de rendimiento
            st.caption("Nota: Los valores negativos indican que el jugador rinde por encima de su nivel habitual en esta categoría.")

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
    
    # Buscador individual de evolución
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