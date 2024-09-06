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

codes = ["NAMA_10R_3GDP", "NAMA_10R_3GDP$DV_1562"]
code = codes[0]


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
df[["country", "number"]] = df["geo"].str.split(r"(\d+)", expand=True)[[0, 1]]
# %%
df["number_len"] = [len(x) if isinstance(x, str) else 0 for x in df["number"]]
# %%
# Get NUTS3
df = df.query("number_len >= 1")

# %%
year_columns = [col for col in df.columns if col.isdigit()]
vars = df.unit_label.drop_duplicates().to_list()

# %%
assert set(df.freq) == {"A"}, "Frequency must be all A (annual I think)"

# %%
out = (
    df.melt(
        id_vars=["geo", "geo_label", "country", "number", "unit_label", "number_len"],
        value_vars=year_columns,
        var_name="year",
    )
    .pivot(
        index=["geo", "geo_label", "country", "number", "year", "number_len"],
        columns="unit_label",
        values="value",
    )
    .reset_index()
    .rename(columns={"geo_label": "region"})
)


# %%
def clean_column_name(name):
    import re

    # Convert to lowercase
    name = name.lower()

    # Remove text within parentheses
    name = re.sub(r"\([^)]*\)", "", name)

    # Replace certain phrases with abbreviations
    replacements = {
        "purchasing power standard": "pps",
        "european union": "eu",
        "per inhabitant": "per_capita",
        "percentage of the": "pct",
        "average": "avg",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)

    # Remove common words
    words_to_remove = ["from", "in", "of", "the"]
    for word in words_to_remove:
        name = re.sub(rf"\b{word}\b", "", name)

    # Remove any remaining punctuation and replace spaces with underscores
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name).strip("_")

    # Ensure the name starts with a letter (pandas requirement)
    if not name[0].isalpha():
        name = "col_" + name

    return name


out.columns = [clean_column_name(col) for col in out.columns]

# %%
out = out.sort_values(["region", "year"])
out
# %%

out_file = proj_dir / "data" / "interim" / "eco_nuts3.csv"
Path(out_file).parent.mkdir(parents=True, exist_ok=True)

out.to_csv(out_file)
