//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"fmt"
	"strconv"
	"strings"
	"syscall/js"
)

func PageConsole() {
	header := HTML.HTML{Tag: "h1", Inner: "Console"}.String()

	consoleOut := HTML.HTML{Tag: "div", Styles: map[string]string{"overflow": "scroll"}, Inner: strings.Repeat("text<br>", 50)}.String()

	consoleDiv := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "console_div"},
		Styles:     map[string]string{"width": "95%", "height": "0px", "background": "#111", "transistion": "height 0.1s"},
		Inner:      consoleOut,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + consoleDiv)

	JS.OnResizeAdd("Console", func(event js.Value) {
		el, err := DOM.GetElement("footer")
		if err != nil {
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}

		height, err := strconv.Atoi(el.El.Get("outerHeight").String())
		if err != nil {
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}

		el, err = DOM.GetElement("console_div")
		if err != nil {
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}
		el.StyleSet("height", strconv.Itoa(height))
	})
}
