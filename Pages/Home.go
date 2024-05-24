//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"fmt"
)

func PageHome() {
	header := HTML.HTML{Tag: "h1", Inner: "Home"}.String()
	txt := HTML.HTML{
		Tag:   "p",
		Inner: "Moving towards GO wasm instead of Python wasm<br><br>For reasons...<br><br>Old site still available at " + HTML.HTML{Attributes: map[string]string{"href": "./python"}, Inner: "./python"}.ApplyTemplate(HTML.HTML_Link).String(),
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + txt)
}
