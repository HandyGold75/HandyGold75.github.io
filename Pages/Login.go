//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/WS"
	"fmt"
	"strconv"
	"strings"
)

func IsAuthenticatedCallback(isAuthenticated error) {
	if isAuthenticated != nil {
		if strings.HasPrefix(isAuthenticated.Error(), "429 TooManyRequest") {
			errSplit := strings.Split(isAuthenticated.Error(), ":")
			retryAfter, err := strconv.Atoi(errSplit[len(errSplit)-1])
			if err != nil {
				fmt.Println(err)
				retryAfter = 60
			}
			PageLoginTimeout(retryAfter)
			return
		}
		return
	}
}

func PageLoginTimeout(duration int) {
}

func PageLogin() {
	header := HTML.HTML{Tag: "h1", Inner: "Login"}.String()
	txt := HTML.HTML{
		Tag:   "p",
		Inner: "Login page",
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + txt)

	WS.SetServer("10.69.2.58:17500")
	WS.IsAuthenticated(IsAuthenticatedCallback)
	WS.Authenticate(func(err error) {}, "handygold75", "Password123")
}
