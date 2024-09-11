//go:build js && wasm

package DOM

import (
	"HandyGold75/WebKit"
	"syscall/js"
)

type (
	Element struct{ El js.Value }
)

func GetElement(id string) (Element, error) {
	El := js.Global().Get("document").Call("getElementById", id)
	if El.IsUndefined() || El.IsNaN() || El.IsNull() {
		return Element{El: El}, WebKit.ErrWebKit.ElementNotFound
	}
	return Element{El: El}, nil
}

func (obj Element) InnerGet() string {
	return obj.El.Get("innerHTML").String()
}

func (obj Element) InnerSet(html string) {
	obj.El.Set("innerHTML", html)
}

func (obj Element) InnerAddPrefix(html string) {
	El := js.Global().Get("document").Call("createElement", "template")
	El.Set("innerHTML", html)

	Els := []any{}
	for i := 0; i < El.Get("content").Get("children").Length(); i++ {
		Els = append(Els, El.Get("content").Get("children").Index(i))
	}

	obj.El.Call("prepend", Els...)
}

func (obj Element) InnerAddSurfix(html string) {
	El := js.Global().Get("document").Call("createElement", "template")
	El.Set("innerHTML", html)

	Els := []any{}
	for i := 0; i < El.Get("content").Get("children").Length(); i++ {
		Els = append(Els, El.Get("content").Get("children").Index(i))
	}

	obj.El.Call("append", Els...)
}

func (obj Element) InnerAddPrefixRaw(html string) {
	obj.El.Set("innerHTML", html+obj.El.Get("innerHTML").String())
}

func (obj Element) InnerAddSurfixRaw(html string) {
	obj.El.Set("innerHTML", obj.El.Get("innerHTML").String()+html)
}

func (obj Element) InnerClear() {
	obj.El.Set("innerHTML", "")
}

func (obj Element) StyleGet(key string) string {
	return obj.El.Get("style").Get(key).String()
}

func (obj Element) StyleSet(key string, value string) {
	obj.El.Get("style").Set(key, value)
}

func (obj Element) AttributeGet(key string) string {
	return obj.El.Get(key).String()
}

func (obj Element) AttributeSet(key string, value string) {
	obj.El.Set(key, value)
}

func (obj Element) MoveTo(target Element) {
	target.El.Call("after", obj.El)
	target.El.Call("remove")
}

func (obj Element) MoveToAsChild(target Element) {
	target.El.Call("appendChild", obj.El)
}

func (obj Element) CopyTo(target Element) {
	El := obj.El.Call("cloneNode", true)
	target.El.Call("after", El)
	target.El.Call("remove")
}

func (obj Element) CopyToAsChild(target Element) {
	El := obj.El.Call("cloneNode", true)
	target.El.Call("appendChild", El)
}

func (obj Element) Remove() {
	obj.El.Call("remove")
}

func (obj Element) Enable() {
	obj.El.Set("disabled", false)
}

func (obj Element) Disable() {
	obj.El.Set("disabled", true)
}

func (obj Element) EventAdd(action string, f func(el js.Value, evs []js.Value)) {
	obj.El.Call("addEventListener", action, js.FuncOf(func(el js.Value, evs []js.Value) any { f(el, evs); return nil }))
}

func (obj Element) EventClear() {
	obj.El.Set("outerHTML", obj.El.Get("outerHTML"))
}

func (obj Element) Call(function string, args ...any) {
	obj.El.Call(function, args...)
}
