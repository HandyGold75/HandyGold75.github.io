//go:build js && wasm

package WebKit

import (
	"errors"
)

var (
	ErrWebKit = struct {
		ElementNotFound  error
		ElementsNotFound error
	}{
		ElementNotFound:  errors.New("element not found"),
		ElementsNotFound: errors.New("elements not found"),
	}
)
