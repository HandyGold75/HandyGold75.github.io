//go:build js && wasm

package DOM

import (
	"HandyGold75/WebKit"
	"syscall/js"
)

type (
	Elements struct{ Els js.Value }
)

func GetElements(class string) (Elements, error) {
	Els := js.Global().Get("document").Call("getElementsByClassName", class)
	if Els.IsUndefined() || Els.IsNaN() || Els.IsNull() || Els.Length() < 1 {
		return Elements{}, WebKit.ErrWebKit.ElementsNotFound
	}
	return Elements{Els: Els}, nil
}

func (obj Elements) InnersSet(html string) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set("innerHTML", html)
	}
}

func (obj Elements) InnersGet() []string {
	Els := []string{}
	for i := 0; i < obj.Els.Length(); i++ {
		Els = append(Els, obj.Els.Index(i).Get("innerHTML").String())
	}
	return Els
}

func (obj Elements) InnersAddPrefix(html string) {
	for i := 0; i < obj.Els.Length(); i++ {
		El := js.Global().Get("document").Call("createElement", "template")
		El.Set("innerHTML", html)

		Els := []any{}
		for i := 0; i < El.Get("content").Get("children").Length(); i++ {
			Els = append(Els, El.Get("content").Get("children").Index(i))
		}

		obj.Els.Index(i).Call("prepent", Els...)
	}
}

func (obj Elements) InnersAddSurfix(html string) {
	for i := 0; i < obj.Els.Length(); i++ {
		El := js.Global().Get("document").Call("createElement", "template")
		El.Set("innerHTML", html)

		Els := []any{}
		for i := 0; i < El.Get("content").Get("children").Length(); i++ {
			Els = append(Els, El.Get("content").Get("children").Index(i))
		}

		obj.Els.Index(i).Call("append", Els...)
	}
}

func (obj Elements) InnersClear(html string) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set("innerHTML", "")
	}
}

func (obj Elements) StylesGet(key string) []string {
	Els := []string{}
	for i := 0; i < obj.Els.Length(); i++ {
		Els = append(Els, obj.Els.Index(i).Get("style").Get(key).String())
	}
	return Els
}

func (obj Elements) StylesSet(key string, value string) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Get("style").Set(key, value)
	}
}

func (obj Elements) AttributesGet(key string) []string {
	Els := []string{}
	for i := 0; i < obj.Els.Length(); i++ {
		Els = append(Els, obj.Els.Index(i).Get(key).String())
	}
	return Els
}

func (obj Elements) AttributesSet(key string, value string) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set(key, value)
	}
}

func (obj Elements) MovesTo(target Element) {
	for i := 0; i < obj.Els.Length(); i++ {
		target.El.Call("after", obj.Els.Index(i))
	}
	target.El.Call("remove")
}

func (obj Elements) MovesToAsChild(target Element) {
	for i := 0; i < obj.Els.Length(); i++ {
		target.El.Call("appendChild", obj.Els.Index(i))
	}
}

func (obj Elements) CopysTo(target Element) {
	for i := 0; i < obj.Els.Length(); i++ {
		El := obj.Els.Index(i).Call("cloneNode", true)
		target.El.Call("after", El)
	}
	target.El.Call("remove")
}

func (obj Elements) CopysToAsChild(target Element) {
	for i := 0; i < obj.Els.Length(); i++ {
		El := obj.Els.Index(i).Call("cloneNode", true)
		target.El.Call("appendChild", El)
	}
}

func (obj Elements) Removes() {
	for obj.Els.Length() != 0 {
		obj.Els.Index(0).Call("remove")
	}
}

func (obj Elements) Enables() {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set("disabled", false)
	}
}

func (obj Elements) Disables() {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set("disabled", true)
	}
}

func (obj Elements) EventsAdd(action string, f func(el js.Value, evs []js.Value)) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Call("addEventListener", action, js.FuncOf(func(el js.Value, evs []js.Value) any { f(el, evs); return nil }))
	}
}

func (obj Elements) EventsClear() {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Set("outerHTML", obj.Els.Index(i).Get("outerHTML"))
	}
}

func (obj Elements) Calls(function string, args ...any) {
	for i := 0; i < obj.Els.Length(); i++ {
		obj.Els.Index(i).Call(function, args...)
	}
}
