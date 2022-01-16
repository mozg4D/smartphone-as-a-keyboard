package main

import (
	"net/http"
)

func main() {
	fs := http.FileServer(http.Dir("./"))
	http.Handle("/", fs)
	http.ListenAndServe(":5000", nil)
}
