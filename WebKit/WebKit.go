//go:build js && wasm

package WebKit

import (
	"errors"
)

var (
	ErrWebKit = struct {
		ElementNotFound      error
		ElementsNotFound     error
		WSUnauthorized       error
		WSNoServerSpecified  error
		WSUnexpectedResponse error
	}{
		ElementNotFound:      errors.New("element not found"),
		ElementsNotFound:     errors.New("elements not found"),
		WSUnauthorized:       errors.New("unauthorized"),
		WSNoServerSpecified:  errors.New("no server specific"),
		WSUnexpectedResponse: errors.New("unexpected response"),
	}
)
