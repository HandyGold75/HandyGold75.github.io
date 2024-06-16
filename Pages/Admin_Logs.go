//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

func LogListCallback(res string, resBytes []byte, resErr error) {
	if resErr == WebKit.ErrWebKit.HTTPUnauthorized || resErr == WebKit.ErrWebKit.HTTPNoServerSpecified {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Logs") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	logs := map[string][]string{}
	err := json.Unmarshal(resBytes, &logs)
	if err != nil {
		fmt.Println(err)
		return
	}

	logTypes := HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	for k := range logs {
		logTypes += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark medium logs_types_buttons"},
			Inner:      k,
		}.String()
	}
	logTypes += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	el, err := DOM.GetElement("logs_types")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(logTypes)

	els, err := DOM.GetElements("logs_types_buttons")
	if err != nil {
		fmt.Println(err)
		return
	}

	els.StylesSet("min-width", strconv.Itoa(min(10, 100/len(logs)))+"%")
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		selectedLog := el.Get("innerHTML").String()
		log, ok := logs[selectedLog]
		if !ok {
			fmt.Println(err)
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
			fmt.Println(err)
			return
		}
		elDates.InnerSet(logDates)

		els, err := DOM.GetElements("logs_types_dates")
		if err != nil {
			fmt.Println(err)
			return
		}

		els.StylesSet("min-width", strconv.Itoa(min(5, 100/len(logs)))+"%")
		els.EventsAdd("click", func(el js.Value, evs []js.Value) {
			HTTP.Send(getLogCallback, "logs", "get", selectedLog, el.Get("innerHTML").String())
		})
	})
}

func getLogCallback(res string, resBytes []byte, resErr error) {
	log := []string{}
	err := json.Unmarshal(resBytes, &log)
	if err != nil {
		fmt.Println(err)
		return
	}

	rows := ""
	lines := strings.Split(strings.Join(log, ""), "<EOR>\n")
	slices.Reverse(lines)
	for _, line := range lines {
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

		rows += HTML.HTML{Tag: "div",
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
	}

	el, err := DOM.GetElement("logs_out")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(rows)
}

func PageAdminLogs() {
	if !HTTP.IsMaybeAuthenticated() {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Logs") }) }
		JS.Async(func() { ForcePage("Login") })
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Logs"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_types"},
		Styles: map[string]string{"display": "flex",
			"width":         "95%",
			"background":    "#202020",
			"border-left":   "2px solid #111",
			"border-right":  "2px solid #111",
			"border-top":    "2px solid #111",
			"border-radius": "10px 10px 0px 0px"},
	}.String()

	dates := HTML.HTML{Tag: "div",

		Attributes: map[string]string{"id": "logs_dates"},
		Styles: map[string]string{"display": "flex",
			"width":         "95%",
			"background":    "#202020",
			"border-left":   "2px solid #111",
			"border-right":  "2px solid #111",
			"border-bottom": "2px solid #111",
			"border-radius": "0px 0px 10px 10px"},
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
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + types + dates + out)

	HTTP.Send(LogListCallback, "logs", "list")
}
