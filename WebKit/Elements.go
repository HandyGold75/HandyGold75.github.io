//go:build js && wasm

package WebKit

import "syscall/js"

type (
	Elements struct{ els js.Value }
)

func GetElements(class string) (Elements, error) {
	els := Dom().Get("document").Call("getElementsByClassName", class)
	if els.IsUndefined() || els.IsNaN() || els.IsNull() || els.Length() < 1 {
		return Elements{}, ErrWebKit.ElementNotFound
	}
	return Elements{els: els}, nil
}

func (obj Elements) InnersSet(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Set("innerHTML", html)
	}
}

func (obj Elements) InnersGet() []string {
	els := []string{}
	for i := 0; i < obj.els.Length(); i++ {
		els = append(els, obj.els.Index(i).Get("innerHTML").String())
	}
	return els
}

func (obj Elements) InnersAddPrefix(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Set("innerHTML", html+obj.els.Index(i).Get("innerHTML").String())
	}
}

func (obj Elements) InnersAddSurfix(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Set("innerHTML", obj.els.Index(i).Get("innerHTML").String()+html)
	}
}

func (obj Elements) InnersClear(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Set("innerHTML", "")
	}
}

func (obj Elements) MovesTo(target Element) {
	for i := 0; i < obj.els.Length(); i++ {
		target.el.Call("after", obj.els.Index(i))
	}
	target.el.Call("remove")
}

func (obj Elements) MovesToAsChild(target Element) {
	for i := 0; i < obj.els.Length(); i++ {
		target.el.Call("appendChild", obj.els.Index(i))
	}
}

func (obj Elements) CopysTo(target Element) {
	for i := 0; i < obj.els.Length(); i++ {
		el := obj.els.Index(i).Call("cloneNode", true)
		target.el.Call("after", el)
	}
	target.el.Call("remove")
}

func (obj Elements) CopysToAsChild(target Element) {
	for i := 0; i < obj.els.Length(); i++ {
		el := obj.els.Index(i).Call("cloneNode", true)
		target.el.Call("appendChild", el)
	}
}

func (obj Elements) Removes(html string) {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Call("remove")
	}
}

func (obj Elements) Enables() {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Get("style").Set("disabled", false)
	}
}

func (obj Elements) Disables() {
	for i := 0; i < obj.els.Length(); i++ {
		obj.els.Index(i).Get("style").Set("disabled", true)
	}
}
