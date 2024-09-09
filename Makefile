

data/interim/eco_nuts3.csv: scripts/eurostat_data/download_data.py
	cd scripts/eurostat_data && uv run download_data.py

data/processed/eco_nuts3.csv: scripts/eurostat_data/clean_data.py
	cd scripts/eurostat_data && uv run clean_data.py

data/processed/eco_nuts3_wiki.csv: scripts/eurostat_data/wiki.py data/processed/eco_nuts3.csv
	cd scripts/eurostat_data && uv run wiki.py

data/processed/eco.db: scripts/eurostat_data/db.py data/processed/eco_nuts3_wiki.csv
	cd scripts/eurostat_data && uv run db.py

data: data/interim/eco_nuts3.csv data/processed/eco_nuts3.csv data/processed/eco_nuts3_wiki.csv data/processed/eco.db

run: 
	go run .

start-chroma:
	docker run -d --rm --name chromadb -p 8000:8000 -v ./chroma:/chroma/chroma -e IS_PERSISTENT=TRUE -e ANONYMIZED_TELEMETRY=TRUE chromadb/chroma:latest
.PHONY: start-chrome run