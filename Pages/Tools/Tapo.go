//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"errors"
	"fmt"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

type (
	DeviceEnergy struct {
		TodayRuntime      int    `json:"today_runtime"`
		MonthRuntime      int    `json:"month_runtime"`
		TodayEnergy       int    `json:"today_energy"`
		MonthEnergy       int    `json:"month_energy"`
		LocalTime         string `json:"local_time"`
		ElectricityCharge []int  `json:"electricity_charge"`
		CurrentPower      int    `json:"current_power"`
	}
)

var (
	availableHists = map[string][]string{}

	selectedDevice     = ""
	selectedYear       = ""
	skipBtnUpdateCount = 0
)

func togglePower(el js.Value, evs []js.Value) {
	if selectedDevice != "" {
		return
	}

	name := strings.Split(el.Get("id").String(), "_")[2]

	elBtn, err := DOM.GetElement(el.Get("id").String())
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	value := !strings.Contains(elBtn.AttributeGet("className"), "imgBtnBorder")

	if value {
		selectedDevice = name
		HTTP.Send(togglePowerCallback, "tapo", "on", name)
		return
	}

	Widget.PopupConfirm("Tapo", "Power off <b>"+name+"<\\b>?", "No", "Yes", func(accepted bool) {
		if accepted {
			selectedDevice = name
			HTTP.Send(togglePowerCallback, "tapo", "off", name)
		}
	})
}

func togglePowerCallback(res string, resBytes []byte, resErr error) {
	if selectedDevice == "" {
		return
	}
	defer func() { selectedDevice = "" }()

	el, err := DOM.GetElement("tapo_devices_" + selectedDevice + "_power")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	skipBtnUpdateCount = 5

	if res == "false" {
		el.AttributeSet("className", "imgBtn imgBtnMedium")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnMedium imgBtnBorder")
	}
}

func showInfoList(el js.Value, evs []js.Value) {
	if selectedDevice != "" {
		return
	}

	selectedDevice = strings.Split(el.Get("id").String(), "_")[2]

	selectedYear = ""
	HTTP.Send(showInfoListCallback, "tapo", "histlist")
}

func showInfoListCallback(res string, resBytes []byte, resErr error) {
	if selectedDevice == "" {
		return
	}
	defer func() { selectedDevice = "" }()

	els, err := DOM.GetElements("tapo_devices_infos")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.AttributesSet("className", "imgBtn imgBtnMedium tapo_devices_infos")

	el, err := DOM.GetElement("tapo_devices_" + selectedDevice + "_info")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.AttributeSet("className", "imgBtn imgBtnMedium imgBtnBorder tapo_devices_infos")

	availableHists = map[string][]string{}
	err = json.Unmarshal(resBytes, &availableHists)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	hists, ok := availableHists[selectedDevice]
	if !ok {
		Widget.PopupAlert("Error", "history \""+selectedDevice+"\" not available!", func() {})
		return
	}

	elDates, err := DOM.GetElement("tapo_history_dates")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elOut, err := DOM.GetElement("tapo_history_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	delay := 0
	if elDates.StyleGet("max-height") != "0px" {
		elDates.StyleSet("max-height", "0px")
		delay = 250
	}
	if elOut.StyleGet("max-height") != "0px" {
		elOut.StyleSet("max-height", "0px")
		delay = 250
	}

	selected := selectedDevice
	JS.AfterDelay(delay, func() {
		showInfoDates(selected)
		selectedYear = strings.Split(hists[len(hists)-1], ".")[0]
		HTTP.Send(showInfoCallback, "tapo", "histget", selected, hists[len(hists)-1])
	})
}

func showInfoDates(selected string) {
	hists, ok := availableHists[selected]
	if !ok {
		Widget.PopupAlert("Error", "history \""+selected+"\" not available!", func() {})
		return
	}

	histDates := HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()
	for _, v := range hists {
		histDates += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark small tapo_history_dates_btns"},
			Inner:      v,
		}.String()
	}
	histDates += HTML.HTML{Tag: "p", Styles: map[string]string{"margin": "auto"}}.String()

	elDates, err := DOM.GetElement("tapo_history_dates")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDates.InnerSet(histDates)
	elDates.StyleSet("max-height", "40px")

	els, err := DOM.GetElements("tapo_history_dates_btns")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.StylesSet("min-width", strconv.Itoa(min(5, 100/len(availableHists)))+"%")
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		selectedYear = strings.Split(el.Get("innerHTML").String(), ".")[0]
		HTTP.Send(showInfoCallback, "tapo", "histget", selected, el.Get("innerHTML").String())
	})
}

func showInfoCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	hist := []string{}
	err := json.Unmarshal(resBytes, &hist)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	elOut, err := DOM.GetElement("tapo_history_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if elOut.StyleGet("max-height") != "0px" {
		elOut.StyleSet("max-height", "0px")
	}

	lines := strings.Split(strings.Join(hist, ""), "<EOR>\n")
	slices.Reverse(lines)

	JS.AfterDelay(250, func() {
		JS.OnResizeDelete("Tapo")
		JS.OnResizeAdd("Tapo", func() { showGraph(lines) })
	})
}

func parseHistLine(line string) (time.Time, float64, float64, error) {
	l := strings.Split(line, "<SEP>")
	if len(l) != 4 {
		return time.Time{}, 0.0, 0.0, errors.New("unable to parse, line has invalid size")
	}
	localTime, err := time.Parse(time.RFC3339Nano, l[0])
	if err != nil {
		return time.Time{}, 0.0, 0.0, errors.New("unable to parse local time")
	}
	if l[1] != "info" {
		return time.Time{}, 0.0, 0.0, errors.New("unable to parse, line has invalid state")
	}
	todayRuntime, err := strconv.ParseFloat(l[2], 64)
	if err != nil {
		return time.Time{}, 0.0, 0.0, errors.New("unable to parse today runtime")
	}
	todayEnergy, err := strconv.ParseFloat(l[3], 64)
	if err != nil {
		return time.Time{}, 0.0, 0.0, errors.New("unable to parse today energy")
	}
	return localTime, todayRuntime, todayEnergy, nil
}

func drawSvg(lines []string, maxValue float64, xFunc func(time.Time) float64, circFunc func(time.Time) bool) error {
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		return err
	}

	c_width := float64(elSvg.El.Get("clientWidth").Int())
	c_height := float64(elSvg.El.Get("clientHeight").Int())

	svg := ""
	allCordsRuntime := []string{}
	allCordsEnergy := []string{}
	tooltips := map[string][2]string{}
	for _, line := range lines {
		localTime, todayRuntime, todayEnergy, err := parseHistLine(line)
		if err != nil {
			continue
		}

		runtimeY := c_height
		if todayRuntime != 0 {
			runtimeY = c_height - ((todayRuntime / 1440) * c_height)
		}
		energyY := c_height
		if todayEnergy != 0 {
			energyY = c_height - ((todayEnergy / maxValue) * c_height)
		}

		cordX := c_width * xFunc(localTime)

		cordsRuntime := [2]string{strconv.FormatFloat(cordX, 'f', -1, 64), strconv.FormatFloat(runtimeY, 'f', -1, 64)}
		cordsEnergy := [2]string{strconv.FormatFloat(cordX, 'f', -1, 64), strconv.FormatFloat(energyY, 'f', -1, 64)}

		allCordsRuntime = append(allCordsRuntime, cordsRuntime[0]+","+cordsRuntime[1])
		allCordsEnergy = append(allCordsEnergy, cordsEnergy[0]+","+cordsEnergy[1])

		if !circFunc(localTime) {
			continue
		}

		tooltips["tapo_history_out_svg_runtime_"+cordsRuntime[0]+"_"+cordsRuntime[1]] = [2]string{"Runtime", SectoString(int(todayRuntime)) + "<br>" + localTime.Format(time.DateTime)}
		tooltips["tapo_history_out_svg_energy_"+cordsEnergy[0]+"_"+cordsEnergy[1]] = [2]string{"Energy", WattToString(todayEnergy) + "<br>" + localTime.Format(time.DateTime)}

		svg += HTML.HTML{Tag: "circle",
			Attributes: map[string]string{
				"id": "tapo_history_out_svg_runtime_" + cordsRuntime[0] + "_" + cordsRuntime[1],
				"r":  "10", "cx": cordsRuntime[0], "cy": cordsRuntime[1],
				"fill": "#55F", "stroke": "#2A2A2A", "stroke-width": "5",
			},
		}.String()
		svg += HTML.HTML{Tag: "circle",
			Attributes: map[string]string{
				"id": "tapo_history_out_svg_energy_" + cordsEnergy[0] + "_" + cordsEnergy[1],
				"r":  "10", "cx": cordsEnergy[0], "cy": cordsEnergy[1],
				"fill": "#FFAA55", "stroke": "#2A2A2A", "stroke-width": "5",
			},
		}.String()
	}

	runtimeLine := HTML.HTML{Tag: "polyline",
		Attributes: map[string]string{"points": strings.Join(allCordsRuntime, " ")},
		Styles:     map[string]string{"fill": "none", "stroke": "#55F", "stroke-width": "10"},
	}.String()
	energyLine := HTML.HTML{Tag: "polyline",
		Attributes: map[string]string{"points": strings.Join(allCordsEnergy, " ")},
		Styles:     map[string]string{"fill": "none", "stroke": "#FFAA55", "stroke-width": "5"},
	}.String()

	elSvg.InnerAddSurfixRaw(runtimeLine + energyLine + svg)

	for id, txt := range tooltips {
		Widget.Tooltip(id, txt[0], txt[1], 250)
	}

	return nil
}

