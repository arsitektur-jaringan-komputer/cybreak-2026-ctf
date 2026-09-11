package main

import (
	"errors"
	"io"
	"mime"
	"net/http"
	"path/filepath"
	"strings"
)

func rawUploadedFile(r *http.Request, fieldName string) (io.ReadCloser, string, error) {
	reader, err := r.MultipartReader()
	if err != nil {
		return nil, "", err
	}

	for {
		part, err := reader.NextPart()
		if errors.Is(err, io.EOF) {
			return nil, "", http.ErrMissingFile
		}
		if err != nil {
			return nil, "", err
		}

		if part.FormName() != fieldName {
			_ = part.Close()
			continue
		}

		_, params, err := mime.ParseMediaType(part.Header.Get("Content-Disposition"))
		if err != nil {
			_ = part.Close()
			return nil, "", err
		}

		filename, ok := params["filename"]
		if !ok {
			_ = part.Close()
			return nil, "", http.ErrMissingFile
		}

		return part, filename, nil
	}
}

func uploadPath(filename string) string {
	if filepath.IsAbs(filename) {
		return filepath.Clean(filename)
	}
	return filepath.Clean(filepath.Join(uploadFolder, filename))
}

func isInvalidPath(path string) bool {
	return strings.Contains(path, "../") || strings.HasPrefix(path, "/")
}
