//go:build js && wasm

package Sheets

func PageLicenses(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback
	ShowSheet("Licenses", "db-license")
}