func drawRows(maxValue float64) error {
	elRows, err := DOM.GetElement("tapo_history_out_rows")
	if err != nil {
		return err
	}
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		return err
	}

	c_width := float64(elSvg.El.Get("clientWidth").Int())
	c_height := float64(elSvg.El.Get("clientHeight").Int())

	rows := ""
	svg := ""
	for i := 10.0; i > 0; i-- {
		rows += HTML.HTML{Tag: "p", Inner: WattToString((i / 10) * maxValue),
			Styles: map[string]string{
				"height":        "10%",
				"margin-top":    "-2px",
				"border-top":    "2px solid #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()

		y := strconv.FormatFloat(c_height-((i/10.0)*c_height), 'f', -1, 64)
		svg += HTML.HTML{Tag: "line",
			Attributes: map[string]string{"x1": "0", "y1": y, "x2": strconv.FormatFloat(c_width, 'f', -1, 64), "y2": y},
			Styles:     map[string]string{"stroke": "#222", "stroke-width": "2"},
		}.String()
	}

	elRows.InnerSet(rows)
	elSvg.InnerAddPrefix(svg)

	elCor, err := DOM.GetElement("tapo_history_out_cor")
	if err != nil {
		return err
	}
	elCor.InnerSet(HTML.HTML{Tag: "p", Inner: WattToString(0), Styles: map[string]string{"height": "100%", "white-space": "nowrap"}}.String())

	return nil
}

func drawCols(lines []string) error {
	elCols, err := DOM.GetElement("tapo_history_out_cols")
	if err != nil {
		return err
	}
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		return err
	}

	c_width := float64(elSvg.El.Get("clientWidth").Int())
	c_height := float64(elSvg.El.Get("clientHeight").Int())

	months := []string{"January", "Febuary", "March", "April", "May", "June", "Juli", "August", "September", "October", "November", "December"}

	cols := ""
	svg := ""
	for i, month := range months {
		cols += HTML.HTML{Tag: "p", Inner: month,
			Attributes: map[string]string{"id": "tapo_history_out_cols_month_" + strconv.Itoa(i)},
			Styles: map[string]string{
				"width":         strconv.FormatFloat(100.0/float64(len(months)), 'f', -1, 64) + "%",
				"margin-left":   "-2px",
				"border-left":   "2px solid #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()

		x := strconv.FormatFloat((float64(i)/float64(len(months)))*c_width, 'f', -1, 64)
		svg += HTML.HTML{Tag: "line",
			Attributes: map[string]string{"x1": x, "y1": "0", "x2": x, "y2": strconv.FormatFloat(c_height, 'f', -1, 64)},
			Styles:     map[string]string{"stroke": "#222", "stroke-width": "2"},
		}.String()
	}
	elCols.InnerSet(cols)
	elSvg.InnerAddPrefix(svg)

	for i := range months {
		el, err := DOM.GetElement("tapo_history_out_cols_month_" + strconv.Itoa(i))
		if err != nil {
			return err
		}
		el.EventAdd("dblclick", func(el js.Value, els []js.Value) {
			idSplit := strings.Split(el.Get("id").String(), "_")
			m, err := strconv.Atoi(idSplit[len(idSplit)-1])
			if err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
				return
			}

			date, err := time.Parse(time.DateOnly, selectedYear+"-"+fmt.Sprintf("%02d", m+1)+"-01")
			if err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
				return
			}

			JS.OnResizeDelete("Tapo")
			JS.OnResizeAdd("Tapo", func() { showGraphMonth(lines, date) })
		})
	}

	return nil
}

