//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"fmt"
)

func LogListCallback(res string, resErr error) {
	if resErr == WebKit.ErrWebKit.HTTPUnauthorized || resErr == WebKit.ErrWebKit.HTTPNoServerSpecified {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Logs") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	fmt.Println(res)

}

func PageAdminLogs() {
	if !HTTP.IsMaybeAuthenticated() {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Logs") }) }
		JS.Async(func() { ForcePage("Login") })
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Logs"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_types"},
		Styles:     map[string]string{"width": "95%", "border-left": "2px solid #111", "border-right": "2px solid #111", "border-top": "2px solid #111", "border-radius": "10px 10px 0px 0px"},
	}.String()

	dates := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "logs_dates"},
		Styles:     map[string]string{"width": "95%", "border-left": "2px solid #111", "border-right": "2px solid #111", "border-bottom": "2px solid #111", "border-radius": "0px 0px 10px 10px"},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + types + dates)

	HTTP.Send(LogListCallback, "logs")
}
