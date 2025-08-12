//go:build js && wasm

package Sheets

func PageLicenses() {
	pageName = "Licenses"
	dbName = "db-license"
	ShowSheet()
}
