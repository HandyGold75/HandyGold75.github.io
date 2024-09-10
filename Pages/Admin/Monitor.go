//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
)

func showMonitor(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Config") }) })
		return
	} else if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if !hasAccess {
		Widget.PopupAlert("Error", "unauthorized", func() {})
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Config"}.String()

	body := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  "",
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + body)
}

func DebugCallback(res string, resBytes []byte, resErr error) {}

func PageMonitor(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Config") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	HTTP.HasAccessTo(showMonitor, "debug")
}
