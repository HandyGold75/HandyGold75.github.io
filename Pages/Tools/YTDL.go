//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/base64"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

var (
	audioOnly  = false
	lowQuality = false
	forceMP4   = false

	requestedID = ""
)

func submitURL(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	elCon, err := DOM.GetElement("ytdl_confirm")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elCon.Disable()

	elInp, err := DOM.GetElement("ytdl_input")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elInp.Disable()
	url := elInp.AttributeGet("value")

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

	id := time.Now().Format(time.DateTime)

	titleTxt := HTML.HTML{Tag: "p", Inner: url,
		Attributes: map[string]string{"id": "ytdl_out_" + id + "_title"},
		Styles: map[string]string{
			"background":  "#2A2A2A",
			"white-space": "nowrap",
		},
	}.String()

	title := HTML.HTML{Tag: "a", Inner: titleTxt,
		Attributes: map[string]string{"href": url, "target": "_blank"},
		Styles: map[string]string{
			"width": "65%",
		},
	}.String()

	options := HTML.HTML{Tag: "p", Inner: strings.Join(args, ", "),
		Styles: map[string]string{
			"width":       "15%",
			"background":  "#2A2A2A",
			"white-space": "nowrap",
		},
	}.String()

	size := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "ytdl_out_" + id + "_size"},
		Styles: map[string]string{
			"width":       "10%",
			"background":  "#2A2A2A",
			"white-space": "nowrap",
		},
	}.String()

	state := HTML.HTML{Tag: "p", Inner: "Fetch",
		Attributes: map[string]string{"id": "ytdl_out_" + id + "_state"},
		Styles: map[string]string{
			"width":       "10%",
			"background":  "#2A2A2A",
			"color":       "#FF5",
			"white-space": "nowrap",
		},
	}.String()

	out := HTML.HTML{Tag: "div", Inner: title + options + size + state,
		Attributes: map[string]string{"id": "ytdl_out_" + id},
		Styles: map[string]string{
			"display":       "flex",
			"max-height":    "0px",
			"background":    "#2A2A2A",
			"margin":        "-1px auto 0px auto",
			"border-radius": "0px",
			"border-top":    "1px solid #191919",
		},
	}.String()

	elOut, err := DOM.GetElement("ytdl_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elOut.InnerAddPrefix(out)
	if err := Widget.AnimateStyle("ytdl_out_"+id, "max-height", "0px", "50px", 250); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
	}

	requestedID = id
	HTTP.Send(submitURLCallback, "ytdl", append([]string{"download", url}, args...)...)
}

func submitURLCallback(res string, resBytes []byte, resErr error) {
	setState := func(url string, state string, color string) {
		if el, err := DOM.GetElement("ytdl_out_" + url + "_state"); err == nil {
			el.InnerSet(state)
			el.StyleSet("color", color)
		}
	}

	url := requestedID
	requestedID = ""

	if el, err := DOM.GetElement("ytdl_confirm"); err == nil {
		el.Enable()
	}
	if el, err := DOM.GetElement("ytdl_input"); err == nil {
		el.Enable()
	}

	if resErr != nil {
		setState(url, "Failed", "#F55")
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	if el, err := DOM.GetElement("ytdl_out_" + url + "_title"); err == nil {
		el.InnerSet(res)
	}

	setState(url, "Encode", "#FF5")

	JS.Async(func() {
		resBase := make([]byte, base64.RawStdEncoding.EncodedLen(len(resBytes)))
		base64.RawStdEncoding.Encode(resBase, resBytes)

		size := float64(len(resBytes)) / 1024 / 1024
		if el, err := DOM.GetElement("ytdl_out_" + url + "_size"); err == nil {
			el.InnerSet(strconv.FormatFloat(size, 'f', 1, 64) + " MB")
		}

		setState(url, "Prepare", "#FF5")

		JS.Async(func() {
			resSplit := strings.Split(res, ".")
			Widget.Download(res, "video/"+resSplit[len(resSplit)-1]+";base64", resBase, func(err error) {
				if err != nil {
					setState(url, "Failed", "#F55")
					if size > 32 {
						Widget.PopupAlert("Warning", "Size greater then 32 MB!\n"+
							"\n"+
							"Firefox has a size limit of 32 MB\n"+
							"Chromium has a size limit of 512 MB\n"+
							"Safari has a size limit of 2048 MB\n"+
							"\n"+
							"https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URLs#length_limitations",
							func() {},
						)
					} else {
						Widget.PopupAlert("Error", err.Error(), func() {})
					}
					return
				}
				setState(url, "Success", "#5F5")
			})
		})
	})
}

func toggleAudioOnly(el js.Value, evs []js.Value) {
	audioOnly = !audioOnly
	elOpt, err := DOM.GetElement("ytdl_option_audio_only")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
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
		Widget.PopupAlert("Error", err.Error(), func() {})
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
		Widget.PopupAlert("Error", err.Error(), func() {})
	}

	if forceMP4 {
		elOpt.AttributeSet("className", "dark small border")
		return
	}
	elOpt.AttributeSet("className", "dark small")
}

func showYTDL() {
	header := HTML.HTML{Tag: "h1", Inner: "YTDL"}.String()

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

	outDiv := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "ytdl_out"},
		Styles: map[string]string{
			"max-width":  "min(75%, 1000px)",
			"min-height": "40px",
			"margin":     "25px auto 25px auto",
			"padding":    "0px",
			"background": "#2A2A2A",
			"border":     "2px solid #191919",
		},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + selectDiv + optionsDiv + outDiv)

	el, err := DOM.GetElement("ytdl_confirm")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", submitURL)

	el, err = DOM.GetElement("ytdl_input")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("keyup", submitURL)

	el, err = DOM.GetElement("ytdl_option_audio_only")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", toggleAudioOnly)
	Widget.Tooltip("ytdl_option_audio_only", "Option", "Only include audio.<br>Will not include video.", 1000)

	el, err = DOM.GetElement("ytdl_option_low_quality")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", toggleLowQuality)
	Widget.Tooltip("ytdl_option_low_quality", "Option", "Get the lowest possible quality.<br>Otherswide get the highest available quality.", 1000)

	el, err = DOM.GetElement("ytdl_option_force_mp4")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", toggleForceMP4)
	Widget.Tooltip("ytdl_option_force_mp4", "Option", "Force the MP4 file format.<br>This might result in a lower then the highest available quality.", 1000)
}

func PageYTDL() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("ytdl", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showYTDL()
		}
	})
}
