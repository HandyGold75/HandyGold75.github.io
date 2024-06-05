//go:build js && wasm

package WebKit

import (
	"errors"
)

var (
	ErrWebKit = struct {
		ElementNotFound        error
		ElementsNotFound       error
		HTTPUnauthorized       error
		HTTPNoServerSpecified  error
		HTTPUnexpectedResponse error
	}{
		ElementNotFound:        errors.New("element not found"),
		ElementsNotFound:       errors.New("elements not found"),
		HTTPUnauthorized:       errors.New("unauthorized"),
		HTTPNoServerSpecified:  errors.New("no server specific"),
		HTTPUnexpectedResponse: errors.New("unexpected response"),
	}
)
