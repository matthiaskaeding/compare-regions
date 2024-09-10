package main

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"sync"

	"github.com/google/uuid"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms/ollama"
	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores/chroma"
	_ "modernc.org/sqlite"
)

var (
	store     *chroma.Store
	storeErr  error
	storeOnce sync.Once
)

func initStore() (*chroma.Store, error) {
	storeOnce.Do(func() {
		store, storeErr = initStore0()
	})
	return store, storeErr
}

func initStore0() (*chroma.Store, error) {

	ollamaLLM, err := ollama.New(ollama.WithModel("llama3.1"))
	if err != nil {
		log.Fatal(err)
	}

	ollamaEmbeder, err := embeddings.NewEmbedder(ollamaLLM)
	if err != nil {
		log.Fatal(err)
	}

	// Create a new Chroma vector store.
	store, errNs := chroma.New(
		chroma.WithChromaURL(os.Getenv("CHROMA_URL")),
		chroma.WithEmbedder(ollamaEmbeder),
		chroma.WithDistanceFunction("cosine"),
		chroma.WithNameSpace(uuid.New().String()),
	)
	if errNs != nil {
		log.Fatalf("new: %v\n", errNs)
	}
	type meta = map[string]any

	// Read sqlite db
	db, err := sql.Open("sqlite", "data/processed/eco.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	query := `
		SELECT wiki_page, region, gdp_per_capita, gdp_million, country, population_million
		FROM regions 
		WHERE country IN ('Spain', 'Germany')
		ORDER BY region
	`
	rows, err := db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("error with query: %v", err)
	}
	defer rows.Close()

	var documents []schema.Document

	for rows.Next() {

		var gdp_per_capita, gdp_million, population_million float64
		var region, country, wiki_page string
		err := rows.Scan(&wiki_page, &region, &gdp_per_capita, &gdp_million, &country, &population_million)
		if err != nil {
			log.Fatal(err)
		}
		doc_meta := make(meta)
		//doc_meta["region"] = region
		doc_meta["gdp_per_capita"] = gdp_per_capita
		doc_meta["gdp_million"] = gdp_million
		doc_meta["population_million"] = population_million
		doc_meta["region"] = region
		doc_meta["country"] = country
		fmt.Println(region)
		fmt.Println(doc_meta)
		schema_doc := schema.Document{
			PageContent: wiki_page,
			Metadata:    doc_meta,
		}
		documents = append(documents, schema_doc)

	}
	fmt.Println("\nAdding documents to store...")

	// Process documents in chunk
	const chunkSize = 3
	ctx := context.Background()

	for i := 0; i < len(documents); i += chunkSize {
		end := i + chunkSize
		if end > len(documents) {
			end = len(documents)
		}

		chunk := documents[i:end]

		_, errAd := store.AddDocuments(ctx, chunk)
		if errAd != nil {
			log.Fatalf("AddDocuments for chunk %d-%d: %v\n", i, end-1, errAd)
		}
		fmt.Printf("Processed documents %d-%d\n", i, end-1)
	}

	return &store, nil

}
