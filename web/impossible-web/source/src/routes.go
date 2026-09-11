package main

import "net/http"

func (app *application) routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", app.index)
	mux.HandleFunc("/upload", app.upload)
	mux.HandleFunc("/uploads/", app.viewFile)
	mux.HandleFunc("/rename/", app.renameFile)
	mux.HandleFunc("/notes", app.createNote)
	mux.HandleFunc("/notes/", app.noteAction)
	return mux
}
