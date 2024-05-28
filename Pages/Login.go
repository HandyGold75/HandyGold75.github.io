//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/WS"
	"fmt"
)

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

	WS.SetServer("10.69.2.58:5500")
	if !WS.IsAuthenticated() {
		WS.Authenticate("", "")
	}
}
