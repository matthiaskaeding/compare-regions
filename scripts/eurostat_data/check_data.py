# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas>=2.2.2",
# ]
# ///

# %%

import pandas as pd
from pathlib import Path

# %%
assert Path().cwd().name == "eurostat_data"
proj_dir = Path().cwd().parent.parent


# %%
file = Path(proj_dir / "data" / "processed" / "eco_nuts3.csv")
assert file.exists()


# %%

# %%
df = pd.read_csv(file)

# %%
df.query("year == 2022").groupby(["region", "country"])[
    "pps_per_capita"
].mean().reset_index().sort_values("pps_per_capita", ascending=False).head(20)

# %%
df.query("year == 2022").groupby(["region", "country"])[
    "euro_per_capita"
].mean().reset_index().sort_values("euro_per_capita", ascending=False).head(20)


# %%
df.query("year == 2021").groupby(["country"])[
    "pps_per_capita"
].mean().reset_index().sort_values("pps_per_capita", ascending=False).head(20)


# %%
df[df.region == "Forchheim"]
# %%
