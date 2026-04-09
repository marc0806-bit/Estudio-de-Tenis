# nuevo uso de los datos de tenis, con un nuevo dataset, con datos de 2016 a 2025, y solo con los jugadores que han estado en el top 50 del ranking mundial. Se hará un análisis de los partidos por torneo, y se mostrarán los resultados.
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv('Tenis.csv')

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df = df[(df['Date'].dt.year > 2015) & (df['Date'].dt.year <= 2025)]
df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)]

print(df.head(5))
print(df.tail(5))

print(df['Surface'].value_counts())

def partidos_per_torneo(df):
    return df['Tournament'].value_counts()

#NUEVAS COLUMNAS PARA EL USO DE LOS GANADORES DE LOS PARTIDOS
df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1']) 



sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Grafico la distribución del ranking del ganador
sns.histplot(df['winner_rank'], kde=True, color="skyblue", label="Ganadores", stat="density", alpha=0.5)
datos_winner_rank = df['winner_rank'].agg(['count', 'mean', 'median', 'std', 'var', 'min', 'max', 'skew', 'kurt'])

# Grafico la distribución del ranking del perdedor
sns.histplot(df['loser_rank'], kde=True, color="red", label="Perdedor", stat="density", alpha=0.5)
datos_loser_rank = df['loser_rank'].agg(['count', 'mean', 'median', 'std', 'var', 'min', 'max', 'skew', 'kurt'])

# Personalización de etiquetas y título
plt.title('Comparación de Distribuciones: Ranking Ganadores vs Perdedores (2016-2025)')
plt.xlabel('Ranking ATP')
plt.ylabel('Densidad')
plt.legend()
plt.show()
print(df[['Tournament', 'winner_rank', 'loser_rank']].head())
print(datos_winner_rank)
print(datos_loser_rank)
print(partidos_per_torneo(df))

# realizamos un gráfico de cajas (boxplot) para comparar el ranking del ganador según la superficie del torneo
datos_grafico = df[df['Surface'].isin(['Hard', 'Clay', 'Grass'])]
plt.figure(figsize=(10, 7))
sns.set_theme(style="whitegrid") 

# CREAR EL BOXPLOT 
sns.boxplot(
    x='Surface', 
    y='winner_rank', 
    data=datos_grafico, 
    palette="Set2",      
    width=0.6,          
    linewidth=2,         
    fliersize=3,         
    flierprops={"marker": "o", "markerfacecolor": "gray", "alpha": 0.5} )

plt.title('Análisis de Jerarquía: Ranking de los Ganadores por Superficie', fontsize=14, fontweight='bold')
plt.xlabel('Tipo de Terreno', fontsize=12)
plt.ylabel('Ranking ATP (1 es el mejor)', fontsize=12)
plt.gca().invert_yaxis()
plt.yticks([1, 10, 20, 30, 40, 50])
plt.show()

#realizamos el gráfico de líneas para mostrar la evolución del ranking del ganador a lo largo de las rondas del torneo, para ver si los mejores jugadores llegan a las finales o si hay sorpresas en las primeras rondas.

# Definimos el orden de las rondas (de la primera a la final)
orden_rondas = ['1st Round', '2nd Round', '3rd Round', '4th Round', 'Quarterfinals', 'Semifinals', 'The Final']

# Agrupamos por ronda y calculamos el promedio del ranking del ganador
resumen_rondas = df.groupby('Round')['winner_rank'].mean()

# Reorganizamos los datos para que sigan el orden lógico del torneo
datos_linea = resumen_rondas.reindex(orden_rondas)

#EL GRÁFICO
plt.figure(figsize=(10, 5))
plt.plot(datos_linea.index, datos_linea.values, marker='o', color='green', linewidth=2)

# Personalizamos los textos
plt.title('¿Se filtran los mejores jugadores al final del torneo?')
plt.xlabel('Ronda del Torneo')
plt.ylabel('Ranking Promedio (Cerca de 1 es mejor)')

# estamos invirtiendo el eje y para que el ranking 1 esté en la parte superior del gráfico
plt.gca().invert_yaxis()

plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

# Realizamos un gráfico de barras poor ramkimg promedio y categoría  
#Datos y Promedio
orden = ['ATP250', 'ATP500', 'Masters 1000', 'Grand Slam']
datos = df.groupby('Series')['winner_rank'].mean().reindex(orden)

# GRÁFICO DE BARRAS 
plt.figure(figsize=(10, 5))
barras = plt.barh(datos.index, datos.values, color='skyblue', edgecolor='black')
#datos de las barras
plt.bar_label(barras, fmt='%.1f', padding=5, fontweight='bold')
# Para que el Ranking 1 (el mejor) esté a la derecha (la barra más larga)
plt.xlim(30, 0) 
#Títulos 
plt.title('Ranking Promedio de los jugadores Ganadores (Más a la derecha = Mejor Ranking)')
plt.xlabel('Ranking ATP (El 1 es la excelencia)')
plt.ylabel('Categoría del Torneo')
plt.tight_layout()
plt.show()



# realizamos un gráfico de torta para mostrar la proporción de partidos por categoría de torneo, para ver si hay una concentración de partidos en ciertas categorías

# Contamos cuántos partidos hay por cada categoría (Series)
conteo_total = df['Series'].value_counts()

# Definimos los colores (usando una paleta coherente con tu gráfico de densidad)
colores_pro = sns.color_palette("viridis", len(conteo_total))

plt.figure(figsize=(10, 7))

# Creamos el gráfico de torta
plt.pie(conteo_total, 
        labels=conteo_total.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colores_pro,
        explode=[0.05] * len(conteo_total), # Separa un poco todas las tajadas
        pctdistance=0.85)

# Añadimos un círculo blanco en el centro para convertirlo en un gráfico de Donut (disnto del gráfico de torta tradicional)
centro_circulo = plt.Circle((0,0), 0.70, fc='white')
fig = plt.gcf()
fig.gca().add_artist(centro_circulo)

plt.title('Distribución Total de Partidos por Categoría\n(Jugadores Top 50 | 2016-2025)', fontsize=14, fontweight='bold')
plt.axis('equal') 
plt.tight_layout()
plt.show()

# Mostramos los números brutos para referencia
print("Cantidad de partidos analizados por categoría:")
print(conteo_total)




#realizamos ahora un gráfico de densidad para mostrar la concentración de los ganadores según su ranking, separado por categoría de torneo
sns.set_theme(style="white")
plt.figure(figsize=(10, 6))

#CREAR EL GRÁFICO DE DENSIDAD (SOLAPADO)
# Usamos 'hue' para separar por torneo y 'fill=True' para que tengan color
sns.kdeplot(data=df, x='winner_rank', hue='Series', 
            hue_order=['ATP250', 'ATP500', 'Masters 1000', 'Grand Slam'],
            fill=True, common_norm=False, palette="viridis", alpha=0.5)

#LIMITAR EL EJE X
plt.xlim(1, 70)
plt.title('Densidad de Ganadores: ¿Dónde se concentra el talento?', fontsize=14)
plt.xlabel('Ranking del Ganador (1 es el mejor)')
plt.ylabel('Densidad (Concentración de victorias)')
plt.show()



#Calculamos victorias y derrotas totales
ganados_50 = df['Winner'].value_counts().head(50)

df['Loser'] = np.where(df['Winner'] == df['Player_1'], df['Player_2'], df['Player_1'])
perdidos_50 = df['Loser'].value_counts().head(50)

#Gráfico para los 50 máximos ganadores
plt.figure(figsize=(15, 8))
ganados_50.plot(kind='bar', color='blue', edgecolor='black')
plt.title('Top 50 Jugadores con más Victorias (2016-2025)', fontsize=16)
plt.xlabel('Jugador', fontsize=12)
plt.ylabel('Número de Victorias', fontsize=12)
plt.xticks(rotation=90) # Rotamos los nombres para que se lean bien
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()
print("LISTADO COMPLETO TOP 50 GANADORES:")
print(ganados_50)

