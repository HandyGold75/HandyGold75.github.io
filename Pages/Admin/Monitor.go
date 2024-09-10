//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"strconv"
	"strings"
	"time"
)

// func getUserDiv(user User) {
// 	getRow := func(name string, typ string, autocomplete string, value string) []string {
// 		id := "monitor_users_" + strings.ToLower(name)

// 		txt := HTML.HTML{Tag: "p", Inner: name, Styles: map[string]string{"margin": "auto 0px", "padding": "5px 0px", "background": "#222", "border": "2px solid #111"}}.String()
// 		inp := HTML.HTML{Tag: "input", Attributes: map[string]string{"type": typ, "id": id, "class": "monitor_users_inputs", "autocomplete": autocomplete, "placeholder": name, "value": value}}.String()
// 		btn := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": id + "_submit", "class": "dark medium monitor_users_submits"}, Inner: "Submit"}.String()

// 		return []string{txt, inp, btn}
// 	}

// 	selectedUser = user

// 	gridStyle := map[string]string{"display": "grid", "grid-template-columns": "20% 60% 20%", "background": "#2A2A2A"}

// 	header := HTML.HTML{Tag: "h2",
// 		Attributes: map[string]string{"id": "monitor_users_header"},
// 		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
// 		Inner:      HTTP.Sha1(user.Username + user.Password),
// 	}.String()

// 	username := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Username", "email", "username", user.Username), "")}.String()

// 	password := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Password", "password", "new-password", user.Password), "")}.String()

// 	row := getRow("authLevel", "", "", "")
// 	row[1] = HTML.HTML{Tag: "select",
// 		Attributes: map[string]string{"id": "monitor_users_authlevel", "class": "monitor_users_inputs", "size": "1"},
// 		Inner: func() string {
// 			s := ""
// 			for v := range authMap {
// 				if v == authMapReversed[user.AuthLevel] {
// 					s += HTML.HTML{Tag: "option", Attributes: map[string]string{"selected": ""}, Inner: v}.String()
// 					continue
// 				}
// 				s += HTML.HTML{Tag: "option", Inner: v}.String()
// 			}
// 			return s
// 		}(),
// 	}.String()
// 	authLevel := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(row, "")}.String()

// 	roles := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Roles", "text", "", strings.Join(user.Roles, ", ")), "")}.String()

// 	state := "Disabled"
// 	btnClass := "imgBtn imgBtnMedium"
// 	if user.Enabled {
// 		state = "Enabled"
// 		btnClass = "imgBtn imgBtnMedium imgBtnBorder"
// 	}

// 	enabledBtn := HTML.HTML{Tag: "button",
// 		Attributes: map[string]string{"id": "monitor_users_enabled", "class": btnClass},
// 		Inner:      HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "monitor_users_enabled_img", "src": "./docs/assets/Admin/Users/" + state + ".svg", "alt": state}}.String(),
// 	}.String()

// 	trashBtn := HTML.HTML{Tag: "button",
// 		Attributes: map[string]string{"id": "monitor_users_delete", "class": "imgBtn imgBtnMedium"},
// 		Inner:      HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "monitor_users_delete_img", "src": "./docs/assets/General/Trash.svg", "alt": "delete"}}.String(),
// 	}.String()

// 	deauthBtn := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "monitor_users_deauth", "class": "dark large"}, Inner: "Deauth"}.String()

// 	spacer := HTML.HTML{Tag: "div", Styles: map[string]string{"background": "#2A2A2A"}}.String()
// 	buttons := HTML.HTML{Tag: "div", Styles: map[string]string{"display": "grid", "grid-template-columns": "5% 25% 5% 25% 5% 30% 5%", "background": "#2A2A2A"}, Inner: spacer + enabledBtn + spacer + trashBtn + spacer + deauthBtn + spacer}.String()

