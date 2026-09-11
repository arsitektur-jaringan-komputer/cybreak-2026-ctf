package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

func (app *application) index(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	if !allowsRead(r.Method) {
		methodNotAllowed(w)
		return
	}

	files, err := app.listFiles()
	if err != nil {
		internalError(w, err)
		return
	}
	notes, err := app.listNotes()
	if err != nil {
		internalError(w, err)
		return
	}

	if err := app.templates.ExecuteTemplate(w, "index.html", dashboardData{Files: files, Notes: notes}); err != nil {
		internalError(w, err)
	}
}

func (app *application) createNote(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		methodNotAllowed(w)
		return
	}

	if err := r.ParseForm(); err != nil {
		http.Error(w, "Invalid note", http.StatusBadRequest)
		return
	}

	title := strings.TrimSpace(r.FormValue("title"))
	body := strings.TrimSpace(r.FormValue("body"))
	if title == "" {
		title = "Untitled note"
	}

	if _, err := app.db.Exec("INSERT INTO notes (title, body) VALUES (?, ?)", title, body); err != nil {
		internalError(w, err)
		return
	}

	http.Redirect(w, r, "/", http.StatusFound)
}

func (app *application) noteAction(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		methodNotAllowed(w)
		return
	}

	parts := strings.Split(strings.TrimPrefix(r.URL.Path, "/notes/"), "/")
	if len(parts) != 2 {
		http.NotFound(w, r)
		return
	}

	id, err := strconv.Atoi(parts[0])
	if err != nil || id < 1 {
		http.NotFound(w, r)
		return
	}

	switch parts[1] {
	case "toggle":
		if _, err := app.db.Exec("UPDATE notes SET completed = CASE completed WHEN 0 THEN 1 ELSE 0 END WHERE id = ?", id); err != nil {
			internalError(w, err)
			return
		}
	case "delete":
		if _, err := app.db.Exec("DELETE FROM notes WHERE id = ?", id); err != nil {
			internalError(w, err)
			return
		}
	default:
		http.NotFound(w, r)
		return
	}

	http.Redirect(w, r, "/", http.StatusFound)
}

func (app *application) upload(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet, http.MethodHead:
		if err := app.templates.ExecuteTemplate(w, "upload.html", nil); err != nil {
			internalError(w, err)
		}
	case http.MethodPost:
		app.acceptUpload(w, r)
	default:
		methodNotAllowed(w)
	}
}

func (app *application) acceptUpload(w http.ResponseWriter, r *http.Request) {
	file, filename, err := rawUploadedFile(r, "file")
	if err != nil {
		http.Redirect(w, r, currentURL(r), http.StatusFound)
		return
	}
	defer file.Close()

	content, err := io.ReadAll(file)
	if err != nil {
		internalError(w, err)
		return
	}
	if len(content) > 0 {
		http.Error(w, "File size exceeds 0 bytes", http.StatusBadRequest)
		return
	}

	uuidFile, err := newUUID()
	if err != nil {
		internalError(w, err)
		return
	}

	savePath := uploadPath(filename)
	if isInvalidPath(savePath) {
		http.Error(w, "Invalid filename", http.StatusBadRequest)
		return
	}

	if err := os.WriteFile(savePath, content, 0o666); err != nil {
		internalError(w, err)
		return
	}

	if _, err := app.db.Exec("INSERT INTO files (filename, uuid) VALUES (?, ?)", filename, uuidFile); err != nil {
		internalError(w, err)
		return
	}

	w.Header().Set("Location", "uploads/"+uuidFile)
	w.WriteHeader(http.StatusFound)
}

func (app *application) viewFile(w http.ResponseWriter, r *http.Request) {
	if !allowsRead(r.Method) {
		methodNotAllowed(w)
		return
	}

	uuidFile := strings.TrimPrefix(r.URL.Path, "/uploads/")
	if uuidFile == "" || strings.Contains(uuidFile, "/") {
		http.NotFound(w, r)
		return
	}

	file, err := app.findFile(uuidFile)
	if errors.Is(err, sql.ErrNoRows) {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}
	if err != nil {
		internalError(w, err)
		return
	}

	f, err := os.Open(uploadPath(file.Filename))
	if err != nil {
		internalError(w, err)
		return
	}
	defer f.Close()

	info, err := f.Stat()
	if err != nil {
		internalError(w, err)
		return
	}

	http.ServeContent(w, r, filepath.Base(file.Filename), info.ModTime(), f)
}

func (app *application) renameFile(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		methodNotAllowed(w)
		return
	}

	uuidFile := strings.TrimPrefix(r.URL.Path, "/rename/")
	if uuidFile == "" || strings.Contains(uuidFile, "/") {
		http.NotFound(w, r)
		return
	}

	var payload struct {
		NewFilename *string `json:"new_filename"`
	}
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Operation failed "+err.Error(), http.StatusBadRequest)
		return
	}

	if err := app.renameStoredFile(uuidFile, payload.NewFilename); err != nil {
		var invalid invalidFilenameError
		if errors.As(err, &invalid) {
			http.Error(w, "Invalid filename", http.StatusBadRequest)
			return
		}

		http.Error(w, "Operation failed "+err.Error(), http.StatusBadRequest)
		return
	}

	http.Redirect(w, r, "/", http.StatusFound)
}
