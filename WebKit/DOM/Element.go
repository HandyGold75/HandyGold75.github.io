//go:build js && wasm

package DOM

import (
	"WebKit"
	"syscall/js"
)

type (
	Element struct{ el js.Value }
)

func GetElement(id string) (Element, error) {
	el := js.Global().Get("document").Call("getElementById", id)
	if el.IsUndefined() || el.IsNaN() || el.IsNull() {
		return Element{}, WebKit.ErrWebKit.ElementNotFound
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
	obj.el.Set("disabled", false)
}

func (obj Element) Disable() {
	obj.el.Set("disabled", true)
}

func (obj Element) EventAdd(action string, f func(js.Value)) {
	obj.el.Call("addEventListener", action, js.FuncOf(func(e js.Value, a []js.Value) any { f(e); return nil }))
}

func (obj Element) EventClear() {
	obj.el.Set("outerHTML", obj.el.Get("outerHTML"))
}
