//go:build js && wasm

package SpotifyAuthCallback

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
)

func showSpotifyAuthCallback() {
	header := HTML.HTML{Tag: "h1", Inner: "Spotify Token"}.String()

	txt := HTML.HTML{Tag: "p", Inner: JS.Href()}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + txt)
}

func Page() {
	showSpotifyAuthCallback()
}
