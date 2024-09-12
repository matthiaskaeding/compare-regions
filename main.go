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
var region_1 = flag.String("region_1", "Niedersachsen", "Second region")

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

	// Run the example cases
	var documents = make(map[string]schema.Document)
	for _, cs := range cases {
		docs, errSs := store.SimilaritySearch(ctx, cs.query, cs.numDocuments, cs.options...)
		if errSs != nil {
			log.Fatalf("query1: %v\n", errSs)
		}
		if len(docs) != 1 {
			panic(fmt.Sprintf("Could not find any data for %s", cs.name))
		}
		fmt.Printf("Metadata for : %+v\n\n", docs)
		documents[cs.name] = docs[0]
	}

	// Build context
	text_context := "Context: \n"
	for region, docs := range documents {
		md := docs.Metadata
		text_context += fmt.Sprintf("Region: %s\n", region)
		for key, value := range md {
			switch key {
			case "nameSpace", "wiki_page", "wiki_summary":
				continue
			}
			var rhs string
			switch value.(type) {
			case float32, float64:
				rhs = fmt.Sprintf("  %s: %.2f\n", key, value)
			default:
				rhs = fmt.Sprintf("  %s: %s\n", key, value)
			}
			text_context += rhs
		}
	}
	fmt.Println(text_context)

	// Feed back into ollama
	ollamaLLM, err := ollama.New(ollama.WithModel("llama3.1"))
	if err != nil {
		log.Fatal(err)
	}

	ctx_background := context.Background()
	content := []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeSystem, text_context),
		llms.TextParts(llms.ChatMessageTypeSystem,
			"Only use the information from the context provided"),
		llms.TextParts(llms.ChatMessageTypeHuman,
			fmt.Sprintf("Compare %s with %s", *region_0, *region_1)),
	}
	completion, err := ollamaLLM.GenerateContent(ctx_background, content,
		llms.WithStreamingFunc(func(ctx context.Context, chunk []byte) error {
			fmt.Print(string(chunk))
			return nil
		}))
	if err != nil {
		log.Fatal(err)
	}
	_ = completion

}
