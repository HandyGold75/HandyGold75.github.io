//go:build js && wasm

package Home

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
)

func Page(forcePage func(string), setLoginSuccessCallback func(func())) {
	header := HTML.HTML{Tag: "h1", Inner: "Home"}.String()

	link := HTML.HTML{Tag: "a",
		Attributes: map[string]string{"href": "./python"},
		Inner:      "python",
	}.String()

	txt := HTML.HTML{
		Tag:   "p",
		Inner: "Moving towards GO wasm instead of Python wasm<br><br>For reasons...<br><br>Old site still available at " + link,
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + txt)
}