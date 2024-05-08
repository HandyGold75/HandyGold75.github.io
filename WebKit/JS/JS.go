//go:build js && wasm

package JS

import "syscall/js"

var (
	onResizeMapping = map[string]func(js.Value){}
)

func Log(msg any) {
	js.Global().Get("console").Call("log", msg)
}

func F5() {
	js.Global().Get("window").Get("location").Call("reload")
}

func GetVP() [2]string {
	window := js.Global().Get("window")
	return [2]string{window.Get("innerHeight").String(), window.Get("innerWidth").String()}
}

func AfterDelay(delay int, f func(js.Value)) {
	js.Global().Call("setTimeout", js.FuncOf(func(e js.Value, a []js.Value) any { f(e); return nil }), delay)
}

func Async(f func(js.Value)) {
	js.Global().Call("setTimeout", js.FuncOf(func(e js.Value, a []js.Value) any { f(e); return nil }), 0)
}

func AtInterval(delay int, f func(js.Value)) {
	js.Global().Call("setInterval", js.FuncOf(func(e js.Value, a []js.Value) any { f(e); return nil }), delay)
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
	return js.Global().Get("window").Get("localStorage").Call("getItem", key).String()
}

func CacheSet(key string, value any) {
	js.Global().Get("window").Get("localStorage").Call("setItem", key, value)
}

func CacheClear() {
	js.Global().Get("window").Get("localStorage").Call("clear")
}

func Title(title string) {
	js.Global().Get("document").Set("title", title)
}

func onResizeAdd(key string, f func(js.Value)) {
	onResizeMapping[key] = f

	js.Global().Get("window").Set("onResize", js.FuncOf(func(e js.Value, a []js.Value) any {
		for _, f := range onResizeMapping {
			f(e)
		}
		return nil
	}))
}

func onResizeDelete(key string) {
	delete(onResizeMapping, key)
}
