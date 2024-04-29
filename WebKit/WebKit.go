//go:build js && wasm

package WebKit

import (
	"errors"
	"syscall/js"
)

type (
	errWebKit struct {
		ElementNotFound error
	}
)

var (
	ErrWebKit = errWebKit{
		ElementNotFound: errors.New("element not found"),
	}
)

func Dom() js.Value {
	return js.Global().Get("document")
}
