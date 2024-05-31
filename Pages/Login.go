//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/WS"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"syscall/js"
)

type config struct {
	Server         string
	RememberSignIn bool
	Token          string
}

var (
	OnSuccessCallback = func() {}

	Config = config{
		Server:         "https.HandyGold75.com:17500",
		RememberSignIn: true,
		Token:          "",
	}
)

func isAuthenticatedCallback(authErr error) {
	if authErr != nil && strings.HasPrefix(authErr.Error(), "429 TooManyRequest") {
		errSplit := strings.Split(authErr.Error(), ":")
		retryAfter, err := strconv.Atoi(errSplit[len(errSplit)-1])
		if err != nil {
			fmt.Println(err)
			retryAfter = 60
		}

		JS.Alert("You've got timed out for " + strconv.Itoa(retryAfter) + "!")
		JS.AfterDelay(retryAfter*1000, func() { WS.IsAuthenticated(isAuthenticatedCallback) })
		return
	}
	if authErr != nil {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			fmt.Println(err)
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			fmt.Println(err)
			return
		}
		elSub.Enable()

		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	OnSuccessCallback()
	OnSuccessCallback = func() {}
}

func authenticateCallback(authErr error) {
	if authErr != nil {
		els, err := DOM.GetElements("login_inputs")
		if err != nil {
			fmt.Println(err)
			return
		}
		els.Enables()

		elSub, err := DOM.GetElement("login_submit")
		if err != nil {
			fmt.Println(err)
			return
		}
		elSub.Enable()
		elSub.StyleSet("border", "2px solid #F55")
		JS.AfterDelay(3000, func() { elSub.StyleSet("border", "2px solid #55F") })

		fmt.Println(authErr)
		return
	}

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.StyleSet("border", "2px solid #5F5")

	OnSuccessCallback()
	OnSuccessCallback = func() {}
}

func toggleRemember(el js.Value, evs []js.Value) {
	*&Config.RememberSignIn = !Config.RememberSignIn

	cfgBytes, err := json.Marshal(&Config)
	if err != nil {
		fmt.Println(err)
		return
	}
	JS.CacheSet("Login", string(cfgBytes))

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		fmt.Println(err)
		return
	}

	if Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	} else {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall")
	}
}

func submitLogin(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		fmt.Println("evs was not parsed")
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		fmt.Println(err)
		return
	}
	els.Disables()

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.Disable()

	elSrv, err := DOM.GetElement("login_server")
	if err != nil {
		fmt.Println(err)
		return
	}
	server := elSrv.AttributeGet("value")

	elUsr, err := DOM.GetElement("login_username")
	if err != nil {
		fmt.Println(err)
		return
	}
	username := elUsr.AttributeGet("value")

	elPsw, err := DOM.GetElement("login_password")
	if err != nil {
		fmt.Println(err)
		return
	}
	password := elPsw.AttributeGet("value")

	*&Config.Server = server

	cfgBytes, err := json.Marshal(&Config)
	if err != nil {
		fmt.Println(err)
		return
	}
	JS.CacheSet("Login", string(cfgBytes))

	JS.CacheSet("server", server)
	WS.Authenticate(authenticateCallback, username, password)
}

func PageLogin() {
	if JS.CacheGet("Login") == "" {
		cfgBytes, err := json.Marshal(&Config)
		if err != nil {
			fmt.Println(err)
			return
		}
		JS.CacheSet("Login", string(cfgBytes))
	}
	err := json.Unmarshal([]byte(JS.CacheGet("Login")), &Config)
	if err != nil {
		fmt.Println(err)
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Login"}.String()

	server := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Server",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "url", "id": "login_server", "class": "login_inputs", "placeholder": "Server", "value": Config.Server},
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
			Attributes: map[string]string{"type": "email", "id": "login_username", "class": "login_inputs", "placeholder": "Username"},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	password := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Password",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "password", "id": "login_password", "class": "login_inputs", "placeholder": "Password"},
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
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + server + username + password + buttons)

	els, err := DOM.GetElements("login_inputs")
	if err != nil {
		fmt.Println(err)
		return
	}
	els.Disables()
	els.EventsAdd("keyup", submitLogin)

	elSub, err := DOM.GetElement("login_submit")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.Disable()
	elSub.EventAdd("click", submitLogin)

	elRem, err := DOM.GetElement("login_remember")
	if err != nil {
		fmt.Println(err)
		return
	}
	elRem.EventAdd("click", toggleRemember)

	if Config.RememberSignIn {
		elRem.AttributeSet("className", "imgBtn imgBtnSmall imgBtnBorder")
	}

	WS.IsAuthenticated(isAuthenticatedCallback)
}
