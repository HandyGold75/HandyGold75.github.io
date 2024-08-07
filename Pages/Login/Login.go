//go:build js && wasm

package Login

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"strconv"
	"strings"
	"syscall/js"
)

var (
	OnLoginSuccessCallback = (func())(nil)
	ForcePage              = func(string) {}
)

func autocompleteCallback(res string, resBytes []byte, resErr error) {
	defer func() {
		if OnLoginSuccessCallback == nil {
			JS.Async(func() { ForcePage("Home") })
			return
		}
		OnLoginSuccessCallback()
		OnLoginSuccessCallback = nil
	}()
	if resErr != nil {
		return
	}

	err := json.Unmarshal(resBytes, &HTTP.Autocompletes)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
}

func isAuthenticatedCallback(authErr error) {
	if authErr != nil && strings.HasPrefix(authErr.Error(), "429 TooManyRequest") {
		errSplit := strings.Split(authErr.Error(), ":")
		retryAfter, err := strconv.Atoi(errSplit[len(errSplit)-1])
		if err != nil {
			JS.Alert(err.Error())
			retryAfter = 60
		}

		JS.Alert("You've got timed out for " + strconv.Itoa(retryAfter) + "!")
		JS.AfterDelay(retryAfter*1000, func() { HTTP.IsAuthenticated(isAuthenticatedCallback) })
		return
	}
	if authErr != nil || !HTTP.Config.RememberSignIn {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		elSub.Enable()

		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	if el, err := DOM.GetElement("footer_login"); err == nil {
		el.AttributeSet("innerHTML", "Logout")
	}

	err = toggleDocker(false)
	if err != nil {
		if el, err := DOM.GetElement("docker"); err == nil {
			el.Remove()
		}
		HTTP.Send(autocompleteCallback, "autocomplete")
		return
	}

	JS.AfterDelay(250, func() {
		if el, err := DOM.GetElement("docker"); err == nil {
			el.Remove()
		}
		HTTP.Send(autocompleteCallback, "autocomplete")
	})
}

func authenticateCallback(authErr error) {
	if authErr != nil {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		elSub.Enable()
		elSub.StyleSet("border", "2px solid #F55")
		JS.AfterDelay(3000, func() { elSub.StyleSet("border", "2px solid #55F") })

		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	if el, err := DOM.GetElement("footer_login"); err == nil {
		el.AttributeSet("innerHTML", "Logout")
	}

	if err := toggleDocker(false); err != nil {
		if el, err := DOM.GetElement("docker"); err == nil {
			el.Remove()
		}
		HTTP.Send(autocompleteCallback, "autocomplete")
		return
	}

	JS.AfterDelay(250, func() {
		if el, err := DOM.GetElement("docker"); err == nil {
			el.Remove()
		}
		HTTP.Send(autocompleteCallback, "autocomplete")
	})
}

func toggleRemember(el js.Value, evs []js.Value) {
	err := HTTP.Config.Set("RememberSignIn", strconv.FormatBool(!HTTP.Config.RememberSignIn))
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	if HTTP.Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	} else {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall")
	}
}

func toggleDocker(show bool) error {
	buttons, _ := DOM.GetElements("docker_buttons")
	titles, _ := DOM.GetElements("docker_titles")
	subs, _ := DOM.GetElements("docker_subs")
	docker, err := DOM.GetElement("docker")
	if err != nil {
		return err
	}
	docker_showhide, err := DOM.GetElement("docker_showhide")
	if err != nil {
		return err
	}
	docker_showhide_img, err := DOM.GetElement("docker_showhide_img")
	if err != nil {
		return err
	}

	if show {
		buttons.Enables()
		buttons.StylesSet("opacity", "1")
		titles.StylesSet("color", "#bff")
		titles.StylesSet("opacity", "1")
		subs.StylesSet("opacity", "1")
		docker.StyleSet("max-width", "250px")
		docker.StyleSet("max-height", "100vh")
		docker.StyleSet("margin", "0px")
		docker.StyleSet("padding", "4px")
		docker_showhide.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
		docker_showhide_img.AttributeSet("src", "./docs/assets/General/Hide-H.svg")
		return nil
	}

	buttons.Disables()
	buttons.StylesSet("opacity", "0")
	titles.StylesSet("color", "#88b")
	titles.StylesSet("opacity", "0")
	subs.StylesSet("opacity", "0")
	docker.StyleSet("max-width", "50px")
	docker.StyleSet("max-height", "48px")
	docker.StyleSet("margin", "-20px 0px 0px -20px")
	docker.StyleSet("padding", "0px")
	docker_showhide.AttributeSet("className", "imgBtn imgBtnSmall")
	docker_showhide_img.AttributeSet("src", "./docs/assets/General/Show-H.svg")
	return nil
}

func submitLogin(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		JS.Alert("evs was not parsed")
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.Disables()

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elSub.Disable()

	elSrv, err := DOM.GetElement("login_server")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	server := elSrv.AttributeGet("value")

	elUsr, err := DOM.GetElement("login_username")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	username := elUsr.AttributeGet("value")

	elPsw, err := DOM.GetElement("login_password")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	password := elPsw.AttributeGet("value")

	err = HTTP.Config.Set("Server", server)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	HTTP.Authenticate(authenticateCallback, username, password)
}

func Page(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage

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
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + server + username + password + buttons)

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	els.Disables()
	els.EventsAdd("keyup", submitLogin)

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elSub.Disable()
	elSub.EventAdd("click", submitLogin)

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elRem.EventAdd("click", toggleRemember)

	if HTTP.Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	}

	HTTP.IsAuthenticated(isAuthenticatedCallback)
}
