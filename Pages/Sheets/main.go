//go:build js && wasm

package Sheets

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"errors"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
)

var (
	ForcePage = func(string) {}

	isBusy = false

	pageName = ""
	dbName   = ""

	headers       = map[string][]string{}
	selectedSheet = ""
	editingCol    = ""
	sheetData     = [][]string{}

	toDelete = []int{}
	toImport = [][]string{}
)

// TODO: Drag n Drop

func dbHeadersCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	headers = map[string][]string{}
	err := json.Unmarshal(resBytes, &headers)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
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
			"background":    "#2A2A2A",
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
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + nav + out + actions)

	els, err := DOM.GetElements("sheets_showdb_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
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
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elOut.InnerSet(HTML.HTML{Tag: "div",
			Styles: map[string]string{
				"display":       "flex",
				"padding":       "0px",
				"margin-bottom": "-2px",
				"background":    "#252525",
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
				"background":    "#2A2A2A",
				"border-radius": "0px",
				"font-size":     "100%",
				"font-weight":   "bold",
			},
			Inner: inps,
		}.String())

		els, err := DOM.GetElements("sheets_inputs_add")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		els.EventsAdd("keyup", submitNewRecord)

		selectedSheet = el.Get("innerHTML").String()
		HTTP.Send(dbReadCallback, dbName, "read", el.Get("innerHTML").String())
	})

	els, err = DOM.GetElements("sheets_action_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Disables()

	el, err := DOM.GetElement("sheets_deleteempty")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", actionDeleteEmpty)

	el, err = DOM.GetElement("sheets_export")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", actionExport)

	el, err = DOM.GetElement("sheets_import")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", actionImport)
}

func dbReadCallback(res string, resBytes []byte, resErr error) {
	if isBusy {
		return
	}
	isBusy = true

	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	sheetData = [][]string{}
	err := json.Unmarshal(resBytes, &sheetData)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	JS.ForEachCount(sheetData, 0, 5, func(count int, record []string, last bool) bool {
		err := addRow(record, count)
		if err != nil {
			isBusy = false
			return false
		}

		if last {
			isBusy = false
		}
		return true
	})

	els, err := DOM.GetElements("sheets_action_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Enables()
}

func addRow(record []string, recordIndex int) error {
	cols := ""
	for i, col := range record {
		borderRight := "2px dashed #151515"
		if i == len(record)-1 {
			borderRight = "0px solid #55f"
		}

		colHeader, ok := headers[selectedSheet]
		if !ok || i > len(colHeader)-1 {
			return errors.New("missing header for " + selectedSheet)
		}

		cols += HTML.HTML{Tag: "input",
			Attributes: map[string]string{"id": "sheets_inputs_edit_" + strconv.Itoa(recordIndex) + "_" + colHeader[i], "value": col},
			Styles: map[string]string{
				"width":           strconv.FormatFloat(100/float64(len(record)), 'f', -1, 64) + "%",
				"margin":          "0px",
				"padding":         "0px",
				"background":      "#2A2A2A",
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
			"background":    "#2A2A2A",
			"border":        "2px solid #151515",
			"border-radius": "0px",
			"font-size":     "100%",
		},
		Inner: cols,
	}.String()

	el, err := DOM.GetElement("sheets_out")
	if err != nil {
		return err
	}
	el.InnerAddSurfix(row)

	for i := range record {
		colHeader, ok := headers[selectedSheet]
		if !ok || i > len(colHeader)-1 {
			return errors.New("missing header for " + selectedSheet)
		}

		el, err := DOM.GetElement("sheets_inputs_edit_" + strconv.Itoa(recordIndex) + "_" + colHeader[i])
		if err != nil {
			return err
		}
		el.EventAdd("focusout", submitEditRecord)
	}

	return nil
}

func submitNewRecord(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
		return
	}
	if evs[0].Get("key").String() != "Enter" {
		return
	}

	els, err := DOM.GetElements("sheets_inputs_add")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	values := els.AttributesGet("value")
	els.AttributesSet("value", "")

	HTTP.Send(submitNewRecordCallback, dbName, append([]string{"add", selectedSheet}, values...)...)
}

func submitNewRecordCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	sheetData = [][]string{}
	err := json.Unmarshal(resBytes, &sheetData)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	err = addRow(sheetData[len(sheetData)-1], len(sheetData)-1)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
}

