//go:build js && wasm

package Sheets

func PageAssets() {
	pageName = "Assets"
	dbName = "db-asset"
	ShowSheet()
}
