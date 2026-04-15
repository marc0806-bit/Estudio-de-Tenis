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

# FUNCIÓN DE CARGA Y LIMPIEZA
@st.cache_data 
def load_and_clean_tennis_data(filename):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)
    df_raw = pd.read_csv(full_path)
    
    df = df_raw.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df[(df['Date'].dt.year >= 2016) & (df['Date'].dt.year <= 2025)].copy()
    df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)].copy()
    
    df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
    df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1'])
    
    # --- UNIFICACIÓN GLOBAL DE TORNEOS (Lo que pediste) ---
    mapeo = {
        'French Open': 'Roland Garros',
        'BNP Paribas Open': 'Indian Wells',
        'Masters 1000 Indian Wells': 'Indian Wells',
        'BNP Paribas Masters': 'Paris Masters',
        'Rolex Paris Masters': 'Paris Masters',
        'Sony Ericsson Open': 'Miami Open',
        'Western & Southern Financial Group Masters': 'Cincinnati Masters',
        'Western & Southern Open': 'Cincinnati Masters'
    }
    df['Tournament'] = df['Tournament'].replace(mapeo)
    
    return df_raw, df

df_raw, df = load_and_clean_tennis_data('Tenis.csv')

# ESTRUCTURA DE NAVEGACIÓN
tab1, tab2, tab3, tab4 = st.tabs([
    "🔢 Estadísticos", 
    "📊 Comparación", 
    "💻 Distribución",  
    "🏆 Victorias"
])

# PESTAÑA 1: ANALISIS DESCRIPTIVO 
with tab1:
    st.header("🔢 Estadísticos de Ranking: Ganadores vs Perdedores")
    st.info("De la data original a las métricas de éxito (2016-2025)")

    st.subheader("📂 Visualización de Dataframes")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        with st.expander("🔍 Ver Datos Crudos (Original)"):
            st.dataframe(df_raw, width='stretch')
    with col_d2:
        with st.expander("🧪 Ver Datos Filtrados (Procesados)"):
            st.dataframe(df, width='stretch')

    st.divider()

    st.subheader("📊 Análisis Detallado: Winner vs Loser")
    opcion_analisis = st.radio("Métrica para profundizar:", options=["Ganadores (winner_rank)", "Perdedores (loser_rank)"], horizontal=True, key="radio_stats")

    col_seleccionada = 'winner_rank' if "Ganadores" in opcion_analisis else 'loser_rank'
    color_tema = 'lightgreen' if col_seleccionada == 'winner_rank' else 'red'

    stats = df[col_seleccionada].describe()
    col_graf, col_info = st.columns([1.5, 1])

    with col_graf:
        fig_interactiva = px.histogram(
            df, x=col_seleccionada, nbins=25,
            title=f"Distribución de Frecuencia: {opcion_analisis}",
            color_discrete_sequence=[color_tema],
            template="plotly_dark"
        )
        fig_interactiva.update_layout(bargap=0.1, xaxis_range=[1, 51])
        st.plotly_chart(fig_interactiva, width='stretch')

    with col_info:
        st.write(f"### Resumen de {opcion_analisis}")
        resumen_vista = stats.to_frame()
        resumen_vista.index = ['Cantidad', 'Promedio', 'Desv. Estándar', 'Mínimo', 'Q1', 'Mediana', 'Q3', 'Máximo']
        st.dataframe(resumen_vista, width='stretch')

    # Interpretación automática
    mediana = int(stats['50%'])
    if col_seleccionada == 'winner_rank':
        st.success(f"**Interpretación:** El 50% de los ganadores son Top {mediana}. El ranking es un gran predictor.")
    else:
        st.warning(f"**Interpretación:** Dispersión alta. El promedio indica que la élite también cae.")

# PESTAÑA 2: COMPARACIÓN
with tab2:
    st.header("🎾 Densidad de Ganadores")
    series_atp = {s: df[df['Series'] == s]['winner_rank'].dropna() for s in ['Grand Slam', 'Masters 1000', 'ATP500', 'ATP250']}
    
    fig_densidad = ff.create_distplot(list(series_atp.values()), list(series_atp.keys()), show_hist=False)
    fig_densidad.update_layout(xaxis_title='Ranking', yaxis_title='Densidad', template='plotly_dark', xaxis=dict(range=[1, 50]))
    st.plotly_chart(fig_densidad, use_container_width=True)

    st.divider()
    st.header("🎯 Consistencia de Élite: Trayectoria")
    rondas_completas = ['1st Round', '2nd Round', '3rd Round', '4th Round', 'Quarterfinals', 'Semifinals', 'The Final']
    
    df['Year'] = df['Date'].dt.year
    frecuencia = df.groupby('Winner')['Year'].nunique()
    jugadores_elite = frecuencia[frecuencia >= 7].index.tolist()

    seleccionados = st.multiselect("Selecciona jugadores:", sorted(jugadores_elite), default=["Djokovic N.", "Nadal R."])

    if seleccionados:
        df_evol = df[(df['Winner'].isin(seleccionados)) & (df['Round'].isin(rondas_completas))]
        df_evol = df_evol.groupby(['Winner', 'Round'])['winner_rank'].mean().reset_index()
        fig_evol = px.line(df_evol, x='Round', y='winner_rank', color='Winner', markers=True, category_orders={"Round": rondas_completas}, template="plotly_dark")
        fig_evol.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_evol, use_container_width=True)

