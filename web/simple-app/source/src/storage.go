package main

import (
	"database/sql"
	"errors"
	"html/template"
	"os"
)

func (app *application) listFiles() ([]fileRecord, error) {
	rows, err := app.db.Query("SELECT * FROM files")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var files []fileRecord
	for rows.Next() {
		var file fileRecord
		if err := rows.Scan(&file.ID, &file.Filename, &file.UUID); err != nil {
			return nil, err
		}
		files = append(files, file)
	}

	return files, rows.Err()
}

func (app *application) listNotes() ([]noteRecord, error) {
	rows, err := app.db.Query("SELECT id, title, body, completed, created_at FROM notes ORDER BY completed ASC, id DESC")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var notes []noteRecord
	for rows.Next() {
		var note noteRecord
		var completed int
		if err := rows.Scan(&note.ID, &note.Title, &note.Body, &completed, &note.CreatedAt); err != nil {
			return nil, err
		}
		note.UnsafeTitle = template.HTML(note.Title)
		note.UnsafeBody = template.HTML(note.Body)
		note.Completed = completed != 0
		notes = append(notes, note)
	}

	return notes, rows.Err()
}

func (app *application) findFile(uuidFile string) (fileRecord, error) {
	var file fileRecord
	err := app.db.QueryRow("SELECT * FROM files WHERE uuid = ?", uuidFile).Scan(&file.ID, &file.Filename, &file.UUID)
	return file, err
}

func (app *application) renameStoredFile(uuidFile string, newFilename *string) error {
	tx, err := app.db.Begin()
	if err != nil {
		return err
	}

	committed := false
	defer func() {
		if !committed {
			_ = tx.Rollback()
		}
	}()

	var file fileRecord
	if err := tx.QueryRow("SELECT * FROM files WHERE uuid = ?", uuidFile).Scan(&file.ID, &file.Filename, &file.UUID); err != nil {
		return err
	}

	if _, err := tx.Exec("UPDATE files SET filename = ? WHERE uuid = ?", newFilename, uuidFile); err != nil {
		return err
	}

	if newFilename == nil {
		return errors.New("new_filename is required")
	}

	oldPath := uploadPath(file.Filename)
	newPath := uploadPath(*newFilename)

	if isInvalidPath(newPath) {
		if err := tx.Commit(); err != nil {
			return err
		}
		committed = true
		return invalidFilenameError{}
	}

	if err := os.Rename(oldPath, newPath); err != nil {
		return err
	}

	if err := tx.Commit(); err != nil {
		return err
	}
	committed = true

	return nil
}

func ensureStorage(db *sql.DB) error {
	if err := os.MkdirAll(uploadFolder, 0o755); err != nil {
		return err
	}

	statements := []string{
		`CREATE TABLE IF NOT EXISTS files (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			filename TEXT NOT NULL,
			uuid TEXT NOT NULL
		)`,
		`CREATE TABLE IF NOT EXISTS notes (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title TEXT NOT NULL,
			body TEXT NOT NULL DEFAULT '',
			completed INTEGER NOT NULL DEFAULT 0,
			created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
		)`,
	}

	for _, statement := range statements {
		if _, err := db.Exec(statement); err != nil {
			return err
		}
	}

	return nil
}

type invalidFilenameError struct{}

func (invalidFilenameError) Error() string {
	return "invalid filename"
}