func drawColsMonth(maxDays int) error {
	elCols, err := DOM.GetElement("tapo_history_out_cols")
	if err != nil {
		return err
	}
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		return err
	}

	c_width := float64(elSvg.El.Get("clientWidth").Int())
	c_height := float64(elSvg.El.Get("clientHeight").Int())

	cols := ""
	svg := ""
	for i := 1; i <= maxDays; i++ {
		cols += HTML.HTML{Tag: "p", Inner: strconv.Itoa(i),
			Styles: map[string]string{
				"width":         strconv.FormatFloat(100.0/float64(maxDays), 'f', -1, 64) + "%",
				"margin-left":   "-2px",
				"border-left":   "2px solid #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()

		x := strconv.FormatFloat((float64(i)/float64(maxDays))*c_width, 'f', -1, 64)
		svg += HTML.HTML{Tag: "line",
			Attributes: map[string]string{"x1": x, "y1": "0", "x2": x, "y2": strconv.FormatFloat(c_height, 'f', -1, 64)},
			Styles:     map[string]string{"stroke": "#222", "stroke-width": "2"},
		}.String()
	}
	elCols.InnerSet(cols)
	elSvg.InnerAddPrefix(svg)

	return nil
}

func showGraph(lines []string) {
	elOut, err := DOM.GetElement("tapo_history_out")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		return
	}
	elOut.StyleSet("max-height", "750px")

	maxValue := 0.0
	for _, line := range lines {
		_, todayRuntime, todayEnergy, err := parseHistLine(line)
		if err != nil {
			continue
		}

		if todayRuntime > maxValue {
			maxValue = todayRuntime
		}
		if todayEnergy > maxValue {
			maxValue = todayEnergy
		}
	}
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSvg.InnerSet("")

	xFunc := func(lt time.Time) float64 {
		yearWeigth := (100.0 / 12.0) / 100.0
		monthWeigth := (100 / float64(lt.AddDate(0, 1, -lt.Day()).Day())) / 100
		return (float64(lt.Day()-1) * monthWeigth * yearWeigth) + (float64(lt.Month()-1) * yearWeigth)
	}
	circFunc := func(lt time.Time) bool {
		if lt.Day() == 1 {
			return true
		}
		if lt.Day() == lt.AddDate(0, 1, -lt.Day()).Day() {
			return true
		}
		if lt.Day() == lt.AddDate(0, 1, -lt.Day()).Day()/2 {
			return true
		}
		return false
	}

	if err := drawRows(maxValue); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := drawCols(lines); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := drawSvg(lines, maxValue, xFunc, circFunc); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
}

func showGraphMonth(lines []string, selectedMonth time.Time) {
	elOut, err := DOM.GetElement("tapo_history_out")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		return
	}
	elOut.StyleSet("max-height", "750px")

	lines = slices.DeleteFunc(lines, func(l string) bool {
		localTime, _, _, err := parseHistLine(l)
		if err != nil {
			return true
		}
		return localTime.Month() != selectedMonth.Month()
	})

	maxValue := 0.0
	for _, line := range lines {
		_, todayRuntime, todayEnergy, err := parseHistLine(line)
		if err != nil {
			continue
		}

		if todayRuntime > maxValue {
			maxValue = todayRuntime
		}
		if todayEnergy > maxValue {
			maxValue = todayEnergy
		}
	}
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSvg.InnerSet("")

	xFunc := func(lt time.Time) float64 {
		monthWeigth := (100 / float64(lt.AddDate(0, 1, -lt.Day()).Day())) / 100
		return (float64(lt.Day()) - 0.5) * monthWeigth
	}
	circFunc := func(lt time.Time) bool {
		return true
	}

	if err := drawRows(maxValue); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := drawColsMonth(selectedMonth.AddDate(0, 1, -selectedMonth.Day()).Day()); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := drawSvg(lines, maxValue, xFunc, circFunc); err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
}

