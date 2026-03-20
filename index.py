import pandas as pd

df = pd.read_csv('Tenis.csv')

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df = df[(df['Date'].dt.year >= 2015) & (df['Date'].dt.year <= 2020)]
df = df[(df['Rank_1'] <= 100) & (df['Rank_2'] <= 100)]

print(df.head(5))
print(df.tail(5))

print(df['Surface'].value_counts())

def partidos_per_torneo(df):
    return df['Tournament'].value_counts()

print(partidos_per_torneo(df))

