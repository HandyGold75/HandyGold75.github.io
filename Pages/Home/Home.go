//go:build js && wasm

package Home

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"fmt"

	"github.com/raitonoberu/ytsearch"
)

func Page(forcePage func(string), setLoginSuccessCallback func(func())) {
	header := HTML.HTML{Tag: "h1", Inner: "Home"}.String()

	link := HTML.HTML{Tag: "a",
		Attributes: map[string]string{"href": "./.python/"},
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

	searchStr := "Spacemen - Electric Callboy"
	fmt.Println(searchStr)

	search := ytsearch.VideoSearch(searchStr)
	result, err := search.Next()
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println(result)
}