func addDevice(name string) error {
	headStyle := map[string]string{"font-size": "125%", "font-weight": "bold", "white-space": "nowrap"}
	txtStyle := map[string]string{"margin": "0px auto 0px 0px", "white-space": "nowrap"}
	outStyle := map[string]string{"margin": "0px 5px", "white-space": "nowrap"}
	divStyle := map[string]string{"display": "flex", "padding": "0px", "background": "#2F2F2F"}

	btnPower := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_power", "class": "imgBtn imgBtnMedium"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Tapo/Power.svg", "alt": "power"},
		}.String(),
	}.String()

	txt := HTML.HTML{Tag: "h2", Inner: name,
		Styles: map[string]string{"margin": "auto 10px", "padding": "0px 10px", "white-space": "nowrap"},
	}.String()

	btnInfo := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_info", "class": "imgBtn imgBtnMedium tapo_devices_infos"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Tapo/Info.svg", "alt": "info"},
		}.String(),
	}.String()

	header := HTML.HTML{Tag: "div", Inner: btnPower + txt + btnInfo,
		Styles: map[string]string{"display": "flex"},
	}.String()

	power := HTML.HTML{Tag: "img",
		Styles:     map[string]string{"width": "100%"},
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_current_power_img", "src": "./docs/assets/Tapo/Power/0.svg", "alt": "info"},
	}.String()

	out := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_current_power"},
		Styles:     map[string]string{"margin": "-15px 5px 0px 5px", "white-space": "nowrap"},
	}.String()

	current := HTML.HTML{Tag: "div", Inner: power + out,
		Styles: map[string]string{
			"width":      "150px",
			"margin":     "10px auto",
			"padding":    "0px 4px",
			"background": "#2F2F2F",
			"border":     "2px solid #191919",
		},
	}.String()

	head := HTML.HTML{Tag: "p", Inner: "Today", Styles: headStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Power", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_today_power"}, Styles: outStyle}.String()
	power = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Runtime", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_today_runtime"}, Styles: outStyle}.String()
	runtime := HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	today := HTML.HTML{Tag: "div", Inner: head + power + runtime,
		Styles: map[string]string{
			"width":      "50%",
			"background": "#2F2F2F",
		},
	}.String()

	head = HTML.HTML{Tag: "p", Inner: "Month", Styles: headStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Power", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_month_power"}, Styles: outStyle}.String()
	power = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Runtime", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_month_runtime"}, Styles: outStyle}.String()
	runtime = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	month := HTML.HTML{Tag: "div", Inner: head + power + runtime,
		Styles: map[string]string{
			"width":      "50%",
			"background": "#2F2F2F",
		},
	}.String()

	stats := HTML.HTML{Tag: "div", Inner: today + month,
		Styles: map[string]string{
			"display":    "flex",
			"padding":    "0px 4px",
			"background": "#2F2F2F",
			"border":     "2px solid #191919",
		},
	}.String()

	div := HTML.HTML{Tag: "div", Inner: header + current + stats,
		Attributes: map[string]string{"id": "tapo_devices_" + name},
		Styles: map[string]string{
			"min-width":  "max-content",
			"background": "#2A2A2A",
			"border":     "4px solid #202020",
		},
	}.String()

	el, err := DOM.GetElement("tapo_monitors")
	if err != nil {
		return err
	}
	el.InnerAddPrefix(div)

	el, err = DOM.GetElement("tapo_devices_" + name + "_power")
	if err != nil {
		return err
	}
	el.EventAdd("click", togglePower)

	el, err = DOM.GetElement("tapo_devices_" + name + "_info")
	if err != nil {
		return err
	}
	el.EventAdd("click", showInfoList)

	return updateDevice(name, DeviceEnergy{})
}

