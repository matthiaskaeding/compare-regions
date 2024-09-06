package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	_ "modernc.org/sqlite"
)

type RequestBody struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

func get_value(db *sql.DB, input_region string) (string, string, error) {

	query := "SELECT gdp_per_capita, gdp_million FROM regions WHERE region = ? LIMIT 1"
	var gdp_per_capita, gdp_million float64
	err := db.QueryRow(query, input_region).Scan(&gdp_per_capita, &gdp_million)
	if err != nil {
		log.Fatal(err)
	}

	return fmt.Sprintf("%.2f", gdp_per_capita), fmt.Sprintf("%.2f", gdp_million), nil

}

func main() {

	db, err := sql.Open("sqlite", "data/processed/eco.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Test the connection
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}

	region_0 := "Niedersachsen"
	region_1 := "Berlin"

	gdp_per_capita_0, gdp_million_0, err := get_value(db, region_0)
	if err != nil {
		log.Fatal(err)
	}

	gdp_per_capita_1, gdp_million_1, err := get_value(db, region_1)
	if err != nil {
		log.Fatal(err)
	}

	prompt := fmt.Sprintf("The region %s has a GDP per capita of %s, and a GDP of %s while the region %s has a GDP per capita of %s and a GDP of %s. Compare these regions.",
		region_0, gdp_per_capita_0, gdp_million_0, region_1, gdp_per_capita_1, gdp_million_1)

	requestBody := RequestBody{
		Model:  "llama3.1",
		Prompt: prompt,
		Stream: false,
	}

	postBody, _ := json.Marshal(requestBody)
	responseBody := bytes.NewBuffer(postBody)

	resp, err := http.Post("http://localhost:11434/api/generate", "application/json", responseBody)
	if err != nil {
		log.Fatalf("An Error Occured %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var responseData map[string]interface{}
	err = json.Unmarshal(body, &responseData)
	if err != nil {
		log.Fatalf("Error unmarshaling JSON: %v", err)
	}
	fmt.Printf("Prompt: %s\n\n", prompt)
	fmt.Printf("Response:\n\n%s", responseData["response"])

}
