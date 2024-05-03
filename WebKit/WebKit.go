//go:build js && wasm

package WebKit

import (
	"errors"
)

var (
	ErrWebKit = struct {
		ElementNotFound error
	}{
		ElementNotFound: errors.New("element not found"),
	}
)
