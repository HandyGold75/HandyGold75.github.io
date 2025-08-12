//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"maps"
	"slices"
	"strings"
	"syscall/js"
	"time"
)

var selectedToken = ""

func deauthToken(el js.Value, els []js.Value) {
	if selectedToken != "" {
		return
	}

	selectedToken = strings.Split(el.Get("id").String(), "_")[2]

	elBtn, err := DOM.GetElement("monitor_users_" + selectedToken + "_deauth")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elBtn.Disable()

	HTTP.Send(deauthTokenCallback, "users", "deauth", "token", selectedToken)
}

func deauthTokenCallback(res string, resBytes []byte, resErr error) {
	defer func() { selectedToken = "" }()
	if resErr != nil {
		elBtn, err := DOM.GetElement("monitor_users_" + selectedToken + "_deauth")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else {
			elBtn.Enable()
		}

		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	if err := Widget.AnimateStyle("monitor_users_"+selectedToken, "max-height", "0px", "150px", 250); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
	}

	el, err := DOM.GetElement("monitor_users_" + selectedToken)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	JS.AfterDelay(250, func() { el.Remove() })
}

func debugCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	debug := map[string]AuthToken{}
	err := json.Unmarshal(resBytes, &debug)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	authDataTextStyle := map[string]string{
		"max-width":   "50%",
		"background":  "#222",
		"border":      "2px solid #111",
		"overflow-x":  "scroll",
		"white-space": "nowrap",
	}

	userDataTextStyle := map[string]string{
		"max-width":   "30%",
		"background":  "#222",
		"border":      "2px solid #111",
		"overflow-x":  "scroll",
		"white-space": "nowrap",
	}

	el, err := DOM.GetElement("monitor_users")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet("")

	pWrapper := func(txt string) string { return HTML.HTML{Tag: "p", Inner: txt}.String() }

	JS.ForEach(slices.Collect(maps.Keys(debug)), 250, func(token string, _ bool) bool {
		auth := debug[token]

		authToken := HTML.HTML{
			Tag: "div", Inner: pWrapper("AuthToken") + pWrapper(token),
			Styles: authDataTextStyle,
		}.String()

		expires := HTML.HTML{
			Tag: "div", Inner: pWrapper("Expires") + pWrapper(auth.Expires.Format(time.DateTime)),
			Styles: authDataTextStyle,
		}.String()

		deauthBtn := HTML.HTML{
			Tag: "button", Inner: "Deauth",
			Attributes: map[string]string{"id": "monitor_users_" + token + "_deauth", "class": "dark large"},
			Styles:     map[string]string{"white-space": "nowrap"},
		}.String()

		authDataDiv := HTML.HTML{
			Tag: "div", Inner: authToken + expires + deauthBtn,
			Styles: map[string]string{
				"display":    "flex",
				"background": "#2A2A2A",
			},
		}.String()

		userHash := HTML.HTML{
			Tag: "div", Inner: pWrapper(auth.UserHash),
			Styles: userDataTextStyle,
		}.String()
		username := HTML.HTML{
			Tag: "div", Inner: pWrapper(auth.UserData.Username),
			Styles: userDataTextStyle,
		}.String()
		authLevel := HTML.HTML{
			Tag: "div", Inner: pWrapper(authMapReversed[auth.UserData.AuthLevel]),
			Styles: userDataTextStyle,
		}.String()
		roles := HTML.HTML{
			Tag: "div", Inner: pWrapper(strings.Join(auth.UserData.Roles, ", ")),
			Styles: userDataTextStyle,
		}.String()

		state := "Disabled"
		if auth.UserData.Enabled {
			state = "Enabled"
		}
		enabled := HTML.HTML{
			Tag: "div", Inner: pWrapper(state),
			Styles: userDataTextStyle,
		}.String()

		userDataDiv := HTML.HTML{
			Tag: "div", Inner: userHash + username + authLevel + roles + enabled,
			Styles: map[string]string{
				"display":       "flex",
				"background":    "#2A2A2A",
				"border-top":    "2px dashed #111",
				"border-radius": "0px",
			},
		}.String()

		div := HTML.HTML{
			Tag: "div", Inner: authDataDiv + userDataDiv,
			Attributes: map[string]string{"id": "monitor_users_" + token},
			Styles: map[string]string{
				"max-height": "0px",
				"margin":     "10px auto",
				"background": "#2A2A2A",
				"border":     "2px solid #111",
			},
		}.String()

		el, err := DOM.GetElement("monitor_users")
		if err != nil {
			return false
		}
		el.InnerAddSurfix(div)

		JS.AfterDelay(50, func() {
			if err := Widget.AnimateStyle("monitor_users_"+token, "max-height", "0px", "150px", 250); err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
			}
		})

		el, err = DOM.GetElement("monitor_users_" + token + "_deauth")
		if err != nil {
			return false
		}
		el.EventAdd("click", deauthToken)

		return true
	})
}

func showMonitor() {
	header := HTML.HTML{Tag: "h1", Inner: "Monitor"}.String()

	body := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "monitor_users"},
		Styles:     map[string]string{"width": "80%"},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + body)

	HTTP.Send(debugCallback, "debug", "auth")
}

func PageMonitor() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("debug", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showMonitor()
		}
	})
}
