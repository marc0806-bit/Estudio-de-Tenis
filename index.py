# nuevo uso de los datos de tenis, con un nuevo dataset, con datos de 2015 a 2025, y solo con los jugadores que han estado en el top 50 del ranking mundial. Se hará un análisis de los partidos por torneo, y se mostrarán los resultados.
import pandas as pd
import seaborn as sns
import matplotlib as plt
import numpy as np
df = pd.read_csv('Tenis.csv')

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df = df[(df['Date'].dt.year >= 2015) & (df['Date'].dt.year <= 2025)]
df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)]

print(df.head(5))
print(df.tail(5))

print(df['Surface'].value_counts())

def partidos_per_torneo(df):
    return df['Tournament'].value_counts()
df = df[(df['Date'].dt.year > 2015) & (df['Date'].dt.year <= 2025)]
df = df[(df['Rank_1'] <= 50) & (df['Rank_2'] <= 50)]

#NUEVAS COLUMNAS PARA EL USO DE LOS GANADORES DE LOS PARTIDOS
df['winner_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_1'], df['Rank_2'])
df['loser_rank'] = np.where(df['Winner'] == df['Player_1'], df['Rank_2'], df['Rank_1']) 

print(df[['Tournament', 'winner_rank', 'loser_rank']].head())

print(partidos_per_torneo(df))