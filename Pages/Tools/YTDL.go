//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"fmt"
	"syscall/js"
)

func accessCallbackYTDL(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:YTDL") }) })
		return
	} else if err != nil {
		JS.Alert(err.Error())
		return
	}

	if !hasAccess {
		JS.Alert("unauthorized")
		return
	}

	showYTDL()
}

func showYTDL() {
	header := HTML.HTML{Tag: "h1", Inner: "YTDL"}.String()

	spacer := HTML.HTML{Tag: "div"}.String()

	inp := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"type": "url", "id": "ytdl_input", "autocomplete": "url", "placeholder": "URL"},
		Styles: map[string]string{
			"width":  "60%",
			"margin": "auto 5px",
		},
	}.String()

	btnConfirm := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_confirm", "class": "dark medium"},
		Styles:     map[string]string{"margin": "auto 2px"},
		Inner:      "Download",
	}.String()

	selectDiv := HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"display": "flex",
		},
		Inner: spacer + inp + btnConfirm + spacer,
	}.String()

	btnAudio := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_option_audio", "class": "dark medium"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
		Inner:      "Audio Only",
	}.String()

	btnLow := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_option_low", "class": "dark medium"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
		Inner:      "Low Quality",
	}.String()

	btnMP4 := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_option_mp4", "class": "dark medium"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
		Inner:      "Force MP4",
	}.String()

	optionsDiv := HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"display": "flex",
			"width":   "50%",
		},
		Inner: btnAudio + spacer + btnLow + spacer + btnMP4}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + selectDiv + optionsDiv)

	el, err := DOM.GetElement("ytdl_confirm")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", submitURL)

	el, err = DOM.GetElement("ytdl_input")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("keyup", submitURL)

}

func submitURL(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		JS.Alert("evs was not parsed")
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	elCon, err := DOM.GetElement("ytdl_confirm")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elCon.Disable()

	elInp, err := DOM.GetElement("ytdl_input")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elInp.Disable()

	HTTP.Send(submitURLCallback, "ytdl", "download", elInp.AttributeGet("value"), "low", "mp4")
}

func submitURLCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	elCon, err := DOM.GetElement("ytdl_confirm")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elCon.Enable()

	elInp, err := DOM.GetElement("ytdl_input")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	elInp.Enable()

	fmt.Println(res)
}

func PageYTDL(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:YTDL") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	HTTP.HasAccessTo(accessCallbackYTDL, "ytdl")
}
