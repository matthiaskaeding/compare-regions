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

assert Path().cwd().name == "scripts"
proj_dir = Path().cwd().parent


# %%

out_file = proj_dir / "data" / "processed" / "eco_nuts3.csv"
df = pd.read_csv(out_file)
# %%
cols = [
    "geo",
    "region",
    "country",
    "year",
    "gdp_per_capita",
    "gdp_million",
]
df = df[cols]
# %%

# Connect to the SQLite database
os.chdir(proj_dir / "data" / "processed")
conn = sqlite3.connect("eco.db")

# %%
# Get last value by year and save to db
df_out = df.dropna().sort_values("year", ascending=False).drop_duplicates(["geo"])
df_out.to_sql(name="regions", con=conn, index=False)

conn.close()

# %%
