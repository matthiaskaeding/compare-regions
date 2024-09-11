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
df = pd.read_csv(proj_dir / "data" / "processed" / "eco_nuts3_wiki.csv")

# %%
assert "wiki_page" in df.columns

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
