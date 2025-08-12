//go:build js && wasm

package Sheets

func PageTests() {
	pageName = "Tests"
	dbName = "db-test"
	ShowSheet()
}
