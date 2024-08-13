//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"

	"github.com/achetronic/tapogo/api/types"
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

func addDevice(name string) {
	header := HTML.HTML{Tag: "h2", Inner: name}.String()

	title := HTML.HTML{Tag: "p",
		Styles: map[string]string{"font-size": "125%", "font-weight": "bold"},
		Inner:  "Daily",
	}.String()

	txt := HTML.HTML{Tag: "p",
		Styles: map[string]string{"margin": "0px auto 0px 0px"},
		Inner:  "Power",
	}.String()
	out := HTML.HTML{Tag: "p",
		Styles:     map[string]string{"margin": "0px 0px auto 0px"},
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_daily_runtime"},
	}.String()
	power := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  txt + out,
	}.String()

	txt = HTML.HTML{Tag: "p",
		Styles: map[string]string{"margin": "0px auto 0px 0px"},
		Inner:  "Runtime",
	}.String()
	out = HTML.HTML{Tag: "p",
		Styles:     map[string]string{"margin": "0px 0px auto 0px"},
		Attributes: map[string]string{"id": "tapo_devices_" + name + "_daily_runtime"},
	}.String()
	runtime := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  txt + out,
	}.String()

	daily := HTML.HTML{Tag: "div",
		Styles: map[string]string{"": ""},
		Inner:  title + power + runtime,
	}.String()

	// title = HTML.HTML{Tag: "p", Inner: "Montly"}.String()

	// txt = HTML.HTML{Tag: "p", Inner: "Power"}.String()
	// out = HTML.HTML{Tag: "p",
	// 	Attributes: map[string]string{"id": "tapo_devices_" + name + "_montly_runtime"},
	// }.String()
	// power = HTML.HTML{Tag: "div",
	// 	Styles: map[string]string{"display": "flex"},
	// 	Inner:  txt + out,
	// }.String()

	// txt = HTML.HTML{Tag: "p", Inner: "Runtime"}.String()
	// out = HTML.HTML{Tag: "p",
	// 	Attributes: map[string]string{"id": "tapo_devices_" + name + "_montly_runtime"},
	// 	Styles: map[string]string{"display": "flex"},
	// }.String()
	// runtime = HTML.HTML{Tag: "div",
	// 	Styles: map[string]string{"display": "flex"},
	// 	Inner:  txt + out,
	// }.String()

	// montly := HTML.HTML{Tag: "div",
	// 	Styles: map[string]string{"": ""},
	// 	Inner:  title + power + runtime,
	// }.String()

	div := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "tapo_devices_" + name},
		Styles:     map[string]string{"min-width": "200px"},
		Inner:      header + daily, // + montly,
	}.String()

	el, err := DOM.GetElement("tapo_monitors")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.InnerAddSurfix(div)
}

func syncCallbackTapo(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Tapo") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	resp := map[string]types.ResponseSpec{}
	err := json.Unmarshal(resBytes, &resp)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	for name, spec := range resp {
		el, err := DOM.GetElement("tapo_devices_" + name)
		if err != nil {
			addDevice(name)
			continue
		}
		el.InnerGet()

		fmt.Println("----")
		fmt.Println(name)
		fmt.Println(spec)
	}
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
		Styles: map[string]string{
			"display":    "flex",
			"overflow-x": "scroll",
		},
		Inner: "",
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + monitors)

	HTTP.HasAccessTo(accessCallbackTapo, "tapo")
}
