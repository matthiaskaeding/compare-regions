package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
)

type RequestBody struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

func main() {

	requestBody := RequestBody{
		Model:  "llama3.1",
		Prompt: "Is 100 bigger than 20000? Just say yes or no",
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

	fmt.Printf("Response:\n\n%s", responseData["response"])

}
