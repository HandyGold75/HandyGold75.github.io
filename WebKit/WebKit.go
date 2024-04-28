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

	DomObj struct {
		value js.Value
	}
)

var (
	ErrWebKit = errWebKit{
		ElementNotFound: errors.New("element not found"),
	}
)

func GetElement(id string) (DomObj, error) {
	dom := js.Global().Get("document")

	el := dom.Call("getElementById", id)
	if el.IsUndefined() {
		return DomObj{}, ErrWebKit.ElementNotFound
	}

	return DomObj{value: el}, nil
}

func GetElements(class string) (DomObj, error) {
	dom := js.Global().Get("document")

	els := dom.Call("getElementsByClassName", class)
	if els.IsUndefined() || els.Length() < 1 {
		return DomObj{}, ErrWebKit.ElementNotFound
	}

	return DomObj{value: els}, nil

}