func submitEditRecord(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
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
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	colHeader, ok := headers[selectedSheet]
	if !ok {
		Widget.PopupAlert("Error", "missing header for "+selectedSheet, func() {})
	}

	keyIndex := slices.Index(colHeader, idSplit[len(idSplit)-1])
	if keyIndex < 0 {
		Widget.PopupAlert("Error", "missing key for "+idSplit[len(idSplit)-1], func() {})
	}

	if sheetData[index][keyIndex] == el.Get("value").String() {
		enableEditingCol(false, true)
		return
	}

	HTTP.Send(submitEditRecordCallback, dbName, "modify", selectedSheet, idSplit[len(idSplit)-2], idSplit[len(idSplit)-1], el.Get("value").String())
}

func submitEditRecordCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		enableEditingCol(false, false)
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	enableEditingCol(true, false)

	recordData := []string{}
	err := json.Unmarshal(resBytes, &recordData)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	idSplit := strings.Split(editingCol, "_")
	index, err := strconv.Atoi(idSplit[len(idSplit)-2])
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	sheetData[index] = recordData

	colHeader, ok := headers[selectedSheet]
	if !ok {
		Widget.PopupAlert("Error", "missing header for "+selectedSheet, func() {})
	}

	keyIndex := slices.Index(colHeader, idSplit[len(idSplit)-1])
	if keyIndex < 0 {
		Widget.PopupAlert("Error", "missing key for "+idSplit[len(idSplit)-1], func() {})
	}

	el, err := DOM.GetElement(editingCol)
	if err != nil {
		editingCol = ""
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.AttributeSet("value", sheetData[index][keyIndex])
}

func enableEditingCol(success bool, skipColor bool) {
	el, err := DOM.GetElement(editingCol)
	if err != nil {
		editingCol = ""
		Widget.PopupAlert("Error", err.Error(), func() {})
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
			el.StyleSet("background", "#2A2A2A")
		})
		return
	}

	el.StyleSet("background", "#208020")
	JS.AfterDelay(2000, func() {
		el.StyleSet("background", "#2A2A2A")
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

	if len(toDelete) <= 0 {
		return
	}

	HTTP.Send(deleteEmptyCallback, dbName, "delete", selectedSheet, strconv.Itoa(toDelete[0]))
	toDelete = toDelete[1:]
}

func deleteEmptyCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		els, err := DOM.GetElements("sheets_rows")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		els.Removes()

		JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })

		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if len(toDelete) > 0 {
		HTTP.Send(deleteEmptyCallback, dbName, "delete", selectedSheet, strconv.Itoa(toDelete[0]))
		toDelete = toDelete[1:]
		return
	}

	els, err := DOM.GetElements("sheets_rows")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Removes()

	JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })
}

func actionExport(el js.Value, evs []js.Value) {
	data, err := json.Marshal(&sheetData)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	Widget.Download(selectedSheet+".json", "text/json;charset=utf-8", data, func(err error) {})
}

func actionImport(el js.Value, evs []js.Value) {
	err := Widget.PopupFile("Import - "+pageName+" > "+selectedSheet, "testing", func(title string, data []byte) {
		if err := json.Unmarshal(data, &toImport); err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}

		if len(toImport) <= 0 {
			return
		}

		if len(toImport[0]) != len(headers[selectedSheet]) {
			Widget.PopupAlert("Error", "Invalid record: ["+strings.Join(toImport[0], ", ")+"]", func() {})
			toImport = toImport[1:]
			toImportCallback("", []byte{}, nil)
		} else {
			HTTP.Send(toImportCallback, dbName, append([]string{"add", selectedSheet}, toImport[0]...)...)
			toImport = toImport[1:]
		}
	})
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
	}
}

func toImportCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		els, err := DOM.GetElements("sheets_rows")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		els.Removes()

		JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })

		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	if len(toImport) > 0 {
		if len(toImport[0]) != len(headers[selectedSheet]) {
			Widget.PopupAlert("Error", "Invalid record: ["+strings.Join(toImport[0], ", ")+"]", func() {})
			toImport = toImport[1:]
			toImportCallback("", []byte{}, nil)
		} else {
			HTTP.Send(toImportCallback, dbName, append([]string{"add", selectedSheet}, toImport[0]...)...)
			toImport = toImport[1:]
		}
		return
	}

	els, err := DOM.GetElements("sheets_rows")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Removes()

	JS.Async(func() { HTTP.Send(dbReadCallback, dbName, "read", selectedSheet) })
}

func ShowSheet() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo(dbName, func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			HTTP.Send(dbHeadersCallback, dbName, "header")
		}
	})
}
