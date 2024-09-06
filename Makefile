

data/interim/eco_nuts3.csv: scripts/eurostat_data/download_data.py
	cd scripts/eurostat_data && uv run download_data.py

data/processed/eco_nuts3.csv: scripts/eurostat_data/clean_data.py
	cd scripts/eurostat_data && uv run clean_data.py

data/processed/eco.db: scripts/db.py
	cd scripts && uv run db.py


data: data/interim/eco_nuts3.csv data/processed/eco_nuts3.csv data/processed/eco.db

make run: 
	go run .

.PHONY: run
