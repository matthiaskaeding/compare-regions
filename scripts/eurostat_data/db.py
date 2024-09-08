# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.2.2",
# ]
# ///
# Makes the db

# %%
import sqlite3
from pathlib import Path
import pandas as pd
import os
# %%

assert Path().cwd().name == "eurostat_data"
proj_dir = Path().cwd().parents[1]

# %%
df = pd.read_csv(proj_dir / "data" / "processed" / "eco_nuts3.csv")

# %%
# Reduce to German Bundesländer and Spanish Comunidades Autónomas
german_nuts_codes = ["DE" + str(x) for x in range(1, 17)]
spanish_nuts_codes = [
    "ES61",  # Andalucía
    "ES24",  # Aragón
    "ES12",  # Principado de Asturias
    "ES53",  # Islas Baleares
    "ES70",  # Canarias
    "ES13",  # Cantabria
    "ES42",  # Castilla-La Mancha
    "ES41",  # Castilla y León
    "ES51",  # Cataluña
    "ES52",  # Comunidad Valenciana
    "ES43",  # Extremadura
    "ES11",  # Galicia
    "ES30",  # Comunidad de Madrid
    "ES62",  # Región de Murcia
    "ES22",  # Comunidad Foral de Navarra
    "ES21",  # País Vasco
    "ES23",  # La Rioja
    "ES63",  # Ceuta
    "ES64",  # Melilla
]
mask = [x in german_nuts_codes or x in spanish_nuts_codes for x in df.geo]
cols = [
    "geo",
    "region",
    "country",
    "year",
    "gdp_per_capita",
    "gdp_million",
    "number_len",
]


df = df.loc[mask, cols].dropna()

# %%
# Last value by year
df = df.sort_values("year", ascending=False).drop_duplicates(["geo"])

# %%
# Connect to the SQLite database
os.chdir(proj_dir / "data" / "processed")
conn = sqlite3.connect("eco.db")

# %%
cursor = conn.cursor()
drop_table_sql = "DROP TABLE IF EXISTS regions"
cursor.execute(drop_table_sql)

# %%
# Save to db
df.to_sql(name="regions", con=conn, index=False)

conn.close()

# %%
# END
