//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/Widget"
	"syscall/js"
)

func exitCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}
}

func restartCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}
}

func showConfig() {
	header := HTML.HTML{Tag: "h1", Inner: "Config"}.String()

	configs := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "config_configs"},
		Styles:     map[string]string{"display": "flex", "width": "75%"},
	}.String()

	exitBtn := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "config_actions_exit", "class": "dark medium"},
		Styles:     map[string]string{"width": "100%"},
		Inner:      "exit",
	}.String()

	restartBtn := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "config_actions_restart", "class": "dark medium"},
		Styles:     map[string]string{"width": "100%"},
		Inner:      "restart",
	}.String()

	actions := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "config_actions"},
		Styles:     map[string]string{"width": "25%", "padding": "8px"},
		Inner:      exitBtn + restartBtn,
	}.String()

	body := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  configs + actions,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + body)

	el, err := DOM.GetElement("config_actions_exit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(exitCallback, "exit")
	})

	el, err = DOM.GetElement("config_actions_restart")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(restartCallback, "restart")
	})
}

func PageConfig() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("exit", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showConfig()
		}
	})
}
