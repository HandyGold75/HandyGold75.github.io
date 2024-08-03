//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

type (
	SyncInfo struct {
		Track   TrackInfo
		Playing bool
		Shuffle bool
		Repeat  bool
		Volume  int
	}

	TrackInfo struct {
		QuePosition string
		Duration    string
		URI         string
		Progress    string
		AlbumArtURI string
		Title       string
		Class       string
		Creator     string
		Album       string
	}

	QueInfo struct {
		Count      string
		TotalCount string
		Tracks     []QueTrack
	}

	QueTrack struct {
		AlbumArtURI string
		Title       string
		Class       string
		Creator     string
		Album       string
	}
)

var (
	ytPlayer = js.Value{}

	syncInfo = SyncInfo{}
	queInfo  = QueInfo{}
)

func accessCallback(hasAccess bool, err error) {
	if HTTP.IsAuthError(err) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if err != nil {
		JS.Alert(err.Error())
		return
	}

	if !hasAccess {
		JS.Alert("unauthorized")
		return
	}

	showSonos()
}

func showSonos() {
	spacer := HTML.HTML{Tag: "div"}.String()
	callback := func(res string, resBytes []byte, resErr error) {}

	// YT Player
	ifr := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "ytdl_player_ifr", "frameborder": "0"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "70vh"},
	}.String()

	img := HTML.HTML{Tag: "img",
		Attributes: map[string]string{"src": "docs/assets/General/Transparent.svg"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "70vh"},
	}.String()

	divYTPlayer := HTML.HTML{Tag: "div",
		Styles: map[string]string{"position": "relative", "padding": "0px 0px min(70vh, 56.25%) 0px"},
		Inner:  ifr + img,
	}.String()

	// Timeline
	txtCur := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "ytdl_timeline_progress"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
		Inner:      "00:00",
	}.String()

	btnSeekBackward := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_actions_seek_backward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekBackward.svg", "alt": "seek_backward"},
		}.String(),
	}.String()

	sliderTimeline := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"id": "ytdl_timeline_slider", "type": "range", "min": "0", "max": "0"},
		Styles:     map[string]string{"width": "75%", "accent-color": "#F7E163"},
	}.String()

	btnSeekForward := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_actions_seek_forward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekForward.svg", "alt": "seek_forward"},
		}.String(),
	}.String()

	txtMax := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "ytdl_timeline_duration"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
		Inner:      "00:00",
	}.String()

	divTimeline := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  spacer + txtCur + btnSeekBackward + sliderTimeline + btnSeekForward + txtMax + spacer,
	}.String()

	// Controls
	buttonKeys := [][3]string{
		{"shuffle", "Shuffle.svg", "imgBtnSmall"},
		{"back", "Back.svg", "imgBtnMedium"},
		{"play", "Play.svg", "imgBtnMedium"},
		{"next", "Next.svg", "imgBtnMedium"},
		{"repeat", "Repeat.svg", "imgBtnSmall"},
	}

	buttons := ""
	for _, keys := range buttonKeys {
		buttons += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"id": "ytdl_actions_" + keys[0], "class": "imgBtn " + keys[2]},
			Inner: HTML.HTML{Tag: "img",
				Attributes: map[string]string{"id": "ytdl_actions_" + keys[0] + "_img", "src": "./docs/assets/Sonos/" + keys[1], "alt": keys[0]},
			}.String(),
		}.String()
	}

	divControls := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex", "margin": "0px auto -15px auto"},
		Inner:  spacer + buttons + spacer,
	}.String()

	// Volume
	datalistItems := ""
	for i := 0; i <= 10; i++ {
		datalistItems += HTML.HTML{Tag: "option", Attributes: map[string]string{"value": strconv.Itoa(i * 10)}}.String()
	}
	datalist := HTML.HTML{Tag: "datalist",
		Attributes: map[string]string{"id": "ytdl_actions_volume_slider_datalist"},
		Inner:      datalistItems,
	}.String()

	btnVolumeDown := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_actions_volume_down", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeDown.svg", "alt": "volume_down"},
		}.String(),
	}.String()

	sliderVolume := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"id": "ytdl_actions_volume_slider", "type": "range", "min": "0", "max": "100", "list": "ytdl_actions_volume_slider_datalist"},
		Styles:     map[string]string{"width": "25%", "margin": "10px", "padding": "0px", "accent-color": "#F7E163"},
	}.String()

	btnVolumeUp := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "ytdl_actions_volume_up", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeUp.svg", "alt": "volume_up"},
		}.String(),
	}.String()

	divVolume := HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  datalist + spacer + btnVolumeDown + sliderVolume + btnVolumeUp + spacer,
	}.String()

	// Que
	divQue := HTML.HTML{Tag: "div",
		Styles:     map[string]string{"display": "flex"},
		Attributes: map[string]string{"id": "ytdl_que"},
	}.String()

	// Finalize
	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(divYTPlayer + divTimeline + divControls + divVolume + divQue)

	JS.Async(func() {
		argBytes, err := json.Marshal(map[string]any{
			"videoId": "",
			"playerVars": map[string]int{
				"autoplay":       0,
				"controls":       0,
				"disablekb":      1,
				"fs":             0,
				"iv_load_policy": 3,
				"modestbranding": 1,
				"rel":            0,
			},
		})
		if err != nil {
			JS.Alert(err.Error())
			return
		}
		ytPlayer = JS.New("YT.Player", "ytdl_player_ifr", string(argBytes))
	})

	// Timeline
	el, err := DOM.GetElement("ytdl_actions_seek_backward")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", "-10")
	})

	el, err = DOM.GetElement("ytdl_timeline_slider")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("keyup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", el.Get("value").String())
	})
	el.EventAdd("mouseup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", el.Get("value").String())
	})

	el, err = DOM.GetElement("ytdl_actions_seek_forward")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", "+10")
	})

	// Control
	el, err = DOM.GetElement("ytdl_actions_shuffle")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Shuffle {
			HTTP.Send(callback, "sonos", "shuffle", "0")
		} else {
			HTTP.Send(callback, "sonos", "shuffle", "1")
		}
	})

	el, err = DOM.GetElement("ytdl_actions_back")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "position", "-1")
	})

	el, err = DOM.GetElement("ytdl_actions_play")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Playing {
			HTTP.Send(callback, "sonos", "play", "0")
		} else {
			HTTP.Send(callback, "sonos", "play", "1")
		}
	})

	el, err = DOM.GetElement("ytdl_actions_next")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "position", "+1")
	})

	el, err = DOM.GetElement("ytdl_actions_repeat")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Repeat {
			HTTP.Send(callback, "sonos", "repeat", "0")
		} else {
			HTTP.Send(callback, "sonos", "repeat", "1")
		}
	})

	// Volume
	el, err = DOM.GetElement("ytdl_actions_volume_up")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", "+5")
	})

	el, err = DOM.GetElement("ytdl_actions_volume_slider")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("keyup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", el.Get("value").String())
	})
	el.EventAdd("mouseup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", el.Get("value").String())
	})

	el, err = DOM.GetElement("ytdl_actions_volume_down")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", "-5")
	})

	// Finalize
	HTTP.Send(syncCallback, "sonos", "sync")
	HTTP.Send(queCallback, "sonos", "que")
}

func syncCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	err := json.Unmarshal(resBytes, &syncInfo)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	// Timeline
	el, err := DOM.GetElement("ytdl_timeline_progress")
	if err != nil {
		return
	}

	if strings.HasPrefix(syncInfo.Track.Progress, "0:") {
		el.InnerSet(strings.Replace(syncInfo.Track.Progress, "0:", "", 1))
	} else {
		el.InnerSet(syncInfo.Track.Progress)
	}

	el, err = DOM.GetElement("ytdl_timeline_slider")
	if err != nil {
		return
	}

	dur, err := time.Parse(time.TimeOnly, syncInfo.Track.Duration)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	h, m, s := dur.Clock()
	el.AttributeSet("max", strconv.Itoa((h*1440)+(m*60)+s))

	pro, err := time.Parse(time.TimeOnly, syncInfo.Track.Progress)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	h, m, s = pro.Add(time.Second).Clock()
	el.AttributeSet("value", strconv.Itoa((h*1440)+(m*60)+s))

	el, err = DOM.GetElement("ytdl_timeline_duration")
	if err != nil {
		return
	}

	if strings.HasPrefix(syncInfo.Track.Duration, "0:") {
		el.InnerSet(strings.Replace(syncInfo.Track.Duration, "0:", "", 1))
	} else {
		el.InnerSet(syncInfo.Track.Duration)
	}

	// Controls
	el, err = DOM.GetElement("ytdl_actions_shuffle")
	if err != nil {
		return
	}

	if syncInfo.Shuffle {
		el.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnSmall")
	}

	el, err = DOM.GetElement("ytdl_actions_play_img")
	if err != nil {
		return
	}

	if syncInfo.Playing {
		el.AttributeSet("src", "./docs/assets/Sonos/Pause.svg")
		el.AttributeSet("alt", "pause")
	} else {
		el.AttributeSet("src", "./docs/assets/Sonos/Play.svg")
		el.AttributeSet("alt", "play")
	}

	el, err = DOM.GetElement("ytdl_actions_repeat")
	if err != nil {
		return
	}

	if syncInfo.Repeat {
		el.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnSmall")
	}

	// Volume
	el, err = DOM.GetElement("ytdl_actions_volume_slider")
	if err != nil {
		return
	}
	el.AttributeSet("value", strconv.Itoa(syncInfo.Volume))

	JS.AfterDelay(1000, func() { HTTP.Send(syncCallback, "sonos", "sync") })
}

func queCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	err := json.Unmarshal(resBytes, &queInfo)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
}

func PageSonos(forcePage func(string), setLoginSuccessCallback func(func())) {
	ForcePage = forcePage
	SetLoginSuccessCallback = setLoginSuccessCallback

	if !HTTP.IsMaybeAuthenticated() {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		JS.Async(func() { ForcePage("Login") })
		return
	}

	HTTP.HasAccessTo(accessCallback, "sonos")
}
