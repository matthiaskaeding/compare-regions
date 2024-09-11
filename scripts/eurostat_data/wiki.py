# %%

import wikipedia as wk

import sqlite3
from pathlib import Path
import pandas as pd
import os

# %%
assert Path().cwd().name == "eurostat_data"
proj_dir = Path().cwd().parents[1]
file = proj_dir / "data" / "processed" / "eco_nuts3.csv"
df = pd.read_csv(file)

# %%
rows = []
for reg in df.region:
    lu = reg.replace("ü", "u")
    print(reg, lu)
    # Handle some errors
    if lu == "Canarias":
        lu = "Canary Islands"
    elif lu == "Comunidad de Madrid":
        lu = "Madrid"
    elif lu == "Galicia":
        lu = "Galicia (Spain)"
    elif lu == "La Rioja":
        lu = "Rioja (Spain)"
    row = {"region": reg}
    row["wiki_page"] = wk.summary(lu)
    rows.append(row)

# %%
rhs = pd.DataFrame(rows)
out = df.merge(rhs, on="region")
file = proj_dir / "data" / "processed" / "eco_nuts3_wiki.csv"
out.to_csv(file)
