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

func LogListCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
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

		logTypes += HTML.HTML{Tag: "button", Inner: k,
			Attributes: map[string]string{"class": "dark medium logs_types_buttons"},
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
		Widget.AnimateReplace("logs_dates", "max-height", "0px", "50px", 250, func() { showLogDates(el.Get("innerHTML").String()) }, func() {})
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
		logDates += HTML.HTML{Tag: "button", Inner: v,
			Attributes: map[string]string{"class": "dark small logs_types_dates"},
		}.String()
	}
	logDates += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	elDates, err := DOM.GetElement("logs_dates")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDates.InnerSet(logDates)

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
	if resErr != nil {
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

	JS.ForEach(lines, 5, func(line string, last bool) bool {
		if len(line) <= 0 {
			return true
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
				cols += HTML.HTML{Tag: "p", Inner: col,
					Styles: map[string]string{
						"scrollbar-width": "thin",
						"scrollbar-color": "transparent transparent",
						"overflow":        "scroll",
					},
				}.String()

				continue
			}

			cols += HTML.HTML{Tag: "p", Inner: col,
				Styles: map[string]string{
					"min-width":       "10%",
					"border-right":    "2px dashed #151515",
					"border-radius":   "0px",
					"scrollbar-width": "thin",
					"scrollbar-color": "transparent transparent",
					"overflow":        "scroll",
				},
			}.String()
		}

		row := HTML.HTML{Tag: "div", Inner: cols,
			Styles: map[string]string{
				"display":       "flex",
				"padding":       "0px",
				"margin-bottom": "-2px",
				"background":    "#202020",
				"border":        "2px solid #151515",
				"border-radius": "0px",
				"font-size":     "75%",
			},
		}.String()

		el, err := DOM.GetElement("logs_out")
		if err != nil {
			isBusy = false
			return false
		}
		el.InnerAddSurfix(row)

		if last {
			isBusy = false
		}
		return true
	})
}

func showLogs() {
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

func PageLogs() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("logs", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showLogs()
		}
	})
}
