//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/WS"
	"fmt"
	"strconv"
	"strings"
)

func IsAuthenticatedCallback(authError error) {
	if strings.HasPrefix(authError.Error(), "429 TooManyRequest") {
		errSplit := strings.Split(authError.Error(), ":")
		retryAfter, err := strconv.Atoi(errSplit[len(errSplit)-1])
		if err != nil {
			fmt.Println(err)
			retryAfter = 60
		}
		PageLoginTimeout(retryAfter)
		return
	}
	if authError != nil {
		fmt.Println(authError)
		return
	}
}

func PageLoginTimeout(duration int) {
}

func PageLogin() {
	if JS.CacheGet("server") == "" {
		JS.CacheSet("server", "https.HandyGold75.com:17500")
	}

	header := HTML.HTML{Tag: "h1", Inner: "Login"}.String()

	server := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Server",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "url", "id": "login_server", "placeholder": "Server", "value": JS.CacheGet("server")},
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
			Attributes: map[string]string{"type": "email", "id": "login_username", "placeholder": "Username"},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	password := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p",
			Inner:  "Password",
			Styles: map[string]string{"width": "20%", "margin": "auto 0px auto auto", "background": "#1f1f1f", "border": "2px solid #111"},
		}.String() + HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": "password", "id": "login_password", "placeholder": "Password"},
			Styles:     map[string]string{"width": "60%", "margin-right": "auto"},
		}.String()}.String()

	pinBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "login_remember", "class": "imgBtn imgBtnSmall"},
		Styles:     map[string]string{"max-width": "50px", "max-height": "50px"},
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

	WS.IsAuthenticated(IsAuthenticatedCallback)
	WS.Authenticate(func(err error) {}, "handygold75", "Password123")
}
