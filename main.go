package main

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores"
)

func main() {

	store, err := initialize_store()
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

	type filter = map[string]any
	exampleCases := []exampleCase{
		{
			name:         "Up to 5 Cities in Japan",
			query:        "Which of these are cities are located in Japan?",
			numDocuments: 5,
			options: []vectorstores.Option{
				vectorstores.WithScoreThreshold(0.8),
			},
		},
		{
			name:         "Large Cities in South America",
			query:        "Which of these are cities are located in South America?",
			numDocuments: 100,
			options: []vectorstores.Option{
				vectorstores.WithFilters(filter{
					"$and": []filter{
						{"area": filter{"$gte": 1000}},
						{"population": filter{"$gte": 13}},
					},
				}),
			},
		},
	}

	// run the example cases
	results := make([][]schema.Document, len(exampleCases))
	for ecI, ec := range exampleCases {
		docs, errSs := store.SimilaritySearch(ctx, ec.query, ec.numDocuments, ec.options...)
		if errSs != nil {
			log.Fatalf("query1: %v\n", errSs)
		}
		results[ecI] = docs
	}

	// print out the results of the run
	fmt.Printf("Results:\n")
	for ecI, ec := range exampleCases {
		texts := make([]string, len(results[ecI]))
		for docI, doc := range results[ecI] {
			texts[docI] = doc.PageContent
		}
		fmt.Printf("%d. case: %s\n", ecI+1, ec.name)
		fmt.Printf("    result: %s\n", strings.Join(texts, ", "))
	}

}
