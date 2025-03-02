//go:build js && wasm

package JS

import (
	"errors"
	"strings"
	"syscall/js"
)

type (
	DB struct {
		db js.Value
	}
)

var onResizeMapping = map[string]func(){}

func Log(msg any) {
	js.Global().Get("console").Call("log", msg)
}

func F5() {
	js.Global().Get("window").Get("location").Call("reload")
}

func GetVP() [2]int {
	return [2]int{js.Global().Get("window").Get("innerHeight").Int(), js.Global().Get("window").Get("innerWidth").Int()}
}

func GetScroll() [2]float64 {
	return [2]float64{js.Global().Get("window").Get("scrollY").Float(), js.Global().Get("window").Get("scrollX").Float()}
}

func New(global string, args ...any) js.Value {
	item := js.Global()
	for _, part := range strings.Split(global, ".") {
		item = item.Get(part)
	}
	return item.New(args...)
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

func ForEach[V any](slice []V, delay int, handler func(item V, last bool) bool) {
	if len(slice) == 0 {
		return
	}

	if !handler(slice[0], len(slice) == 1) {
		return
	}

	var fOf js.Func
	fOf = js.FuncOf(func(el js.Value, evs []js.Value) any {
		defer fOf.Release()
		ForEach(slice[1:], delay, handler)
		return nil
	})
	js.Global().Call("setTimeout", fOf, delay)
}

func ForEachCount[V any](slice []V, count, delay int, handler func(count int, item V, last bool) bool) {
	if len(slice) == 0 {
		return
	}

	if !handler(count, slice[0], len(slice) == 1) {
		return
	}

	var fOf js.Func
	fOf = js.FuncOf(func(el js.Value, evs []js.Value) any {
		defer fOf.Release()
		ForEachCount(slice[1:], count+1, delay, handler)
		return nil
	})
	js.Global().Call("setTimeout", fOf, delay)
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

func DBNew(onOpenCallback func(db DB, dbErr error), name string, stores []string, version int) {
	openReq := js.Global().Get("window").Get("indexedDB").Call("open", name, version)

	openReq.Set("onerror", js.FuncOf(func(el js.Value, evs []js.Value) any {
		onOpenCallback(DB{}, errors.New(openReq.Get("error").String()))
		return nil
	}))

	openReq.Set("onsuccess", js.FuncOf(func(el js.Value, evs []js.Value) any {
		db := DB{db: openReq.Get("result")}

		onOpenCallback(db, nil)
		db.db.Call("close")

		return nil
	}))

	openReq.Set("onupgradeneeded", js.FuncOf(func(el js.Value, evs []js.Value) any {
		db := DB{db: openReq.Get("result")}

		for _, store := range stores {
			if db.db.Get("objectStoreNames").Get("uris").IsUndefined() {
				db.db.Call("createObjectStore", store)
			}
		}

		return nil
	}))
}

func (db DB) GetAll(onGetCallback func(value map[string]string), store string) {
	tran := db.db.Call("transaction", store, "readonly")
	values := tran.Call("objectStore", store)

	results := map[string]string{}
	cursor := values.Call("openCursor")

	cursor.Set("onsuccess", js.FuncOf(func(el js.Value, evs []js.Value) any {
		cur := cursor.Get("result")
		if cur.Truthy() {
			results[cur.Get("primaryKey").String()] = cur.Get("value").String()
			cur.Call("continue")
		} else {
			onGetCallback(results)
		}

		return nil
	}))
}

func (db DB) GetAllKeys(onGetCallback func(keys []string), store string) {
	tran := db.db.Call("transaction", store, "readonly")
	values := tran.Call("objectStore", store)

	getReq := values.Call("getAllKeys")

	getReq.Set("onsuccess", js.FuncOf(func(el js.Value, evs []js.Value) any {
		res := getReq.Get("result")
		if res.IsUndefined() {
			onGetCallback([]string{})
			return nil
		}

		result := []string{}
		for i := 0; i < res.Length(); i++ {
			result = append(result, res.Index(i).String())
		}

		onGetCallback(result)
		return nil
	}))
}

func (db DB) Get(onGetCallback func(value string), store string, key string) {
	tran := db.db.Call("transaction", store, "readonly")
	values := tran.Call("objectStore", store)

	getReq := values.Call("get", key)

	getReq.Set("onsuccess", js.FuncOf(func(el js.Value, evs []js.Value) any {
		res := getReq.Get("result")
		if res.IsUndefined() {
			onGetCallback("")
			return nil
		}
		onGetCallback(res.String())
		return nil
	}))
}

func (db DB) Set(store string, key string, value string) {
	tran := db.db.Call("transaction", store, "readwrite")
	values := tran.Call("objectStore", store)
	values.Call("put", value, key)
}

func (db DB) Del(store string, key string) {
	tran := db.db.Call("transaction", store, "readwrite")
	values := tran.Call("objectStore", store)
	values.Call("delete", key)
}

func (db DB) Clear(store string) {
	tran := db.db.Call("transaction", store, "readwrite")
	values := tran.Call("objectStore", store)
	values.Call("clear")
}

func DBClear() {
	js.Global().Get("window").Get("indexedDB").Call("deleteDatabase", "Sonos")
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

func FuncWrap(f func(el js.Value, evs []js.Value)) js.Func {
	return js.FuncOf(func(el js.Value, evs []js.Value) any { f(el, evs); return nil })
}

func FuncWrapSimple(f func()) js.Func {
	return js.FuncOf(func(el js.Value, evs []js.Value) any { f(); return nil })
}
