//go:build js && wasm

package Tools

var (
	ForcePage               = func(string) {}
	SetLoginSuccessCallback = func(func()) {}
)
