//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/base64"
	"strings"
	"syscall/js"
)

var (
	audioOnly  = false
	lowQuality = false
	forceMP4   = false
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

	args := []string{}
	if audioOnly {
		args = append(args, "audio")
	}
	if lowQuality {
		args = append(args, "low")
	}
	if forceMP4 {
		args = append(args, "mp4")
	}

	HTTP.Send(submitURLCallback, "ytdl", append([]string{"download", elInp.AttributeGet("value")}, args...)...)
}

func submitURLCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
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

	if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	resBase := make([]byte, base64.RawStdEncoding.EncodedLen(len(resBytes)))
	base64.RawStdEncoding.Encode(resBase, resBytes)

	resSplit := strings.Split(res, ".")
	err = JS.Download(res, "video/"+resSplit[len(resSplit)-1]+";base64", resBase)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
}

func toggleAudioOnly(el js.Value, evs []js.Value) {
	audioOnly = !audioOnly
	elOpt, err := DOM.GetElement("ytdl_option_audio_only")
	if err != nil {
		JS.Alert(err.Error())
	}

	if audioOnly {
		elOpt.AttributeSet("className", "dark small border")
		return
	}
	elOpt.AttributeSet("className", "dark small")
}

func toggleLowQuality(el js.Value, evs []js.Value) {
	lowQuality = !lowQuality
	elOpt, err := DOM.GetElement("ytdl_option_low_quality")
	if err != nil {
		JS.Alert(err.Error())
	}

	if lowQuality {
		elOpt.AttributeSet("className", "dark small border")
		return
	}
	elOpt.AttributeSet("className", "dark small")
}

func toggleForceMP4(el js.Value, evs []js.Value) {
	forceMP4 = !forceMP4
	elOpt, err := DOM.GetElement("ytdl_option_force_mp4")
	if err != nil {
		JS.Alert(err.Error())
	}

	if forceMP4 {
		elOpt.AttributeSet("className", "dark small border")
		return
	}
	elOpt.AttributeSet("className", "dark small")
}

func showYTDL() {
	header := HTML.HTML{Tag: "h1", Inner: "YTDL",
		Styles: map[string]string{"max-width": "min(100%, 1250px)"},
	}.String()

	spacer := HTML.HTML{Tag: "div", Styles: map[string]string{"background": "#2A2A2A"}}.String()

	inp := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"type": "url", "id": "ytdl_input", "autocomplete": "url", "placeholder": "URL"},
		Styles:     map[string]string{"width": "55%"},
	}.String()

	btnConfirm := HTML.HTML{Tag: "button", Inner: "Download",
		Attributes: map[string]string{"id": "ytdl_confirm", "class": "dark medium"},
	}.String()

	selectDiv := HTML.HTML{Tag: "div", Inner: spacer + inp + btnConfirm + spacer,
		Styles: map[string]string{
			"display":    "flex",
			"max-width":  "min(75%, 1000px)",
			"margin":     "25px auto 0px auto",
			"padding":    "10px 4px",
			"background": "#2A2A2A",
			"border":     "2px solid #191919",
		},
	}.String()

	btnAudio := HTML.HTML{Tag: "button", Inner: "Audio Only",
		Attributes: map[string]string{"id": "ytdl_option_audio_only", "class": "dark small"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
	}.String()

	btnLow := HTML.HTML{Tag: "button", Inner: "Low Quality",
		Attributes: map[string]string{"id": "ytdl_option_low_quality", "class": "dark small"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
	}.String()

	btnMP4 := HTML.HTML{Tag: "button", Inner: "Force MP4",
		Attributes: map[string]string{"id": "ytdl_option_force_mp4", "class": "dark small"},
		Styles:     map[string]string{"margin": "auto 2px", "white-space": "nowrap"},
	}.String()

	optionsDiv := HTML.HTML{Tag: "div", Inner: spacer + btnAudio + btnLow + btnMP4 + spacer,
		Styles: map[string]string{
			"display":    "flex",
			"max-width":  "min(75%, 1000px)",
			"margin":     "-2px auto 25px auto",
			"padding":    "10px 4px",
			"background": "#2A2A2A",
			"border":     "2px solid #191919",
		},
	}.String()

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

	el, err = DOM.GetElement("ytdl_option_audio_only")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", toggleAudioOnly)

	el, err = DOM.GetElement("ytdl_option_low_quality")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", toggleLowQuality)

	el, err = DOM.GetElement("ytdl_option_force_mp4")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", toggleForceMP4)
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
