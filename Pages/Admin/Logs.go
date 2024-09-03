//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

var (
	availableLogs = map[string][]string{}
	isBusy        = false
)

func showLogs(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		return
	} else if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if !hasAccess {
		Widget.PopupAlert("Error", "unauthorized", func() {})
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Logs"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_types"},
		Styles: map[string]string{"display": "flex",
			"width":         "90%",
			"background":    "#202020",
			"border-left":   "2px solid #111",
			"border-right":  "2px solid #111",
			"border-top":    "2px solid #111",
			"border-radius": "10px 10px 0px 0px",
		},
	}.String()

	dates := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_dates"},
		Styles: map[string]string{"display": "flex",
			"width":         "90%",
			"max-height":    "0px",
			"background":    "#202020",
			"border-left":   "2px solid #111",
			"border-right":  "2px solid #111",
			"border-bottom": "2px solid #111",
			"border-radius": "0px 0px 10px 10px",
			"transition":    "max-height 0.25s",
		},
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_out"},
		Styles: map[string]string{
			"width":       "95%",
			"margin":      "15px auto",
			"white-space": "pre",
			"font-family": "Hack",
		},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + types + dates + out)

	HTTP.Send(LogListCallback, "logs", "list")
}

func LogListCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		return
	} else if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	availableLogs = map[string][]string{}
	err := json.Unmarshal(resBytes, &availableLogs)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	logTypes := HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	for k := range availableLogs {
		if len(availableLogs[k]) == 0 {
			continue
		}

		logTypes += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark medium logs_types_buttons"},
			Inner:      k,
		}.String()
	}
	logTypes += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	el, err := DOM.GetElement("logs_types")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet(logTypes)

	els, err := DOM.GetElements("logs_types_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.StylesSet("min-width", strconv.Itoa(min(10, 100/len(availableLogs)))+"%")
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		elDates, err := DOM.GetElement("logs_dates")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}

		delay := 0
		if elDates.StyleGet("max-height") != "0px" {
			elDates.StyleSet("max-height", "0px")
			delay = 250
		}

		selectedLog := el.Get("innerHTML").String()
		JS.AfterDelay(delay, func() {
			showLogDates(selectedLog)
		})
	})
}

func showLogDates(selected string) {
	log, ok := availableLogs[selected]
	if !ok {
		Widget.PopupAlert("Error", "log \""+selected+"\" not available!", func() {})
		return
	}

	logDates := HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	for _, v := range log {
		logDates += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark small logs_types_dates"},
			Inner:      v,
		}.String()
	}
	logDates += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	elDates, err := DOM.GetElement("logs_dates")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDates.InnerSet(logDates)
	elDates.StyleSet("max-height", "40px")

	els, err := DOM.GetElements("logs_types_dates")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.StylesSet("min-width", strconv.Itoa(min(5, 100/len(availableLogs)))+"%")
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(getLogCallback, "logs", "get", selected, el.Get("innerHTML").String())
	})
}

func getLogCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		return
	} else if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	log := []string{}
	err := json.Unmarshal(resBytes, &log)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	lines := strings.Split(strings.Join(log, ""), "<EOR>\n")
	slices.Reverse(lines)

	showLogContent(lines)
}

func showLogContent(lines []string) {
	if isBusy {
		return
	}
	isBusy = true

	el, err := DOM.GetElement("logs_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet("")

	for i, line := range lines {
		if len(line) <= 0 {
			continue
		}

		cols := ""
		lineSplit := strings.Split(line, "<SEP>")
		for i, col := range lineSplit {
			if i == 0 {
				t, err := time.Parse(time.RFC3339Nano, col)
				if err == nil {
					col = t.Format(time.DateTime)
				}
			}

			if i == len(lineSplit)-1 {
				cols += HTML.HTML{Tag: "p",
					Styles: map[string]string{
						"scrollbar-width": "thin",
						"scrollbar-color": "transparent transparent",
						"overflow":        "scroll",
					},
					Inner: col,
				}.String()

				continue
			}

			cols += HTML.HTML{Tag: "p",
				Styles: map[string]string{
					"min-width":       "10%",
					"border-right":    "2px dashed #151515",
					"border-radius":   "0px",
					"scrollbar-width": "thin",
					"scrollbar-color": "transparent transparent",
					"overflow":        "scroll",
				},
				Inner: col,
			}.String()
		}

		row := HTML.HTML{Tag: "div",
			Styles: map[string]string{
				"display":       "flex",
				"padding":       "0px",
				"margin-bottom": "-2px",
				"background":    "#202020",
				"border":        "2px solid #151515",
				"border-radius": "0px",
				"font-size":     "75%",
			},
			Inner: cols,
		}.String()

		JS.AfterDelay(i*5, func() {
			el.InnerAddSurfix(row)
		})
	}

	JS.AfterDelay((len(lines)-1)*5, func() { isBusy = false })
}

func PageLogs(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	HTTP.HasAccessTo(showLogs, "logs")
}