# PESTAÑA 3: DISTRIBUCIÓN 
with tab3:
    
    st.header("💻 Nivel de Élite: Rondas Finales")
    
    # Preparación de datos base
    df['rank_medio'] = (df['winner_rank'] + df['loser_rank']) / 2
    rondas_clave = ['Quarterfinals', 'Semifinals', 'The Final']
    df_elite = df[df['Round'].isin(rondas_clave)].copy()

    #  SELECCIÓN DE CATEGORÍA (RADIO VERTICAL)
    st.write("**Categoría:**")
    cat = st.radio(
        "Selección", 
        options=sorted(df_elite['Series'].unique()), 
        label_visibility="collapsed", 
        key="cat_tab3_radio"
    )

    # iltro que SOLO depende de la categoría 
    df_cat = df_elite[df_elite['Series'] == cat]

    #  SELECTOR DE TORNEO (Afecta solo al gráfico de burbujas)
    tour_sel = st.selectbox(
        "Torneo:", 
        options=["Todos"] + sorted(df_cat['Tournament'].unique()), 
        key="tour_f"
    )

    # Filtro específico para las burbujas
    df_plot_burbuja = df_cat if tour_sel == "Todos" else df_cat[df_cat['Tournament'] == tour_sel]

    # GRÁFICO DE BURBUJAS 
    if not df_plot_burbuja.empty:
        agr = df_plot_burbuja.groupby(['Tournament', 'Round'])['rank_medio'].agg(['mean', 'count']).reset_index()
        fig_b = px.scatter(
            agr, x="Round", y="mean", size="count", color="Tournament", 
            category_orders={"Round": rondas_clave}, 
            template="plotly_dark", size_max=20,
            title=f"Tendencia de Élite: {tour_sel if tour_sel != 'Todos' else cat}"
        )
        fig_b.update_yaxes(autorange="reversed", title="Ranking Promedio")
        st.plotly_chart(fig_b, use_container_width=True)

    st.divider()

    # BOXPLOT SEGUNDO (ABAJO Y ESTÁTICO)
    st.subheader(f"📊 Distribución por Superficie en {cat}")
    
    if not df_cat.empty:
        fig_box = px.box(
            df_cat, x="Surface", y="rank_medio", color="Surface", points=False,
            color_discrete_map={'Clay': 'red', 'Grass': 'lightgreen', 'Hard': 'lightblue'}, 
            template="plotly_dark"
        )
        fig_box.update_layout(
            yaxis=dict(autorange="reversed", title="Ranking Medio"), 
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.info(f"Este análisis de superficie representa a todos los torneos de la categoría {cat}.")
# PESTAÑA 4: VICTORIAS 
with tab4:
    st.header("🏆 Top 50 Jugadores con más Victorias")
    top_vics = df['Winner'].value_counts().head(50).reset_index()
    top_vics.columns = ['Jugador', 'Victorias']
    st.plotly_chart(px.bar(top_vics, x='Jugador', y='Victorias', color='Victorias', template='plotly_dark'), use_container_width=True)

    st.divider()
    st.header("🏆 Consulta Individual")
    jugador_sel = st.selectbox("Selecciona un jugador:", options=sorted(df['Winner'].unique()), key="jug_tab4")
    
    if jugador_sel:
        df_j = df[df['Winner'] == jugador_sel].copy()
        c1, c2 = st.columns(2)
        c1.metric("Victorias Totales", len(df_j))
        c2.metric("Ranking Promedio", f"{round(df_j['winner_rank'].mean(), 1)}°")
        
        df_j['Year'] = df_j['Date'].dt.year
        vict_anuales = df_j.groupby('Year').size().reset_index(name='Vics')
        fig_ev = px.line(vict_anuales, x='Year', y='Vics', markers=True, template='plotly_dark', title=f"Evolución: {jugador_sel}")
        st.plotly_chart(fig_ev, use_container_width=True)