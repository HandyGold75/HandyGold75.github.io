//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"strconv"
	"strings"
	"syscall/js"
)

var (
	CommandHistory         = []string{""}
	CommandHistorySelected = -1
	Token                  = ""
)

func commandSubmitCallback(res string, resBytes []byte, resErr error) {
	elIn, errIn := DOM.GetElement("console_in")
	if errIn != nil {
		Widget.PopupAlert("Error", errIn.Error(), func() {})
		return
	}
	elIn.Enable()
	elIn.El.Call("focus")

	elArrow, errArrow := DOM.GetElement("console_arrow")
	if errArrow != nil {
		Widget.PopupAlert("Error", errArrow.Error(), func() {})
		return
	}
	elArrow.StyleSet("color", "#5F5")

	if resErr != nil {
		res = resErr.Error()
	} else if res == "" && len(resBytes) > 0 {
		res = string(resBytes)
	}

	elOut, errOut := DOM.GetElement("console_out")
	if errOut != nil {
		Widget.PopupAlert("Error", errOut.Error(), func() {})
		return
	}

	for line := range strings.SplitSeq(strings.ReplaceAll(res, "\r", ""), "\n") {
		if line == "" {
			line = " "
		}

		elOut.InnerAddSurfix(HTML.HTML{
			Tag: "p", Inner: strings.ReplaceAll(strings.ReplaceAll(line, "<", "&lt"), ">", "&gt"),
			Styles: map[string]string{"text-align": "left"},
		}.String())
	}

	elOut.El.Get("lastElementChild").Call("scrollIntoView")
}

func commandEdited(el js.Value, evs []js.Value) {
	elIn, err := DOM.GetElement("console_in")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
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
		elIn.AttributeSet("value", CommandHistory[CommandHistorySelected])

		return

	} else if key == "ArrowDown" {
		if CommandHistorySelected <= 0 {
			return
		}

		CommandHistorySelected -= 1
		if evs[0].Get("ctrlKey").Bool() {
			CommandHistorySelected = 0
		}
		elIn.AttributeSet("value", CommandHistory[CommandHistorySelected])

		return

	} else if key != "Enter" {
		return
	}

	input := elIn.AttributeGet("value")
	if input == "" {
		return
	}

	elArrow, err := DOM.GetElement("console_arrow")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elArrow.StyleSet("color", "#F55")

	elIn.Disable()

	CommandHistorySelected = -1
	CommandHistory = append([]string{input}, CommandHistory...)

	inputSplit := strings.Split(input, " ")
	com := inputSplit[0]
	args := inputSplit[1:]

	HTTP.Send(commandSubmitCallback, com, args...)
	elIn.AttributeSet("value", "")
}

func showConsole() {
	header := HTML.HTML{Tag: "h1", Attributes: map[string]string{"id": "console_header"}, Inner: "Console"}.String()

	consoleOut := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "console_out"},
		Styles:     map[string]string{"height": "0px", "white-space": "pre", "font-family": "Hack", "background": "#111", "color": "#f7e163", "border-radius": "10px", "overflow": "scroll"},
	}.String()

	consoleIn := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"type": "text", "id": "console_in", "placeholder": "command ...args"},
		Styles:     map[string]string{"width": "95%", "margin": "0px 0px -2px -2px", "padding": "3px 2.5%", "border-radius": "10px", "border-color": "#f7e163"},
		Prefix: HTML.HTML{
			Tag: "p", Inner: ">",
			Attributes: map[string]string{"id": "console_arrow"},
			Styles:     map[string]string{"position": "absolute", "padding": "5px 0px 5px 0.5em", "text-align": "left", "color": "#5F5", "font-weight": "bold"},
		}.String(),
	}.String()

	consoleDiv := HTML.HTML{
		Tag: "div", Inner: consoleOut + consoleIn,
		Attributes: map[string]string{"id": "console_div"},
		Styles:     map[string]string{"width": "95%", "margin": "10px auto", "padding": "2px", "background": "#111", "transition": "height 1s"},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + consoleDiv)

	JS.OnResizeAdd("Console", func() {
		height := JS.GetVP()[0] - 8

		in, err := DOM.GetElement("console_in")
		if err != nil {
			JS.OnResizeDelete("Console")
			return
		}
		height -= in.El.Get("offsetHeight").Int()

		header, err := DOM.GetElement("console_header")
		if err != nil {
			JS.OnResizeDelete("Console")
			return
		}
		height -= header.El.Get("offsetHeight").Int() + 20

		footer, err := DOM.GetElement("footer")
		if err != nil {
			JS.OnResizeDelete("Console")
			return
		}
		height -= footer.El.Get("offsetHeight").Int() + 10

		out, err := DOM.GetElement("console_out")
		if err != nil {
			JS.OnResizeDelete("Console")
			return
		}
		out.StyleSet("height", strconv.Itoa(height-18-10)+"px")
	})

	el, err := DOM.GetElement("console_in")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("keyup", commandEdited)
	el.El.Call("focus")
}

func PageConsole() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("help", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showConsole()
		}
	})
}
