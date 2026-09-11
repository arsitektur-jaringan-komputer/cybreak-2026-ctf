package main

import (
	"database/sql"
	"html/template"
)

const (
	uploadFolder = "uploads"
	databaseFile = "database.sqlite"
)

type application struct {
	db        *sql.DB
	templates *template.Template
}

type fileRecord struct {
	ID       int
	Filename string
	UUID     string
}

type noteRecord struct {
	ID          int
	Title       string
	Body        string
	UnsafeTitle template.HTML
	UnsafeBody  template.HTML
	Completed   bool
	CreatedAt   string
}

type dashboardData struct {
	Files []fileRecord
	Notes []noteRecord
}
