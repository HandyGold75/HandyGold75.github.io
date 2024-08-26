//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"syscall/js"
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
	selectedDevice     = ""
	skipBtnUpdateCount = 0
)

func accessCallbackTapo(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Tapo") }) })
		return
	} else if err != nil {
		JS.Alert(err.Error())
		return
	}

	if !hasAccess {
		JS.Alert("unauthorized")
		return
	}

	HTTP.Send(syncCallbackTapo, "tapo", "sync")
}

func togglePower(el js.Value, evs []js.Value) {
	name := strings.Split(el.Get("id").String(), "_")[2]

	elBtn, err := DOM.GetElement(el.Get("id").String())
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	value := !strings.Contains(elBtn.AttributeGet("className"), "imgBtnBorder")

	if value {
		selectedDevice = name
		HTTP.Send(togglePowerCallback, "tapo", "on", name)
		return
	}

	JS.PopupConfirm("Tapo", "Power off "+name+"?", "No", "Yes", func(accepted bool) {
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

	el, err := DOM.GetElement("tapo_devices_" + selectedDevice + "_power")
	if err != nil {
		return
	}
	skipBtnUpdateCount = 5
	selectedDevice = ""

	if res == "false" {
		el.AttributeSet("className", "imgBtn imgBtnMedium")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnMedium imgBtnBorder")
	}
}

func toggleInfo(el js.Value, evs []js.Value) {
	// name := strings.Split(el.Get("id").String(), "_")[2:3]
	fmt.Println(el.Get("id").String())
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
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_info", "class": "imgBtn imgBtnMedium"},
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
	el.EventAdd("click", toggleInfo)

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
		JS.Alert(resErr.Error())
		return
	}

	resp := map[string]DeviceEnergy{}
	if err := json.Unmarshal(resBytes, &resp); err != nil {
		JS.Alert(err.Error())
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

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + monitors)

	HTTP.HasAccessTo(accessCallbackTapo, "tapo")
}
