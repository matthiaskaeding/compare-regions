package main

import (
	"context"
	"flag"
	"fmt"
	"log"

	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/ollama"
	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores"
)

var rebuildStore = flag.Bool("buildstore", false, "Initialize the store")
var region_0 = flag.String("region_0", "Catalunia", "First region")
var region_1 = flag.String("region_1", "Bayern", "Second region")

func main() {
	flag.Parse()
	fmt.Printf("Comparing regions %s and %s\n", *region_0, *region_1)

	store, err := initStore(*rebuildStore)
	if err != nil {
		log.Fatal(err)
	}

	ctx := context.TODO()

	type exampleCase struct {
		name         string
		query        string
		numDocuments int
		options      []vectorstores.Option
	}

	//type filter = map[string]any
	cases := []exampleCase{
		{
			name:         *region_0,
			query:        *region_0,
			numDocuments: 1,
			options: []vectorstores.Option{
				vectorstores.WithScoreThreshold(0.5),
			},
		},
		{
			name:         *region_1,
			query:        *region_1,
			numDocuments: 1,
			options: []vectorstores.Option{
				vectorstores.WithScoreThreshold(0.5),
			},
		},
	}

	// run the example cases
	results := make([][]schema.Document, len(cases))
	for eCs, cs := range cases {
		docs, errSs := store.SimilaritySearch(ctx, cs.query, cs.numDocuments, cs.options...)
		if errSs != nil {
			log.Fatalf("query1: %v\n", errSs)
		}
		if len(docs) == 0 {
			panic(fmt.Sprintf("Could not find any data for %s", cs.name))
		}
		results[eCs] = docs
	}
	md_0 := results[0][0].Metadata

	context_0 := fmt.Sprintf(
		"%s\n:Country: %s, population: %s, gdp_per_capita:%s",
		*region_0, md_0["country"], md_0["population_million"], md_0["gdp_per_capita"])

	md_1 := results[1][0].Metadata
	context_1 := fmt.Sprintf(
		"%s\n:Country: %s, population: %s, gdp_per_capita:%s",
		*region_1, md_1["country"], md_1["population_million"], md_1["gdp_per_capita"])

	context_text := fmt.Sprintf("Context:\n%s\n%s", context_0, context_1)

	// Feed back into ollama
	ollamaLLM, err := ollama.New(ollama.WithModel("llama3.1"))
	if err != nil {
		log.Fatal(err)
	}

	ctx_background := context.Background()
	content := []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeSystem, context_text),
		llms.TextParts(llms.ChatMessageTypeSystem, "Only use the information from the context provided"),
		llms.TextParts(llms.ChatMessageTypeHuman, fmt.Sprintf("Compare %s with %s", *region_0, *region_1)),
	}
	completion, err := ollamaLLM.GenerateContent(ctx_background, content, llms.WithStreamingFunc(func(ctx context.Context, chunk []byte) error {
		fmt.Print(string(chunk))
		return nil
	}))
	if err != nil {
		log.Fatal(err)
	}
	_ = completion

}
