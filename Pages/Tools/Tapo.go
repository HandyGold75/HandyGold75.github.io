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

func addDevice(name string) error {
	headStyle := map[string]string{"font-size": "125%", "font-weight": "bold", "white-space": "nowrap"}
	txtStyle := map[string]string{"margin": "0px auto 0px 0px", "white-space": "nowrap"}
	outStyle := map[string]string{"margin": "0px 5px", "white-space": "nowrap"}
	divStyle := map[string]string{"display": "flex", "padding": "0px", "background": "#2A2A2A"}

	header := HTML.HTML{Tag: "h2", Inner: name}.String()

	head := HTML.HTML{Tag: "p", Inner: "Current", Styles: headStyle}.String()

	txt := HTML.HTML{Tag: "p", Inner: "Power", Styles: txtStyle}.String()
	out := HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_current_power"}, Styles: outStyle}.String()
	power := HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	current := HTML.HTML{Tag: "div", Inner: head + power,
		Styles: map[string]string{
			"width":      "50%",
			"margin":     "10px auto",
			"background": "#2A2A2A",
			"border":     "2px solid #191919",
		},
	}.String()

	head = HTML.HTML{Tag: "p", Inner: "Today", Styles: headStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Power", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_today_power"}, Styles: outStyle}.String()
	power = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Runtime", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_today_runtime"}, Styles: outStyle}.String()
	runtime := HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	today := HTML.HTML{Tag: "div", Inner: head + power + runtime,
		Styles: map[string]string{
			"width":      "50%",
			"background": "#2A2A2A",
		},
	}.String()

	head = HTML.HTML{Tag: "p", Inner: "month", Styles: headStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Power", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_month_power"}, Styles: outStyle}.String()
	power = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	txt = HTML.HTML{Tag: "p", Inner: "Runtime", Styles: txtStyle}.String()
	out = HTML.HTML{Tag: "p", Attributes: map[string]string{"id": "tapo_devices_" + name + "_month_runtime"}, Styles: outStyle}.String()
	runtime = HTML.HTML{Tag: "div", Inner: txt + out, Styles: divStyle}.String()

	month := HTML.HTML{Tag: "div", Inner: head + power + runtime,
		Styles: map[string]string{
			"width":      "50%",
			"background": "#2A2A2A",
		},
	}.String()

	stats := HTML.HTML{Tag: "div", Inner: today + month,
		Styles: map[string]string{
			"display":    "flex",
			"background": "#2A2A2A",
			"border":     "2px solid #191919",
		},
	}.String()

	div := HTML.HTML{Tag: "div", Inner: header + current + stats,
		Attributes: map[string]string{"id": "tapo_devices_" + name},
		Styles:     map[string]string{"min-width": "300px", "background": "#2A2A2A"},
	}.String()

	el, err := DOM.GetElement("tapo_monitors")
	if err != nil {
		return err
	}
	el.InnerAddSurfix(div)

	return updateDevice(name, DeviceEnergy{})
}

func updateDevice(name string, specs DeviceEnergy) error {
	el, err := DOM.GetElement("tapo_devices_" + name + "_current_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(specs.CurrentPower))

	el, err = DOM.GetElement("tapo_devices_" + name + "_today_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(specs.TodayEnergy))

	el, err = DOM.GetElement("tapo_devices_" + name + "_today_runtime")
	if err != nil {
		return err
	}
	el.InnerSet(SectoString(specs.TodayRuntime))

	el, err = DOM.GetElement("tapo_devices_" + name + "_month_power")
	if err != nil {
		return err
	}
	el.InnerSet(WattToString(specs.MonthEnergy))

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

func WattToString(w int) string {
	if w > 1000 {
		return fmt.Sprintf("%0.1f", float64(w)/1000) + " kw"
	} else if w > 1000000 {
		return fmt.Sprintf("%0.1f", float64(w)/1000000) + " mw"
	} else if w > 1000000000 {
		return fmt.Sprintf("%0.1f", float64(w)/1000000000) + " gw"
	}
	return strconv.Itoa(w) + " w"
}

func SectoString(m int) string {
	if m > 60 {
		return fmt.Sprintf("%0.1f", float64(m)/60) + " h"
	} else if m > 1440 {
		return fmt.Sprintf("%0.1f", float64(m)/1440) + " d"
	} else if m > 10080 {
		return fmt.Sprintf("%0.1f", float64(m)/10080) + " w"
	} else if m > 43800 {
		return fmt.Sprintf("%0.1f", float64(m)/43800) + " M"
	} else if m > 525600 {
		return fmt.Sprintf("%0.1f", float64(m)/525600) + " Y"
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
