//go:build js && wasm

package Pages

import (
	"WebKit/DOM"
	"WebKit/HTML"
	"fmt"
)

func PageHome() {
	txt := HTML.HTML{
		Tag:        "p",
		Attributes: map[string]string{"id": "someText"},
		Styles:     map[string]string{"color": "#55F"},
		Inner:      "Moving towards GO wasm instead of Python wasm<br><br><br><br><br><br><br><br><br><br><br><br><br>For reasons...<br>Old site should still be available at " + HTML.HTML{Attributes: map[string]string{"href": "./python"}, Inner: "./python"}.ApplyTemplate(HTML.HTML_Link).String(),
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(txt)

	el, err := DOM.GetElement("someText")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(el.InnerGet())
}
