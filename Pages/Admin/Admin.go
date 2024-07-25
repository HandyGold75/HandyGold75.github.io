//go:build js && wasm

package Admin

var (
	ForcePage               = func(string) {}
	SetLoginSuccessCallback = func(func()) {}
)
