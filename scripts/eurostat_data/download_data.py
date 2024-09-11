# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "eurostat==1.1.1",
#     "pandas>=2.2.2",
# ]
# ///

# %%

import eurostat
from pathlib import Path

# %%
assert Path().cwd().name == "eurostat_data"
proj_dir = Path().cwd().parent.parent

# %%
# toc = eurostat.get_toc()
# toc_df = eurostat.get_toc_df()
# toc_df = toc_df.set_index("title")
# toc_df.loc["Gross domestic product (GDP) at current market prices by NUTS 3 regions"]

# %%

code = "NAMA_10R_3GDP"

# %%
# The actual dataframe
df = eurostat.get_data_df(code).rename(columns={"geo\TIME_PERIOD": "geo"})

# %%
# Add labels: unit
dic_unit = eurostat.get_dic(code, "unit", frmt="df").rename(
    columns={"val": "unit", "descr": "unit_label"}
)
df = df.merge(dic_unit, on="unit", how="left")

# %%
# Add labels: geo
dic_geo = eurostat.get_dic(code, "geo", frmt="df").rename(
    columns={"val": "geo", "descr": "geo_label"}
)
df = df.merge(dic_geo, on="geo", how="left")

# %%
assert "geo_label" in df.columns
assert "unit_label" in df.columns
# %%

out_file = proj_dir / "data" / "interim" / "eco_nuts3.csv"
df.to_csv(out_file)
