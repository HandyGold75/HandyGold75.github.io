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
	elBody, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	elBody.InnerAddSurfix(HTML.HTML{Tag: "a",
		Attributes: map[string]string{
			"id":       fileName + "_download",
			"href":     "data:text/json;charset=utf-8," + UriFriendlyfy(string(data)),
			"download": fileName + ".json"},
		Styles: map[string]string{"display": "none"},
	}.String())

	elDl, err := DOM.GetElement(fileName + "_download")
	if err != nil {
		return err
	}

	elDl.Call("click")
	elDl.Remove()

	return nil
}
