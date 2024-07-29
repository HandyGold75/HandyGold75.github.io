//go:build js && wasm

package Sheets

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
)

var (
	ForcePage               = func(string) {}
	SetLoginSuccessCallback = func(func()) {}

	isBusy = false

	pageName = ""
	dbName   = ""

	headers       = map[string][]string{}
	selectedSheet = ""
	editingCol    = ""
	sheetData     = [][]string{}

	toDelete = []int{}
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
			"margin":        "10px auto",
			"background":    "#202020",
			"border":        "2px solid #111",
			"border-radius": "10px",
		},
		Inner: btnSheets,
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sheets_out"},
		Styles: map[string]string{
			"width":       "90%",
			"margin":      "10px auto",
			"white-space": "pre",
			"font-family": "Hack",
		},
	}.String()

	btnSheets = HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	btnSheets += HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sheets_deleteempty", "class": "dark small sheets_action_buttons"},
		Inner:      "Delete Empty",
	}.String()
	btnSheets += HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sheets_export", "class": "dark small sheets_action_buttons"},
		Inner:      "export",
	}.String()
	btnSheets += HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sheets_import", "class": "dark small sheets_action_buttons"},
		Inner:      "import",
	}.String()
	btnSheets += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	actions := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sheets_actions"},
		Styles: map[string]string{"display": "flex",
			"width":  "90%",
			"margin": "10px auto",
		},
		Inner: btnSheets,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + nav + out + actions)

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
			borderRight := "2px dashed #151515"
			borderRightInput := "0px solid #55f"
			if i == len(header)-1 {
				borderRight = "0px"
				borderRightInput = ""
			}

			cols += HTML.HTML{Tag: "p",
				Styles: map[string]string{
					"width":           strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
					"border-right":    borderRight,
					"border-radius":   "0px",
					"scrollbar-width": "thin",
					"scrollbar-color": "transparent transparent",
					"overflow":        "scroll",
				},
				Inner: col,
			}.String()

			inps += HTML.HTML{Tag: "input",
				Attributes: map[string]string{"class": "sheets_inputs_add"},
				Styles: map[string]string{
					"width":         strconv.FormatFloat(100/float64(len(header)), 'f', -1, 64) + "%",
					"margin":        "0px",
					"padding":       "0px",
					"border-right":  borderRightInput,
					"border-radius": "0px",
					"text-align":    "center",
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
				"border-radius": "0px",
				"font-size":     "100%",
				"font-weight":   "bold",
			},
			Inner: inps,
		}.String())

		els, err := DOM.GetElements("sheets_inputs_add")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		els.EventsAdd("keyup", submitNewRecord)

		selectedSheet = el.Get("innerHTML").String()
		HTTP.Send(dbReadCallback, dbName, "read", el.Get("innerHTML").String())
	})

	els, err = DOM.GetElements("sheets_action_buttons")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.Disables()

	el, err := DOM.GetElement("sheets_deleteempty")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", actionDeleteEmpty)

	el, err = DOM.GetElement("sheets_export")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", actionExport)

	el, err = DOM.GetElement("sheets_import")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", actionImport)
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

	sheetData = [][]string{}
	err := json.Unmarshal(resBytes, &sheetData)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	for i, record := range sheetData {
		addRow(record, i, i*5)
	}
	JS.AfterDelay((len(sheetData)-1)*5, func() { isBusy = false })

	els, err := DOM.GetElements("sheets_action_buttons")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.Enables()
}

func addRow(record []string, recordIndex int, delay int) {
	el, err := DOM.GetElement("sheets_out")
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	cols := ""
	for i, col := range record {
		borderRight := "2px dashed #151515"
		if i == len(record)-1 {
			borderRight = "0px solid #55f"
		}

		colHeader, ok := headers[selectedSheet]
		if !ok || i > len(colHeader)-1 {
			JS.Alert("missing header for " + selectedSheet)
			break
		}

		cols += HTML.HTML{Tag: "input",
			Attributes: map[string]string{"id": "sheets_inputs_edit_" + strconv.Itoa(recordIndex) + "_" + colHeader[i], "value": col},
			Styles: map[string]string{
				"width":           strconv.FormatFloat(100/float64(len(record)), 'f', -1, 64) + "%",
				"margin":          "0px",
				"padding":         "0px",
				"background":      "#202020",
				"border-top":      "0px solid #55f",
				"border-right":    borderRight,
				"border-bottom":   "0px solid #55f",
				"border-left":     "0px solid #55f",
				"border-radius":   "0px",
				"text-align":      "center",
				"scrollbar-width": "thin",
				"scrollbar-color": "transparent transparent",
				"overflow":        "scroll",
				"transition":      "background 1s",
			},
		}.String()
	}

	row := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"class": "sheets_rows"},
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

	JS.AfterDelay(delay, func() {
		el.InnerAddSurfix(row)
		for i, _ := range record {
			colHeader, ok := headers[selectedSheet]
			if !ok || i > len(colHeader)-1 {
				JS.Alert("missing header for " + selectedSheet)
				break
			}

			el, err := DOM.GetElement("sheets_inputs_edit_" + strconv.Itoa(recordIndex) + "_" + colHeader[i])
			if err != nil {
				JS.Alert(err.Error())
				break
			}

			el.EventAdd("focusout", submitEditRecord)
		}
	})
	return
}

