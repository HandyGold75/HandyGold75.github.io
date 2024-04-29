//go:build js && wasm

package WebKit

import "syscall/js"

type (
	Element struct{ el js.Value }
)

func GetElement(id string) (Element, error) {
	dom := js.Global().Get("document")

	el := dom.Call("getElementById", id)
	if el.IsUndefined() {
		return Element{}, ErrWebKit.ElementNotFound
	}

	return Element{el: el}, nil
}

func (obj Element) SetElement(html string) {
	obj.el.Set("innerHTML", html)
}

func (obj Element) Inner() string {
	return obj.el.Get("innerHTML").String()
}
