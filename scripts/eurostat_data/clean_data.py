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
df = pd.read_csv(file)


# %%
df["country"] = df["geo"].str.slice(0, 2)
df["number"] = df["geo"].str.slice(3, 100)

# %%
df["number_len"] = [len(x) if isinstance(x, str) else 0 for x in df["number"]]
# %%

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
out = out.rename(
    columns={"euro_per_capita": "gdp_per_capita", "million_euro": "gdp_million"}
)

# %%
out["population_million"] = out["gdp_million"] / out["gdp_per_capita"]

# %%
# %%
# Reduce to German Bundesländer and Spanish Comunidades Autónomas

german_nuts_codes = [
    "DE1",  # Baden-Württemberg
    "DE2",  # Bayern (Bavaria)
    "DE3",  # Berlin
    "DE4",  # Brandenburg
    "DE5",  # Bremen
    "DE6",  # Hamburg
    "DE7",  # Hessen (Hesse)
    "DE8",  # Mecklenburg-Vorpommern
    "DE9",  # Niedersachsen (Lower Saxony)
    "DEA",  # Nordrhein-Westfalen (North Rhine-Westphalia)
    "DEB",  # Rheinland-Pfalz (Rhineland-Palatinate)
    "DEC0",  # Saarland
    "DED",  # Sachsen (Saxony)
    "DEE",  # Sachsen-Anhalt (Saxony-Anhalt)
    "DEF",  # Schleswig-Holstein
    "DEG",  # Thüringen (Thuringia)
]

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
mask = [x in german_nuts_codes or x in spanish_nuts_codes for x in out.geo]
cols = [
    "geo",
    "region",
    "country",
    "year",
    "gdp_per_capita",
    "gdp_million",
    "population_million",
    "number_len",
]


out = out.loc[mask, cols].dropna()

assert set(out.geo) == set(german_nuts_codes + spanish_nuts_codes)


out["country"] = out.country.replace(to_replace=dict(ES="Spain", DE="Germany"))

# %%
# Last value by year
out = (
    out.sort_values("year", ascending=False)
    .drop_duplicates(["geo"])
    .sort_values(["country", "region"])
)

# %%

out_file = proj_dir / "data" / "processed" / "eco_nuts3.csv"
Path(out_file).parent.mkdir(parents=True, exist_ok=True)
out.to_csv(out_file)


# %%