func submitNewRecord(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		JS.Alert("evs was not parsed")
		return
	}
	if evs[0].Get("key").String() != "Enter" {
		return
	}

	els, err := DOM.GetElements("sheets_inputs_add")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	values := els.AttributesGet("value")
	els.AttributesSet("value", "")

	HTTP.Send(submitNewRecordCallback, dbName, append([]string{"add", selectedSheet}, values...)...)
}

func submitNewRecordCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	sheetData = [][]string{}
	err := json.Unmarshal(resBytes, &sheetData)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	addRow(sheetData[len(sheetData)-1], len(sheetData)-1, 0)
}

func submitEditRecord(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		JS.Alert("evs was not parsed")
		return
	}
	if editingCol != "" {
		return
	}

	el.Set("disabled", true)

	editingCol = el.Get("id").String()
	idSplit := strings.Split(editingCol, "_")
	index, err := strconv.Atoi(idSplit[len(idSplit)-2])
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	colHeader, ok := headers[selectedSheet]
	if !ok {
		JS.Alert("missing header for " + selectedSheet)
	}

	keyIndex := slices.Index(colHeader, idSplit[len(idSplit)-1])
	if keyIndex < 0 {
		JS.Alert("missing key for " + idSplit[len(idSplit)-1])
	}

	if sheetData[index][keyIndex] == el.Get("value").String() {
		enableEditingCol(false, true)
		return
	}

	HTTP.Send(submitEditRecordCallback, dbName, "modify", selectedSheet, idSplit[len(idSplit)-2], idSplit[len(idSplit)-1], el.Get("value").String())
}

func submitEditRecordCallback(res string, resBytes []byte, resErr error) {
	defer enableEditingCol(resErr == nil, false)
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	}

	recordData := []string{}
	err := json.Unmarshal(resBytes, &recordData)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	idSplit := strings.Split(editingCol, "_")
	index, err := strconv.Atoi(idSplit[len(idSplit)-2])
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	sheetData[index] = recordData

	colHeader, ok := headers[selectedSheet]
	if !ok {
		JS.Alert("missing header for " + selectedSheet)
	}

	keyIndex := slices.Index(colHeader, idSplit[len(idSplit)-1])
	if keyIndex < 0 {
		JS.Alert("missing key for " + idSplit[len(idSplit)-1])
	}

	el, err := DOM.GetElement(editingCol)
	if err != nil {
		editingCol = ""
		JS.Alert(err.Error())
		return
	}
	el.AttributeSet("value", sheetData[index][keyIndex])
}

func enableEditingCol(success bool, skipColor bool) {
	el, err := DOM.GetElement(editingCol)
	if err != nil {
		editingCol = ""
		JS.Alert(err.Error())
		return
	}

	editingCol = ""
	el.Enable()

	if skipColor {
		return
	}

	if !success {
		el.StyleSet("background", "#802020")
		JS.AfterDelay(2000, func() {
			el.StyleSet("background", "#202020")
		})
		return
	}

	el.StyleSet("background", "#208020")
	JS.AfterDelay(2000, func() {
		el.StyleSet("background", "#202020")
	})
}

func actionDeleteEmpty(el js.Value, evs []js.Value) {
	if len(toDelete) > 0 {
		return
	}

	slices.Reverse(sheetData)
	for i, record := range sheetData {
		isEmpty := true
		for _, value := range record {
			if value != "" {
				isEmpty = false
				break
			}
		}

		if isEmpty {
			toDelete = append(toDelete, len(sheetData)-i-1)
		}
	}

	if len(toDelete) > 0 {
		HTTP.Send(deleteEmptyCallback, dbName, "delete", selectedSheet, strconv.Itoa(toDelete[0]))
		toDelete = toDelete[1:]
	}
}

func deleteEmptyCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Sheets:" + pageName) }) })
		return
	} else if resErr != nil {
		els, err := DOM.GetElements("sheets_rows")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		els.Removes()

		JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })

		JS.Alert(resErr.Error())
		return
	}

	if len(toDelete) > 0 {
		HTTP.Send(deleteEmptyCallback, dbName, "delete", selectedSheet, strconv.Itoa(toDelete[0]))
		toDelete = toDelete[1:]
		return
	}

	els, err := DOM.GetElements("sheets_rows")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.Removes()

	JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })
}

func actionExport(el js.Value, evs []js.Value) {
	data, err := json.Marshal(&sheetData)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	JS.Download(selectedSheet+".json", data)
}

func actionImport(el js.Value, evs []js.Value) {
	// TODO
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
	selectedSheet = ""

	HTTP.HasAccessTo(accessCallback, dbName)
}
