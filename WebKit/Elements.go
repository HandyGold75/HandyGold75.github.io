//go:build js && wasm

package WebKit

import "syscall/js"

type (
	Elements struct{ els js.Value }
)

func GetElements(class string) (Elements, error) {
	dom := js.Global().Get("document")

	els := dom.Call("getElementsByClassName", class)
	if els.IsUndefined() || els.Length() < 1 {
		return Elements{}, ErrWebKit.ElementNotFound
	}

	return Elements{els: els}, nil
}

func (obj Elements) SetElements(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Set("innerHTML", html)
	}
}

func (obj Elements) Inners() []string {
	els := []string{}
	for i := 0; i < obj.els.Length(); i++ {
		els = append(els, obj.els.Index(i).Get("innerHTML").String())
	}

	return els
}
