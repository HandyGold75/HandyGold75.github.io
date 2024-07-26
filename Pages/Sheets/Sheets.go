//go:build js && wasm

package Sheets

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"strconv"
	"syscall/js"
)

var (
	ForcePage               = func(string) {}
	SetLoginSuccessCallback = func(func()) {}

	isBusy = false

	pageName = ""
	dbName   = ""

	headers = map[string][]string{}
)

func accessCallback(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	} else if err != nil {
		JS.Alert(err.Error())
		return
	}

	if !hasAccess {
		JS.Alert("unauthorized")
		return
	}

	HTTP.Send(dbHeadersCallback, dbName, "header")
}

func dbHeadersCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	err := json.Unmarshal(resBytes, &headers)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: pageName}.String()

	btnSheets := HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	for header := range headers {
		btnSheets += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark medium sheets_showdb_buttons"},
			Inner:      header,
		}.String()
	}
	btnSheets += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	nav := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sheets_nav"},
		Styles: map[string]string{"display": "flex",
			"width":         "90%",
			"background":    "#202020",
			"border":        "2px solid #111",
			"border-radius": "10px",
		},
		Inner: btnSheets,
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sheets_out"},
		Styles: map[string]string{
			"width":       "95%",
			"margin":      "15px auto",
			"white-space": "pre",
			"font-family": "Hack",
		},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + nav + out)

	els, err := DOM.GetElements("sheets_showdb_buttons")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.StylesSet("min-width", strconv.Itoa(min(10, 100/len(headers)))+"%")
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		header := headers[el.Get("innerHTML").String()]
		cols := ""
		inps := ""
		for i, col := range header {
			if i == len(header)-1 {
				cols += HTML.HTML{Tag: "p",
					Styles: map[string]string{
						"width":           strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
						"scrollbar-width": "thin",
						"scrollbar-color": "transparent transparent",
						"overflow":        "scroll",
					},
					Inner: col,
				}.String()

				inps += HTML.HTML{Tag: "input",
					Styles: map[string]string{
						"width":         strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
						"margin":        "0px",
						"padding":       "0px",
						"border-radius": "0px",
					},
				}.String()

				continue
			}

			cols += HTML.HTML{Tag: "p",
				Styles: map[string]string{
					"width":           strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
					"border-right":    "2px dashed #151515",
					"border-radius":   "0px",
					"scrollbar-width": "thin",
					"scrollbar-color": "transparent transparent",
					"overflow":        "scroll",
				},
				Inner: col,
			}.String()

			inps += HTML.HTML{Tag: "input",
				Styles: map[string]string{
					"width":         strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
					"margin":        "0px",
					"padding":       "0px",
					"border-right":  "0px solid #55f",
					"border-radius": "0px",
				},
			}.String()
		}

		elOut, err := DOM.GetElement("sheets_out")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		elOut.InnerSet(HTML.HTML{Tag: "div",
			Styles: map[string]string{
				"display":       "flex",
				"padding":       "0px",
				"margin-bottom": "-2px",
				"background":    "#202020",
				"border":        "2px solid #151515",
				"border-radius": "0px",
				"font-size":     "150%",
				"font-weight":   "bold",
			},
			Inner: cols,
		}.String() + HTML.HTML{Tag: "div",
			Styles: map[string]string{
				"display":       "flex",
				"padding":       "0px",
				"margin-bottom": "-2px",
				"background":    "#202020",
				// "border":        "2px solid #151515",
				"border-radius": "0px",
				"font-size":     "100%",
				"font-weight":   "bold",
			},
			Inner: inps,
		}.String())

		HTTP.Send(dbReadCallback, dbName, "read", el.Get("innerHTML").String())
	})
}

func dbReadCallback(res string, resBytes []byte, resErr error) {
	if isBusy {
		return
	}
	isBusy = true

	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	data := [][]string{}
	err := json.Unmarshal(resBytes, &data)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	el, err := DOM.GetElement("sheets_out")
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	for i, record := range data {
		cols := ""
		for i, col := range record {
			if i == len(record)-1 {
				cols += HTML.HTML{Tag: "p",
					Styles: map[string]string{
						"width":           strconv.FormatFloat(100/float64(len(record)), 'f', -1, 64) + "%",
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
					"width":           strconv.FormatFloat(100/float64(len(record)), 'f', -1, 64) + "%",
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
				"font-size":     "100%",
			},
			Inner: cols,
		}.String()

		JS.AfterDelay(i*5, func() {
			el.InnerAddSurfix(row)
		})
	}

	JS.AfterDelay((len(data)-1)*5, func() { isBusy = false })
}

// pagename: Tests, dbname: db-test
func ShowSheet(pagename string, dbname string) {
	pageName = pagename
	dbName = dbname

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	headers = map[string][]string{}
	HTTP.HasAccessTo(accessCallback, dbName)
}
