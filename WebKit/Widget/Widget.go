//go:build js && wasm

package Widget

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
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

func ensurePopupDiv(title string, txt string, buttons string) error {
	if _, err := DOM.GetElement("popup"); err == nil {
		return errors.New("popup already active")
	}

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

	JS.AfterDelay(10, func() {
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
			JS.Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		JS.AfterDelay(250, func() {
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
			JS.Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		value := el.Get("id").String() == "popup_"+trueText

		JS.AfterDelay(250, func() {
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
			JS.Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		value := strings.Replace(el.Get("id").String(), "popup_", "", 1)

		JS.AfterDelay(250, func() {
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
			JS.Alert(err.Error())
			return
		}
		value := elInp.AttributeGet("value")

		elPop, err := DOM.GetElement("popup")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		JS.AfterDelay(250, func() {
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
			JS.Alert(err.Error())
			return
		}
		elPop.StyleSet("opacity", "0")

		JS.AfterDelay(250, func() {
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

	confirm := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "popup_confirm", "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      "confirm",
	}.String()

	cancel := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "popup_cancel", "class": "dark medium popup_buttons"},
		Styles:     map[string]string{"min-width": "10%"},
		Inner:      "cancel",
	}.String()

	if err := ensurePopupDiv(title, txt, spacer+label+spacer+cancel+spacer+confirm+spacer); err != nil {
		return err
	}

	el, err := DOM.GetElement("popup_cancel")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elPop, err := DOM.GetElement("popup")
		if err != nil {
			JS.Alert(err.Error())
			return
		}

		elPop.StyleSet("opacity", "0")

		JS.AfterDelay(250, func() {
			elPop.Remove()
		})
	})

	el, err = DOM.GetElement("popup_confirm")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elInp, err := DOM.GetElement("popup_input")
		if err != nil {
			JS.Alert(err.Error())
			return
		}

		name := elInp.AttributeGet("value")
		if name == "" {
			JS.Alert("no file selected")
			return
		}

		nameSplit := strings.Split(name, "\\")

		elPop, err := DOM.GetElement("popup")
		if err != nil {
			JS.Alert(err.Error())
			return
		}

		reader := js.Global().Get("FileReader").New()
		reader.Set("onload", js.FuncOf(func(el js.Value, args []js.Value) any {
			in := js.Global().Get("Uint8Array").New(el.Get("result"))
			result := make([]byte, in.Get("length").Int())
			js.CopyBytesToGo(result, in)

			elPop.StyleSet("opacity", "0")

			JS.AfterDelay(250, func() {
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
			JS.Alert(err.Error())
			return
		}

		nameSplit := strings.Split(el.Get("value").String(), "\\")
		elFile.InnerSet(nameSplit[len(nameSplit)-1])

	})

	return nil
}

// https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs#length_limitations
func Download(fileName string, dataType string, data []byte, onComplete func(error)) {
	fetch := js.Global().Call("fetch", "data:"+dataType+","+JS.UriFriendlyfy(string(data)))

	fetch.Call("then", js.FuncOf(func(el js.Value, evs []js.Value) any {
		if len(evs) < 0 {
			err := errors.New("failed to catch response")
			onComplete(err)
			return err.Error()
		}

		evs[0].Call("blob").Call("then", js.FuncOf(func(el js.Value, evs []js.Value) any {
			if len(evs) < 0 {
				err := errors.New("failed to catch response")
				onComplete(err)
				return err.Error()
			}

			body, err := DOM.GetElement("body")
			if err != nil {
				onComplete(err)
				return err.Error()
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
				onComplete(err)
				return err.Error()
			}
			download.Call("click")
			download.Remove()

			onComplete(nil)
			return nil
		}))
		return nil
	}))

	fetch.Call("catch", js.FuncOf(func(el js.Value, evs []js.Value) any {
		if len(evs) < 0 {
			err := errors.New("failed to catch response")
			onComplete(err)
			return err.Error()
		}

		err := errors.New(evs[0].Get("message").String())
		onComplete(err)
		return err.Error()
	}))
}