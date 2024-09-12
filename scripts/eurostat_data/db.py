# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.2.2",
#     "pysbd==0.3.4",
# ]
# ///
# Makes the db

# %%
import sqlite3
from pathlib import Path
import pandas as pd
import os
from pysbd import Segmenter
# %%

assert Path().cwd().name == "eurostat_data"
proj_dir = Path().cwd().parents[1]

# %%
df = pd.read_csv(proj_dir / "data" / "processed" / "eco_nuts3_wiki.csv")

# %%

# Wiki page first 2 words
assert "wiki_page" in df.columns
segmenter = Segmenter(language="en", clean=False)
# %%
all_sents = []
for wp in df.wiki_page:
    sents = segmenter.segment(wp)
    first = sents[0]
    all_sents.append(first)

df["wiki_summary"] = all_sents
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
# %%
cursor.execute("PRAGMA table_info(regions);")
columns_info = cursor.fetchall()

for column in columns_info:
    print(column)
# %%

conn.close()

# %%
# END
