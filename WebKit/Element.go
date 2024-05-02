//go:build js && wasm

package WebKit

import (
	"syscall/js"
)

type (
	Element struct{ el js.Value }
)

func GetElement(id string) (Element, error) {
	el := Dom().Call("getElementById", id)
	if el.IsUndefined() || el.IsNaN() || el.IsNull() {
		return Element{}, ErrWebKit.ElementNotFound
	}
	return Element{el: el}, nil
}

func (obj Element) InnerSet(html string) {
	obj.el.Set("innerHTML", html)
}

func (obj Element) InnerGet() string {
	return obj.el.Get("innerHTML").String()
}

func (obj Element) InnerAddPrefix(html string) {
	obj.el.Set("innerHTML", html+obj.el.Get("innerHTML").String())
}

func (obj Element) InnerAddSurfix(html string) {
	obj.el.Set("innerHTML", obj.el.Get("innerHTML").String()+html)
}

func (obj Element) InnerClear() {
	obj.el.Set("innerHTML", "")
}

func (obj Element) MoveTo(target Element) {
	target.el.Call("after", obj.el)
	target.el.Call("remove")
}

func (obj Element) MoveToAsChild(target Element) {
	target.el.Call("appendChild", obj.el)
}

func (obj Element) CopyTo(target Element) {
	el := obj.el.Call("cloneNode", true)
	target.el.Call("after", el)
	target.el.Call("remove")
}

func (obj Element) CopyToAsChild(target Element) {
	el := obj.el.Call("cloneNode", true)
	target.el.Call("appendChild", el)
}

func (obj Element) Remove() {
	obj.el.Call("remove")
}

func (obj Element) Enable() {
	obj.el.Get("style").Set("disabled", false)
}

func (obj Element) Disable() {
	obj.el.Get("style").Set("disabled", true)
}
