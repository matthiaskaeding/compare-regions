package main

import (
	"context"
	"log"
	"os"

	"github.com/google/uuid"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms/ollama"
	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores/chroma"
)

func initialize_store() (*chroma.Store, error) {
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

	// Add documents to the vector store.
	_, errAd := store.AddDocuments(context.Background(), []schema.Document{
		{PageContent: "Tokyo", Metadata: meta{"population": 9.7, "area": 622}},
		{PageContent: "Kyoto", Metadata: meta{"population": 1.46, "area": 828}},
		{PageContent: "Hiroshima", Metadata: meta{"population": 1.2, "area": 905}},
		{PageContent: "Kazuno", Metadata: meta{"population": 0.04, "area": 707}},
		{PageContent: "Nagoya", Metadata: meta{"population": 2.3, "area": 326}},
		{PageContent: "Toyota", Metadata: meta{"population": 0.42, "area": 918}},
		{PageContent: "Fukuoka", Metadata: meta{"population": 1.59, "area": 341}},
		{PageContent: "Paris", Metadata: meta{"population": 11, "area": 105}},
		{PageContent: "London", Metadata: meta{"population": 9.5, "area": 1572}},
		{PageContent: "Santiago", Metadata: meta{"population": 6.9, "area": 641}},
		{PageContent: "Buenos Aires", Metadata: meta{"population": 15.5, "area": 203}},
		{PageContent: "Rio de Janeiro", Metadata: meta{"population": 13.7, "area": 1200}},
		{PageContent: "Sao Paulo", Metadata: meta{"population": 22.6, "area": 1523}},
	})
	if errAd != nil {
		log.Fatalf("AddDocument: %v\n", errAd)
	}

	return &store, nil

}
