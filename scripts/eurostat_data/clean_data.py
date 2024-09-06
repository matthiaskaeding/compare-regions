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
proj_dir = Path().cwd().parents[1]


# %%
file = Path(proj_dir / "data" / "interim" / "eco_nuts3.csv")
assert file.exists()


# %%
df = pd.read_csv(file)
df.head()
# %%
df = df.rename(
    columns={"euro_per_capita": "gdp_per_capita", "million_euro": "gdp_million"}
)

# %%
df
# %%

out_file = proj_dir / "data" / "processed" / "eco_nuts3.csv"
Path(out_file).parent.mkdir(parents=True, exist_ok=True)
# %%

df.to_csv(out_file)
file.exists()
# %%
