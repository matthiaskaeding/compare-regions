

data/interim/eco_nuts3.csv: scripts/eurostat_data/download_data.py
	cd scripts/eurostat_data && uv run download_data.py

data/processed/eco_nuts3.csv: scripts/eurostat_data/clean_data.py
	cd scripts/eurostat_data && uv run clean_data.py

data/processed/eco.db: scripts/db.py
	cd scripts && uv run db.py

data: data/interim/eco_nuts3.csv data/processed/eco_nuts3.csv data/processed/eco.db

make run: 
	go run .

make start-chroma:
	docker run -d --rm --name chromadb -p 8000:8000 -v ./chroma:/chroma/chroma -e IS_PERSISTENT=TRUE -e ANONYMIZED_TELEMETRY=TRUE chromadb/chroma:latest
.PHONY: start-chroma