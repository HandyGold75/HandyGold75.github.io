//go:build js && wasm

package JS

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"errors"
	"strings"
	"syscall/js"
)

type (
	DB struct {
		db js.Value
	}
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

// https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs#length_limitations
func Download(fileName string, dataType string, data []byte) error {
	js.Global().Call("fetch", "data:"+dataType+","+UriFriendlyfy(string(data))).Call("then", js.FuncOf(func(el js.Value, evs []js.Value) any {
		if len(evs) < 0 {
			return nil
		}
		evs[0].Call("blob").Call("then", js.FuncOf(func(el js.Value, evs []js.Value) any {
			if len(evs) < 0 {
				return nil
			}

			body, err := DOM.GetElement("body")
			if err != nil {
				return err
			}
			body.InnerAddSurfix(HTML.HTML{Tag: "a",
				Attributes: map[string]string{
					"id":       "download_" + fileName,
					"type":     dataType,
					"download": fileName,
					"href":     js.Global().Get("URL").Call("createObjectURL", evs[0]).String(),
				},
				Styles: map[string]string{"display": "none"},
			}.String())

			download, err := DOM.GetElement("download_" + fileName)
			if err != nil {
				return err
			}
			download.Call("click")
			download.Remove()

			return nil
		}))
		return nil
	}))
	return nil
}

func FuncWrap(f func(el js.Value, evs []js.Value)) js.Func {
	return js.FuncOf(func(el js.Value, evs []js.Value) any { f(el, evs); return nil })
}

func FuncWrapSimple(f func()) js.Func {
	return js.FuncOf(func(el js.Value, evs []js.Value) any { f(); return nil })
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

func PopupButtons(title string, txt string, options []string, callback func(string)) error {
	spacer := HTML.HTML{Tag: "div"}.String()

	btns := []string{}
	for _, option := range options {
		btns = append(btns, HTML.HTML{
			Tag:        "button",
			Attributes: map[string]string{"id": "popup_" + option, "class": "dark medium popup_buttons"},
			Styles:     map[string]string{"min-width": "10%"},
			Inner:      option,
		}.String())
	}

	if err := ensurePopupDiv(title, txt, spacer+strings.Join(btns, spacer)+spacer); err != nil {
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

		value := strings.Replace(el.Get("id").String(), "popup_", "", 1)

		AfterDelay(250, func() {
			elPop.Remove()
			callback(value)
		})
	})

	return nil
}

func PopupInput(title string, txt string, callback func(string)) error {
	spacer := HTML.HTML{Tag: "div"}.String()

	input := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"type": "text", "id": "popup_input"},
		Styles:     map[string]string{"min-width": "60%"},
	}.String()
	button := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "popup_confirm", "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      "confirm",
	}.String()

	if err := ensurePopupDiv(title, txt, spacer+input+spacer+button+spacer); err != nil {
		return err
	}

	el, err := DOM.GetElement("popup_confirm")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elInp, err := DOM.GetElement("popup_input")
		if err != nil {
			Alert(err.Error())
			return
		}
		value := elInp.AttributeGet("value")

		elPop, err := DOM.GetElement("popup")
		if err != nil {
			Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		AfterDelay(250, func() {
			elPop.Remove()
			callback(value)
		})
	})

	el, err = DOM.GetElement("popup_input")
	if err != nil {
		return err
	}
	el.EventAdd("keyup", func(el js.Value, evs []js.Value) {
		if evs[0].Get("key").String() != "Enter" {
			return
		}
		value := el.Get("value").String()

		elPop, err := DOM.GetElement("popup")
		if err != nil {
			Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		AfterDelay(250, func() {
			elPop.Remove()
			callback(value)
		})
	})

	return nil
}

func PopupFile(title string, txt string, callback func(string, []byte)) error {
	spacer := HTML.HTML{Tag: "div"}.String()

	input := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"type": "file", "id": "popup_input"},
		Styles:     map[string]string{"display": "none"},
	}.String()
	file := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "popup_file"},
		Styles:     map[string]string{"color": "#bff"},
		Inner:      "Upload",
	}.String()
	label := HTML.HTML{Tag: "label",
		Attributes: map[string]string{"class": "input"},
		Styles:     map[string]string{"min-width": "60%"},
		Inner:      input + file,
	}.String()

	button := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "popup_confirm", "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      "confirm",
	}.String()

	if err := ensurePopupDiv(title, txt, spacer+label+spacer+button+spacer); err != nil {
		return err
	}

	el, err := DOM.GetElement("popup_confirm")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elInp, err := DOM.GetElement("popup_input")
		if err != nil {
			Alert(err.Error())
			return
		}
		nameSplit := strings.Split(elInp.AttributeGet("value"), "\\")

		elPop, err := DOM.GetElement("popup")
		if err != nil {
			Alert(err.Error())
			return
		}

		reader := js.Global().Get("FileReader").New()
		reader.Set("onload", js.FuncOf(func(el js.Value, args []js.Value) any {
			in := js.Global().Get("Uint8Array").New(el.Get("result"))
			result := make([]byte, in.Get("length").Int())
			js.CopyBytesToGo(result, in)

			elPop.StyleSet("opacity", "0")

			AfterDelay(250, func() {
				elPop.Remove()
				callback(nameSplit[len(nameSplit)-1], result)
			})

			return nil
		}))
		reader.Call("readAsArrayBuffer", elInp.El.Get("files").Index(0))
	})

	el, err = DOM.GetElement("popup_input")
	if err != nil {
		return err
	}
	el.EventAdd("change", func(el js.Value, evs []js.Value) {
		elFile, err := DOM.GetElement("popup_file")
		if err != nil {
			Alert(err.Error())
			return
		}

		nameSplit := strings.Split(el.Get("value").String(), "\\")
		elFile.InnerSet(nameSplit[len(nameSplit)-1])

	})

	return nil
}
