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

var (
	CommandHistory         = []string{""}
	CommandHistorySelected = -1
	Token                  = ""
)

func CommandEdited(el js.Value, evs []js.Value) {
	in, err := DOM.GetElement("console_in")
	if err != nil {
		fmt.Println(err)
		return
	}

	if len(evs) < 1 {
		fmt.Println("evs was not parsed")
		return
	}
	key := evs[0].Get("key").String()

	if key == "ArrowUp" {
		if CommandHistorySelected >= len(CommandHistory)-1 {
			return
		}

		CommandHistorySelected += 1
		if evs[0].Get("ctrlKey").Bool() {
			CommandHistorySelected = len(CommandHistory) - 1
		}
		in.AttributeSet("value", CommandHistory[CommandHistorySelected])

		return

	} else if key == "ArrowDown" {
		if CommandHistorySelected <= 0 {
			return
		}

		CommandHistorySelected -= 1
		if evs[0].Get("ctrlKey").Bool() {
			CommandHistorySelected = 0
		}
		in.AttributeSet("value", CommandHistory[CommandHistorySelected])

		return

	} else if key != "Enter" {
		return
	}

	com := in.AttributeGet("value")
	CommandHistorySelected = -1
	CommandHistory = append([]string{com}, CommandHistory...)

	fmt.Println("COM: " + com)
	in.AttributeSet("value", "")
}

func PageConsole() {
	Token := JS.CacheGet("token")
	if Token == "" {
		JS.Async(func() { ForcePage("Login") })
		return
	}

	header := HTML.HTML{Tag: "h1", Attributes: map[string]string{"id": "console_header"}, Inner: "Console"}.String()

	consoleOut := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "console_out"},
		Styles:     map[string]string{"height": "0px", "background": "#111", "color": "#f7e163", "border-radius": "10px", "overflow": "scroll"},
		Inner:      strings.Repeat("<p style='text-align: left; height: 1.5em'>text</p>", 10),
	}.String()

	consoleIn := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"type": "text", "id": "console_in", "placeholder": "> command ...args"},
		Styles:     map[string]string{"width": "100%", "margin": "0px 0px -2px -2px", "padding": "3px 0px", "border-radius": "0px 0px 10px 10px", "border-color": "#f7e163"},
	}.String()

	consoleDiv := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "console_div"},
		Styles:     map[string]string{"width": "95%", "padding": "2px", "background": "#111", "transistion": "height 1s"},
		Inner:      consoleOut + consoleIn,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + consoleDiv)

	JS.OnResizeAdd("Console", func() {
		height := JS.GetVP()[0] - 8

		in, err := DOM.GetElement("console_in")
		if err != nil {
			fmt.Print("Disabled onresize: Console > ")
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}
		height -= in.El.Get("offsetHeight").Int()

		header, err := DOM.GetElement("console_header")
		if err != nil {
			fmt.Print("Disabled onresize: Console > ")
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}
		height -= header.El.Get("offsetHeight").Int() + 20

		footer, err := DOM.GetElement("footer")
		if err != nil {
			fmt.Print("Disabled onresize: Console > ")
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}
		height -= footer.El.Get("offsetHeight").Int() + 10

		out, err := DOM.GetElement("console_out")
		if err != nil {
			fmt.Print("Disabled onresize: Console > ")
			fmt.Println(err)
			JS.OnResizeDelete("Console")
			return
		}
		out.StyleSet("height", strconv.Itoa(height-8-17)+"px")
	})

	el, err := DOM.GetElement("console_in")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("keyup", CommandEdited)
}
