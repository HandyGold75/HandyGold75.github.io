//go:build js && wasm

package Sheets

func PageTests(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback
	ShowSheet("Tests", "db-test")
}