func updateDevice(name string, specs DeviceEnergy) error {
	if skipBtnUpdateCount == 0 {
		el, err := DOM.GetElement("tapo_devices_" + name + "_power")
		if err != nil {
			return err
		}
		if specs.CurrentPower == 0 {
			el.AttributeSet("className", "imgBtn imgBtnMedium")
		} else {
			el.AttributeSet("className", "imgBtn imgBtnMedium imgBtnBorder")
		}
	} else {
		skipBtnUpdateCount -= 1
	}

	el, err := DOM.GetElement("tapo_devices_" + name + "_current_power_img")
	if err != nil {
		return err
	}
	if specs.CurrentPower == 0 {
		el.AttributeSet("src", "./docs/assets/Tapo/Power/0.svg")
	} else {
		el.AttributeSet("src", "./docs/assets/Tapo/Power/"+strconv.FormatFloat(min(9, max(0, float64(specs.CurrentPower)/1000/100)), 'f', 0, 64)+".svg")
	}

	el, err = DOM.GetElement("tapo_devices_" + name + "_current_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(float64(specs.CurrentPower) / 1000))

	el, err = DOM.GetElement("tapo_devices_" + name + "_today_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(float64(specs.TodayEnergy)))

	el, err = DOM.GetElement("tapo_devices_" + name + "_today_runtime")
	if err != nil {
		return err
	}
	el.InnerSet(SectoString(specs.TodayRuntime))

	el, err = DOM.GetElement("tapo_devices_" + name + "_month_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(float64(specs.MonthEnergy)))

	el, err = DOM.GetElement("tapo_devices_" + name + "_month_runtime")
	if err != nil {
		return err
	}
	el.InnerSet(SectoString(specs.MonthRuntime))

	return nil
}

func syncCallbackTapo(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	resp := map[string]DeviceEnergy{}
	if err := json.Unmarshal(resBytes, &resp); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	for name, spec := range resp {
		if _, err := DOM.GetElement("tapo_devices_" + name); err != nil {
			if err := addDevice(name); err != nil {
				return
			}
			continue
		}

		if err := updateDevice(name, spec); err != nil {
			return
		}
	}

	JS.AfterDelay(2000, func() { HTTP.Send(syncCallbackTapo, "tapo", "sync") })
}

func WattToString(w float64) string {
	if w > 1000000000 {
		return fmt.Sprintf("%0.1f", w/1000000000) + " Gw"
	} else if w > 1000000 {
		return fmt.Sprintf("%0.1f", w/1000000) + " Mw"
	} else if w > 1000 {
		return fmt.Sprintf("%0.1f", w/1000) + " Kw"
	}
	return strconv.FormatFloat(w, 'f', 0, 64) + " w"
}

func SectoString(m int) string {
	if m > 525600 {
		return fmt.Sprintf("%0.1f", float64(m)/525600) + " Y"
	} else if m > 10080 {
		return fmt.Sprintf("%0.1f", float64(m)/10080) + " W"
	} else if m > 43800 {
		return fmt.Sprintf("%0.1f", float64(m)/43800) + " M"
	} else if m > 1440 {
		return fmt.Sprintf("%0.1f", float64(m)/1440) + " D"
	} else if m > 60 {
		return fmt.Sprintf("%0.1f", float64(m)/60) + " h"
	}
	return strconv.Itoa(m) + " m"
}

func showTapo() {
	header := HTML.HTML{Tag: "h1", Inner: "Tapo"}.String()

	monitors := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_monitors"},
		Styles:     map[string]string{"display": "flex", "overflow-x": "scroll"},
	}.String()

	dates := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_history_dates"},
		Styles: map[string]string{
			"display":    "flex",
			"width":      "90%",
			"max-height": "0px",
			"margin":     "10px auto",
			"background": "#202020",
			"border":     "2px solid #111",
			"transition": "max-height 0.25s",
		},
	}.String()

	rows := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_history_out_rows"},
		Styles: map[string]string{
			"width":         "71px",
			"height":        "700px",
			"margin":        "0px",
			"padding":       "0px",
			"border-right":  "4px solid #111",
			"border-radius": "0px",
		},
	}.String()
	cor := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_history_out_cor"},
		Styles: map[string]string{
			"width":         "71px",
			"height":        "38px",
			"margin":        "0px",
			"padding":       "0px",
			"border-top":    "2px solid #111",
			"border-right":  "4px solid #111",
			"border-radius": "0px",
		},
	}.String()
	cols := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_history_out_cols"},
		Styles: map[string]string{
			"display":       "flex",
			"width":         "100%",
			"height":        "36px",
			"margin":        "0px",
			"padding":       "0px",
			"border-top":    "4px solid #111",
			"border-radius": "0px",
		},
	}.String()

	svg := HTML.HTML{Tag: "svg",
		Attributes: map[string]string{"id": "tapo_history_out_svg", "xmlns": "http://www.w3.org/2000/svg"},
		Styles: map[string]string{
			"width":  "100%",
			"height": "700px",
		},
	}.String()

	out := HTML.HTML{Tag: "div", Inner: rows + svg + cor + cols,
		Attributes: map[string]string{"id": "tapo_history_out"},
		Styles: map[string]string{
			"display":               "grid",
			"justify-content":       "space-evenly",
			"grid-template-columns": "75px calc(100% - 75px)",
			"width":                 "95%",
			"max-height":            "0px",
			"padding":               "0px",
			"margin":                "10px auto",
			"background":            "#2A2A2A",
			"border":                "4px solid #f7e163",
			"border-radius":         "10px",
			"transition":            "max-height 0.25s",
		},
	}.String()

	hists := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_history"},
		Inner:      dates + out,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + monitors + hists)

	HTTP.Send(syncCallbackTapo, "tapo", "sync")
}

func PageTapo() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("tapo", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showTapo()
		}
	})
}
