//go:build js && wasm

package JS

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"syscall/js"
)

var (
	onResizeMapping = map[string]func(){}
)

func Log(msg any) {
	js.Global().Get("console").Call("log", msg)
}

func F5() {
	js.Global().Get("window").Get("location").Call("reload")
}

func GetVP() [2]int {
	return [2]int{js.Global().Get("window").Get("innerHeight").Int(), js.Global().Get("window").Get("innerWidth").Int()}
}

func AfterDelay(delay int, f func()) {
	var fOf js.Func
	fOf = js.FuncOf(func(el js.Value, evs []js.Value) any { defer fOf.Release(); f(); return nil })
	js.Global().Call("setTimeout", fOf, delay)
}

func Async(f func()) {
	var fOf js.Func
	fOf = js.FuncOf(func(el js.Value, evs []js.Value) any { defer fOf.Release(); f(); return nil })
	js.Global().Call("setTimeout", fOf, 0)
}

func AtInterval(delay int, f func()) {
	js.Global().Call("setInterval", js.FuncOf(func(el js.Value, evs []js.Value) any { f(); return nil }), delay)
}

func Eval(com string) js.Value {
	return js.Global().Call("eval", com)
}

func UriFriendlyfy(uri string) string {
	return js.Global().Call("encodeURIComponent", uri).String()
}

func Alert(txt string) {
	js.Global().Get("window").Call("alert", txt)
}

func Confirm(txt string) bool {
	return js.Global().Get("window").Call("confirm", txt).Truthy()
}

func Prompt(txt string) string {
	return js.Global().Get("window").Call("alert", txt).String()
}

func CacheGet(key string) string {
	value := js.Global().Get("window").Get("localStorage").Call("getItem", key)
	if !value.Truthy() {
		return ""
	}
	return value.String()
}

func CacheSet(key string, value any) {
	js.Global().Get("window").Get("localStorage").Call("setItem", key, value)
}

func CacheClear() {
	js.Global().Get("window").Get("localStorage").Call("clear")
}

func ScrollToTop() {
	js.Global().Get("window").Call("scrollTo", 0, 0)
}

func Title(title string) {
	js.Global().Get("document").Set("title", title)
}

func OnResizeAdd(key string, f func()) {
	onResizeMapping[key] = f

	js.Global().Get("window").Set("onresize", js.FuncOf(func(el js.Value, evs []js.Value) any {
		for _, f := range onResizeMapping {
			f()
		}
		return nil
	}))

	f()
}

func OnResizeDelete(key string) {
	delete(onResizeMapping, key)
}

func Download(fileName string, data []byte) error {
	el, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	el.InnerAddSurfix(HTML.HTML{Tag: "a",
		Attributes: map[string]string{
			"id":       fileName + "_download",
			"href":     "data:text/json;charset=utf-8," + UriFriendlyfy(string(data)),
			"download": fileName + ".json"},
		Styles: map[string]string{"display": "none"},
	}.String())

	el, err = DOM.GetElement(fileName + "_download")
	if err != nil {
		return err
	}

	el.Call("click")
	el.Remove()

	return nil
}

func ensurePopupDiv(title string, txt string, buttons string) error {
	header := HTML.HTML{Tag: "h1", Inner: "Alert - " + title}.String()
	text := HTML.HTML{Tag: "p", Inner: txt}.String()
	btnDiv := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex", "margin": "10px 0px 0px 0px"},
		Inner:  buttons,
	}.String()

	div := HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"width":     "50%",
			"min-width": "500px",
			"max-width": "1000px",
			"margin":    "50px auto",
			"padding":   "10px",
			"border":    "2px solid #55F",
		},
		Inner: header + text + btnDiv,
	}.String()

	popDiv := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "popup"},
		Styles: map[string]string{
			"z-index":    "10000",
			"position":   "absolute",
			"top":        "0px",
			"left":       "0px",
			"width":      "100vw",
			"height":     "100vh",
			"margin":     "0px",
			"padding":    "0px",
			"background": "rgba(0, 0, 0, 0.5)",
			"opacity":    "0",
			"transition": "opacity 0.25s",
		},
		Inner: div,
	}.String()

	el, err := DOM.GetElement("body")
	if err != nil {
		return err
	}
	el.InnerAddSurfix(popDiv)

	AfterDelay(10, func() {
		el, err := DOM.GetElement("popup")
		if err != nil {
			return
		}
		el.StyleSet("opacity", "1")
	})

	return nil
}

func PopupAlert(title string, txt string, callback func()) error {
	spacer := HTML.HTML{Tag: "div"}.String()
	button := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "popup_continue", "class": "dark medium"},
		Inner:      "Continue",
	}.String()

	if err := ensurePopupDiv(title, txt, spacer+button+spacer); err != nil {
		return err
	}

	el, err := DOM.GetElement("popup_continue")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elPop, err := DOM.GetElement("popup")
		if err != nil {
			Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		AfterDelay(250, func() {
			elPop.Remove()
			callback()
		})
	})

	return nil
}

func PopupConfirm(title string, txt string, falseText string, trueText string, callback func(bool)) error {
	spacer := HTML.HTML{Tag: "div"}.String()
	btnTrue := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "popup_" + trueText, "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      trueText,
	}.String()
	btnFalse := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "popup_" + falseText, "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      falseText,
	}.String()

	if err := ensurePopupDiv(title, txt, spacer+btnFalse+spacer+btnTrue+spacer); err != nil {
		return err
	}

	els, err := DOM.GetElements("popup_buttons")
	if err != nil {
		return err
	}
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		elPop, err := DOM.GetElement("popup")
		if err != nil {
			Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		value := el.Get("id").String() == "popup_"+trueText

		AfterDelay(250, func() {
			elPop.Remove()
			callback(value)
		})
	})

	return nil
}
