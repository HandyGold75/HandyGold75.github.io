//go:build js && wasm

package Sheets

func PageQuerys(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback
	ShowSheet("Querys", "db-query")
}
