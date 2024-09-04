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
	skipBtnUpdateCount = 0
)

func accessCallbackTapo(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Tapo") }) })
		return
	} else if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if !hasAccess {
		Widget.PopupAlert("Error", "unauthorized", func() {})
		return
	}

	HTTP.Send(syncCallbackTapo, "tapo", "sync")
}

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

	delay := 0
	if elDates.StyleGet("max-height") != "0px" {
		elDates.StyleSet("max-height", "0px")
		delay = 250
	}

	selected := selectedDevice
	JS.AfterDelay(delay, func() {
		showInfoDates(selected)
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
		HTTP.Send(showInfoCallback, "tapo", "histget", selected, el.Get("innerHTML").String())
	})
}

func showInfoCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		return
	} else if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	hist := []string{}
	err := json.Unmarshal(resBytes, &hist)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	elDates, err := DOM.GetElement("tapo_history_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDates.StyleSet("max-height", "750px")

	lines := strings.Split(strings.Join(hist, ""), "<EOR>\n")
	slices.Reverse(lines)

	JS.AfterDelay(300, func() {
		JS.OnResizeDelete("Tapo")
		JS.OnResizeAdd("Tapo", func() { drawSvg(lines) })
	})
}

func drawSvg(lines []string) {
	elSvg, err := DOM.GetElement("tapo_history_out_svg")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elRows, err := DOM.GetElement("tapo_history_out_rows")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elCor, err := DOM.GetElement("tapo_history_out_cor")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elCols, err := DOM.GetElement("tapo_history_out_cols")
	if err != nil {
		JS.OnResizeDelete("Tapo")
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	parseLine := func(line string) (time.Time, float64, float64, error) {
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

	c_width := float64(elSvg.El.Get("clientWidth").Int())
	c_height := float64(elSvg.El.Get("clientHeight").Int())

	maxValue := 0.0
	linesLen := 0.0
	for _, line := range lines {
		_, todayRuntime, todayEnergy, err := parseLine(line)
		if err != nil {
			continue
		}

		if todayRuntime > maxValue {
			maxValue = todayRuntime
		}
		if todayEnergy > maxValue {
			maxValue = todayEnergy
		}

		linesLen++
	}

	rows := ""
	for i := 10.0; i > 0; i-- {
		rows += HTML.HTML{Tag: "p", Inner: SectoString(int((i / 10) * maxValue)),
			Styles: map[string]string{
				"height":        "5%",
				"margin-bottom": "-2px",
				"border-bottom": "2px dotted #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()
		rows += HTML.HTML{Tag: "p", Inner: WattToString((i / 10) * maxValue),
			Styles: map[string]string{
				"height":        "5%",
				"margin-bottom": "-2px",
				"border-bottom": "2px solid #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()
	}
	elRows.InnerSet(rows)

	elCor.InnerSet(HTML.HTML{Tag: "p", Inner: "0", Styles: map[string]string{"height": "100%", "white-space": "nowrap"}}.String())

	cols := ""
	for _, month := range []string{"January", "Febuary", "March", "April", "May", "June", "Juli", "August", "September", "October", "November", "December"} {
		cols += HTML.HTML{Tag: "p", Inner: month,
			Styles: map[string]string{
				"width":         "10%",
				"margin-left":   "-2px",
				"border-left":   "2px solid #111",
				"border-radius": "0px",
				"white-space":   "nowrap",
			},
		}.String()
	}
	elCols.InnerSet(cols)

	svgHtml := ""
	allCordsRuntime := []string{}
	allCordsEnergy := []string{}
	tooltips := map[string][2]string{}

	i := 0
	for _, line := range lines {
		localTime, todayRuntime, todayEnergy, err := parseLine(line)
		if err != nil {
			continue
		}

		runtimeY := 0.0
		if todayRuntime != 0 {
			runtimeY = c_height - ((todayRuntime / maxValue) * c_height)
		}
		energyY := 0.0
		if todayEnergy != 0 {
			energyY = c_height - ((todayEnergy / maxValue) * c_height)
		}

		// fmt.Println("---")
		// fmt.Println(localTime.Format(time.DateTime))
		// fmt.Println(float64(localTime.Month() - 1))
		// fmt.Println((float64(localTime.Month()-1) * (100.0 / 12.0) / 100.0))
		// fmt.Println(c_width * (float64(localTime.Month()-1) * (100.0 / 12.0) / 100.0))
		// fmt.Println(float64(localTime.AddDate(0, 1, -localTime.Day()).Day()))
		// fmt.Println((((100.0 / float64(localTime.AddDate(0, 1, -localTime.Day()).Day())) / (100.0 / 12.0)) / 100.0))
		// fmt.Println(c_width * (((100.0 / float64(localTime.AddDate(0, 1, -localTime.Day()).Day())) / (100.0 / 12.0)) / 100.0))

		// cordX := c_width * (float64(localTime.Month()-1) * (100.0 / 12.0) / 100.0)
		// cordX += c_width * (((100.0 / float64(localTime.AddDate(0, 1, -localTime.Day()).Day())) / (100.0 / 12.0)) / 100.0)

		// cordX := (c_width * (float64(localTime.Month()-1) * (100.0 / 12.0) / 100.0)) + (c_width * (((100.0 / float64(localTime.AddDate(0, 1, -localTime.Day()).Day())) / (100.0 / 12.0)) / 100.0))

		cordX := (float64(i) / (linesLen - 1)) * c_width

		cordsRuntime := [2]string{strconv.FormatFloat(min(c_width, max(0, cordX)), 'f', -1, 64), strconv.FormatFloat(min(c_height, max(0, runtimeY)), 'f', -1, 64)}
		cordsEnergy := [2]string{strconv.FormatFloat(min(c_width, max(0, cordX)), 'f', -1, 64), strconv.FormatFloat(min(c_height, max(0, energyY)), 'f', -1, 64)}

		allCordsRuntime = append(allCordsRuntime, cordsRuntime[0]+","+cordsRuntime[1])
		allCordsEnergy = append(allCordsEnergy, cordsEnergy[0]+","+cordsEnergy[1])

		tooltips["tapo_history_out_svg_"+cordsRuntime[0]+"_"+cordsRuntime[1]] = [2]string{"Runtime", SectoString(int(todayRuntime)) + "<br>" + localTime.Format(time.DateTime)}
		tooltips["tapo_history_out_svg_"+cordsEnergy[0]+"_"+cordsEnergy[1]] = [2]string{"Energy", WattToString(todayEnergy) + "<br>" + localTime.Format(time.DateTime)}

		svgHtml += HTML.HTML{Tag: "circle",
			Attributes: map[string]string{
				"id": "tapo_history_out_svg_" + cordsRuntime[0] + "_" + cordsRuntime[1],
				"r":  "10", "cx": cordsRuntime[0], "cy": cordsRuntime[1],
				"fill": "#55F", "stroke": "#2A2A2A", "stroke-width": "5",
			},
		}.String()
		svgHtml += HTML.HTML{Tag: "circle",
			Attributes: map[string]string{
				"id": "tapo_history_out_svg_" + cordsEnergy[0] + "_" + cordsEnergy[1],
				"r":  "10", "cx": cordsEnergy[0], "cy": cordsEnergy[1],
				"fill": "#FFAA55", "stroke": "#2A2A2A", "stroke-width": "5",
			},
		}.String()

		i++
	}

	runtimeLine := HTML.HTML{Tag: "polyline",
		Attributes: map[string]string{"points": strings.Join(allCordsRuntime, " ")},
		Styles:     map[string]string{"fill": "none", "stroke": "#55F", "stroke-width": "10"},
	}.String()

	energyLine := HTML.HTML{Tag: "polyline",
		Attributes: map[string]string{"points": strings.Join(allCordsEnergy, " ")},
		Styles:     map[string]string{"fill": "none", "stroke": "#FFAA55", "stroke-width": "5"},
	}.String()

	elSvg.InnerSet(runtimeLine + energyLine + svgHtml)

	for id, txt := range tooltips {
		Widget.Tooltip(id, txt[0], txt[1], 250)
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
		Styles:     map[string]string{"margin": "-10px 5px 0px 5px", "white-space": "nowrap"},
	}.String()

	current := HTML.HTML{Tag: "div", Inner: power + out,
		Styles: map[string]string{
			"width":      "150px",
			"margin":     "10px auto",
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
	el.InnerAddSurfix(div)

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
		el.AttributeSet("src", "./docs/assets/Tapo/Power/"+strconv.FormatFloat(min(9, max(0, float64(specs.CurrentPower)/1000/75)), 'f', 0, 64)+".svg")
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
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Tapo") }) })
		return
	} else if resErr != nil {
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

func PageTapo(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Tapo") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

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
			"height":        "48px",
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
			"height":        "46px",
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

	HTTP.HasAccessTo(accessCallbackTapo, "tapo")
}