// 	el, err := DOM.GetElement("monitor_users_out")
// 	if err != nil {
// 		Widget.PopupAlert("Error", err.Error(), func() {})
// 		return
// 	}
// 	el.InnerSet(header + username + password + authLevel + roles + buttons)
// 	el.StyleSet("max-height", "100vh")

// 	for _, key := range []string{"username", "password", "authlevel", "roles"} {
// 		el, err = DOM.GetElement("monitor_users_" + key)
// 		if err != nil {
// 			Widget.PopupAlert("Error", err.Error(), func() {})
// 			return
// 		}
// 		el.EventAdd("keyup", modifyUser)

// 		el, err = DOM.GetElement("monitor_users_" + key + "_submit")
// 		if err != nil {
// 			Widget.PopupAlert("Error", err.Error(), func() {})
// 			return
// 		}
// 		el.EventAdd("click", modifyUser)
// 	}

// 	el, err = DOM.GetElement("monitor_users_enabled")
// 	if err != nil {
// 		Widget.PopupAlert("Error", err.Error(), func() {})
// 		return
// 	}
// 	el.EventAdd("click", toggleEnabled)

// 	el, err = DOM.GetElement("monitor_users_delete")
// 	if err != nil {
// 		Widget.PopupAlert("Error", err.Error(), func() {})
// 		return
// 	}
// 	el.EventAdd("click", deleteUser)

// 	el, err = DOM.GetElement("monitor_users_deauth")
// 	if err != nil {
// 		Widget.PopupAlert("Error", err.Error(), func() {})
// 		return
// 	}
// 	el.EventAdd("click", deauthUser)
// }

func showMonitor(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Monitor") }) })
		return
	} else if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if !hasAccess {
		Widget.PopupAlert("Error", "unauthorized", func() {})
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Monitor"}.String()

	body := HTML.HTML{Tag: "div",
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

func debugCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Logs") }) })
		return
	} else if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	debug := map[string]AuthToken{}
	err := json.Unmarshal(resBytes, &debug)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	el, err := DOM.GetElement("monitor_users")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet("")

	for token, auth := range debug {
		authToken := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "AuthToken"}.String() +
				HTML.HTML{Tag: "p", Inner: token}.String(),
		}.String()

		userHash := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "UserHash"}.String() +
				HTML.HTML{Tag: "p", Inner: auth.UserHash}.String(),
		}.String()

		expires := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "Expires"}.String() +
				HTML.HTML{Tag: "p", Inner: auth.Expires.Format(time.DateTime)}.String(),
		}.String()

		username := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "Username"}.String() +
				HTML.HTML{Tag: "p", Inner: auth.UserData.Username}.String(),
		}.String()

		authLevel := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "AuthLevel"}.String() +
				HTML.HTML{Tag: "p", Inner: strconv.Itoa(auth.UserData.AuthLevel)}.String(),
		}.String()

		roles := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "Roles"}.String() +
				HTML.HTML{Tag: "p", Inner: "[" + strings.Join(auth.UserData.Roles, ", ") + "]"}.String(),
		}.String()

		enabled := HTML.HTML{Tag: "div",
			Inner: HTML.HTML{Tag: "p", Inner: "Enabled"}.String() +
				HTML.HTML{Tag: "p", Inner: strconv.FormatBool(auth.UserData.Enabled)}.String(),
		}.String()

		userDataDiv := HTML.HTML{Tag: "div", Inner: expires + username + authLevel + roles + enabled,
			Styles: map[string]string{
				"display":    "flex",
				"background": "#2A2A2A",
			},
		}.String()

		div := HTML.HTML{Tag: "div", Inner: authToken + userHash + userDataDiv,
			Styles: map[string]string{
				"margin":     "10px auto",
				"background": "#2A2A2A",
				"border":     "2px solid #111",
			},
		}.String()

		el, err := DOM.GetElement("monitor_users")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		el.InnerAddSurfix(div)
	}
}

func PageMonitor(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Admin:Monitor") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	HTTP.HasAccessTo(showMonitor, "debug")
}
