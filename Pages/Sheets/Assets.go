//go:build js && wasm

package Sheets

func PageAssets(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback
	ShowSheet("Assets", "db-asset")
}
