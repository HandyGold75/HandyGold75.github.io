//go:build js && wasm

package Login

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"strconv"
	"strings"
	"syscall/js"
)

func autocompleteCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	err := json.Unmarshal(resBytes, &HTTP.Autocompletes)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	HTTP.AuthorizedCallback()
}

func isAuthenticatedCallback(authErr error) {
	if authErr != nil && strings.HasPrefix(authErr.Error(), "429 TooManyRequest") {
		errSplit := strings.Split(authErr.Error(), ":")
		retryAfter, err := strconv.Atoi(errSplit[len(errSplit)-1])
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			retryAfter = 60
		}

		Widget.PopupAlert("Error", "You've got timed out for "+strconv.Itoa(retryAfter)+"!", func() {})
		JS.AfterDelay(retryAfter*1000, func() { HTTP.IsAuthenticated(isAuthenticatedCallback) })
		return
	}
	if authErr != nil || !HTTP.Config.RememberSignIn {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elSub.Enable()

		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	if el, err := DOM.GetElement("footer_login"); err == nil {
		el.AttributeSet("innerHTML", "Logout")
	}

	HTTP.Send(autocompleteCallback, "autocomplete")
}

func authenticateCallback(authErr error) {
	if authErr != nil {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elSub.Enable()
		elSub.StyleSet("border", "2px solid #F55")
		JS.AfterDelay(3000, func() { elSub.StyleSet("border", "2px solid #55F") })

		Widget.PopupAlert("Error", authErr.Error(), func() {})

		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	if el, err := DOM.GetElement("footer_login"); err == nil {
		el.AttributeSet("innerHTML", "Logout")
	}
}

func toggleRemember(el js.Value, evs []js.Value) {
	err := HTTP.Config.Set("RememberSignIn", strconv.FormatBool(!HTTP.Config.RememberSignIn))
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if HTTP.Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	} else {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall")
	}
}

func submitLogin(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Disables()

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.Disable()

	elSrv, err := DOM.GetElement("login_server")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	server := elSrv.AttributeGet("value")

	elUsr, err := DOM.GetElement("login_username")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	username := elUsr.AttributeGet("value")

	elPsw, err := DOM.GetElement("login_password")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	password := elPsw.AttributeGet("value")

	err = HTTP.Config.Set("Server", server)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	HTTP.Authenticate(authenticateCallback, username, password)
}

func showLogin() {
	header := HTML.HTML{Tag: "h1", Inner: "Login"}.String()

	server := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Server",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "url", "id": "login_server", "class": "login_inputs", "autocomplete": "url", "placeholder": "Server", "value": HTTP.Config.Server},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	username := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Username",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{
			Tag:        "input",
			Attributes: map[string]string{"type": "email", "id": "login_username", "class": "login_inputs", "autocomplete": "username", "placeholder": "Username"},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	password := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Password",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "password", "id": "login_password", "class": "login_inputs", "autocomplete": "current-password", "placeholder": "Password"},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	pinBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "login_remember", "class": "imgBtn imgBtnSmall"},
		Styles:     map[string]string{"margin-top": "auto", "margin-bottom": "auto"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"id": "login_remember_img", "src": "./docs/assets/Login/Pin.svg", "alt": "remember"},
		}.String()}.String()

	spacer := HTML.HTML{Tag: "div"}.String()
	buttons := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: spacer +
			pinBtn +
			HTML.HTML{Tag: "div", Styles: map[string]string{"width": "25%"}}.String() +
			HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "login_submit", "class": "dark large"}, Inner: "Login"}.String() +
			spacer,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + server + username + password + buttons)

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Disables()
	els.EventsAdd("keyup", submitLogin)

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.Disable()
	elSub.EventAdd("click", submitLogin)

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elRem.EventAdd("click", toggleRemember)

	if HTTP.Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	}
}

func Page() {
	showLogin()
	HTTP.IsAuthenticated(isAuthenticatedCallback)
}
