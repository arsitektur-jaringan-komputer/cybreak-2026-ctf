package main

import (
	"database/sql"
	"html/template"
	"log"
	"net/http"
	"path/filepath"

	_ "github.com/mattn/go-sqlite3"
)

func main() {
	db, err := sql.Open("sqlite3", databaseFile)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	if err := ensureStorage(db); err != nil {
		log.Fatal(err)
	}

	app := &application{
		db:        db,
		templates: template.Must(template.ParseGlob(filepath.Join("templates", "*.html"))),
	}

	log.Fatal(http.ListenAndServe("0.0.0.0:5000", app.routes()))
}
