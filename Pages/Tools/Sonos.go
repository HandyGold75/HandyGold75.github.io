//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

type (
	SyncInfo struct {
		Track struct {
			QuePosition string
			Duration    string
			Progress    string
			Title       string
			Creator     string
			Album       string
		}
		Que struct {
			Count      string
			TotalCount string
		}
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

	YTInfo struct {
		ID        string
		Title     string
		Duration  int
		ViewCount int
		Creator   string
	}
)

var (
	ytPlayer = js.Value{}

	syncInfo = SyncInfo{}
	ytInfo   = []YTInfo{}
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

func getYTPlayer() string {
	ifr := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sonos_player_ifr", "frameborder": "0"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "75vh"},
	}.String()

	img := HTML.HTML{Tag: "img",
		Attributes: map[string]string{"src": "docs/assets/General/Transparent.svg"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "75vh"},
	}.String()

	return HTML.HTML{Tag: "div",
		Styles: map[string]string{"position": "relative", "padding": "0px 0px min(75vh, 56.25%) 0px"},
		Inner:  ifr + img,
	}.String()
}

func setEventsYTPlayer() error {
	JS.Async(func() {
		args := map[string]any{
			"videoId": "",
			"playerVars": map[string]any{
				"autoplay":       0,
				"controls":       0,
				"disablekb":      1,
				"enablejsapi":    1,
				"fs":             0,
				"iv_load_policy": 3,
				"origin":         "https://www.HandyGold75.com",
				"rel":            0,
			},
		}
		ytPlayer = JS.New("YT.Player", "sonos_player_ifr", args)
	})

	return nil
}

func updateYTPlayer() error {
	if !ytPlayer.Get("s").Bool() {
		if _, err := DOM.GetElement("sonos_player_ifr"); err != nil {
			return nil
		}

		JS.AfterDelay(100, func() { updateYTPlayer() })
		return nil
	}

	video := ytInfo[0]

	pro, err := time.Parse(time.TimeOnly, syncInfo.Track.Progress)
	if err != nil {
		return err
	}
	h, m, s := pro.Add(time.Second).Clock()

	ytPlayer.Call("mute")
	ytPlayer.Call("setVolume", 0)
	ytPlayer.Call("setLoop", true)
	ytPlayer.Call("loadVideoById", video.ID, (h*1440)+(m*60)+s)

	return nil
}

func getTimeline() string {
	txtCur := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "sonos_timeline_progress"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
		Inner:      "00:00",
	}.String()

	btnSeekBackward := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sonos_actions_seek_backward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekBackward.svg", "alt": "seek_backward"},
		}.String(),
	}.String()

	sliderTimeline := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"id": "sonos_timeline_slider", "type": "range", "min": "0", "max": "0"},
		Styles:     map[string]string{"width": "75%", "accent-color": "#F7E163"},
	}.String()

	btnSeekForward := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sonos_actions_seek_forward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekForward.svg", "alt": "seek_forward"},
		}.String(),
	}.String()

	txtMax := HTML.HTML{Tag: "p",
		Attributes: map[string]string{"id": "sonos_timeline_duration"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
		Inner:      "00:00",
	}.String()

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  spacer + txtCur + btnSeekBackward + sliderTimeline + btnSeekForward + txtMax + spacer,
	}.String()
}

func setEventsTimeline() error {
	callback := func(res string, resBytes []byte, resErr error) {}

	el, err := DOM.GetElement("sonos_actions_seek_backward")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", "-10")
	})

	el, err = DOM.GetElement("sonos_timeline_slider")
	if err != nil {
		return err
	}
	el.EventAdd("keyup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", el.Get("value").String())
	})
	el.EventAdd("mouseup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", el.Get("value").String())
	})

	el, err = DOM.GetElement("sonos_actions_seek_forward")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "seek", "+10")
	})

	return nil
}

func updateTimeline() error {
	pro, err := time.Parse(time.TimeOnly, syncInfo.Track.Progress)
	if err != nil {
		return err
	}
	hp, mp, sp := pro.Add(time.Second).Clock()
	proSecs := (hp * 1440) + (mp * 60) + sp
	proStr := fmt.Sprintf("%d:%02d", mp, sp)
	if hp != 0 {
		proStr = strconv.Itoa(hp) + ":" + proStr
	}

	dur, err := time.Parse(time.TimeOnly, syncInfo.Track.Duration)
	if err != nil {
		JS.Alert(err.Error())
		return err
	}
	hd, md, sd := dur.Clock()
	durSecs := (hd * 1440) + (md * 60) + sd
	durStr := fmt.Sprintf("%d:%02d", md, sd)
	if hd != 0 {
		durStr = strconv.Itoa(hd) + ":" + durStr
	}

	el, err := DOM.GetElement("sonos_timeline_progress")
	if err != nil {
		return err
	}
	el.InnerSet(proStr)

	el, err = DOM.GetElement("sonos_timeline_slider")
	if err != nil {
		return err
	}
	el.AttributeSet("max", strconv.Itoa(durSecs))
	el.AttributeSet("value", strconv.Itoa(proSecs))

	el, err = DOM.GetElement("sonos_timeline_duration")
	if err != nil {
		return err
	}

	el.InnerSet(durStr)

	if ytPlayer.Get("s").Bool() {
		playerPos := ytPlayer.Call("getCurrentTime").Int()
		if proSecs > playerPos+1 || proSecs < playerPos-1 {
			ytPlayer.Call("seekTo", proSecs)
		}
	}

	return nil
}

func getControls() string {
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
			Attributes: map[string]string{"id": "sonos_actions_" + keys[0], "class": "imgBtn " + keys[2]},
			Inner: HTML.HTML{Tag: "img",
				Attributes: map[string]string{"id": "sonos_actions_" + keys[0] + "_img", "src": "./docs/assets/Sonos/" + keys[1], "alt": keys[0]},
			}.String(),
		}.String()
	}

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex", "margin": "0px auto -25px auto"},
		Inner:  spacer + buttons + spacer,
	}.String()
}

func setEventsControls() error {
	callback := func(res string, resBytes []byte, resErr error) {}

	el, err := DOM.GetElement("sonos_actions_shuffle")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Shuffle {
			HTTP.Send(callback, "sonos", "shuffle", "0")
		} else {
			HTTP.Send(callback, "sonos", "shuffle", "1")
		}
	})

	el, err = DOM.GetElement("sonos_actions_back")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "position", "-1")
	})

	el, err = DOM.GetElement("sonos_actions_play")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Playing {
			HTTP.Send(callback, "sonos", "play", "0")
		} else {
			HTTP.Send(callback, "sonos", "play", "1")
		}
	})

	el, err = DOM.GetElement("sonos_actions_next")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "position", "+1")
	})

	el, err = DOM.GetElement("sonos_actions_repeat")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if syncInfo.Repeat {
			HTTP.Send(callback, "sonos", "repeat", "0")
		} else {
			HTTP.Send(callback, "sonos", "repeat", "1")
		}
	})

	return nil
}

func updateControls() error {
	el, err := DOM.GetElement("sonos_actions_shuffle")
	if err != nil {
		return err
	}

	if syncInfo.Shuffle {
		el.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnSmall")
	}

	el, err = DOM.GetElement("sonos_actions_play_img")
	if err != nil {
		return err
	}

	if syncInfo.Playing {
		if ytPlayer.Get("s").Bool() {
			ytPlayer.Call("playVideo")
		}
		el.AttributeSet("src", "./docs/assets/Sonos/Pause.svg")
		el.AttributeSet("alt", "pause")

	} else {
		if ytPlayer.Get("s").Bool() {
			ytPlayer.Call("pauseVideo")
		}
		el.AttributeSet("src", "./docs/assets/Sonos/Play.svg")
		el.AttributeSet("alt", "play")
	}

	el, err = DOM.GetElement("sonos_actions_repeat")
	if err != nil {
		return err
	}

	if syncInfo.Repeat {
		el.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
	} else {
		el.AttributeSet("className", "imgBtn imgBtnSmall")
	}

	return nil
}

func getVolume() string {
	datalistItems := ""
	for i := 0; i <= 10; i++ {
		datalistItems += HTML.HTML{Tag: "option", Attributes: map[string]string{"value": strconv.Itoa(i * 10)}}.String()
	}
	datalist := HTML.HTML{Tag: "datalist",
		Attributes: map[string]string{"id": "sonos_actions_volume_slider_datalist"},
		Inner:      datalistItems,
	}.String()

	btnVolumeDown := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sonos_actions_volume_down", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeDown.svg", "alt": "volume_down"},
		}.String(),
	}.String()

	sliderVolume := HTML.HTML{Tag: "input",
		Attributes: map[string]string{"id": "sonos_actions_volume_slider", "type": "range", "min": "0", "max": "100", "list": "sonos_actions_volume_slider_datalist"},
		Styles:     map[string]string{"width": "30%", "margin": "10px", "padding": "0px", "accent-color": "#F7E163"},
	}.String()

	btnVolumeUp := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "sonos_actions_volume_up", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeUp.svg", "alt": "volume_up"},
		}.String(),
	}.String()

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{Tag: "div",
		Styles: map[string]string{"display": "flex"},
		Inner:  datalist + spacer + btnVolumeDown + sliderVolume + btnVolumeUp + spacer,
	}.String()
}

func setEventsVolume() error {
	callback := func(res string, resBytes []byte, resErr error) {}

	el, err := DOM.GetElement("sonos_actions_volume_up")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", "+5")
	})

	el, err = DOM.GetElement("sonos_actions_volume_slider")
	if err != nil {
		return err
	}
	el.EventAdd("keyup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", el.Get("value").String())
	})
	el.EventAdd("mouseup", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", el.Get("value").String())
	})

	el, err = DOM.GetElement("sonos_actions_volume_down")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(callback, "sonos", "volume", "-5")
	})

	return nil
}

func updateVolume() error {
	el, err := DOM.GetElement("sonos_actions_volume_slider")
	if err != nil {
		return err
	}
	el.AttributeSet("value", strconv.Itoa(syncInfo.Volume))

	return nil
}

func getQue() string {
	return HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "sonos_que"},
		Styles: map[string]string{
			"display":    "flex",
			"margin":     "25px auto 0px auto",
			"padding":    "0px",
			"overflow-x": "scroll",
			"border":     "4px solid #111",
		},
	}.String()
}

func updateQue() error {
	quePos, err := strconv.Atoi(syncInfo.Track.QuePosition)
	if err != nil {
		return err
	}

	tracks := ""
	for i, track := range queInfo.Tracks {
		imgMargin := "-4px 5px -4px 0px"
		if i == 0 {
			imgMargin = "-4px 5px -4px -4px"
		}

		textColor := "#55F"
		imgBorder := "4px solid #111"
		imgBorderRadius := "10px"
		divBackground := "#202020"
		if i == quePos {
			textColor = "#f7e163"
			imgBorder = "4px solid #f7e163"
			imgBorderRadius = "0px"
			divBackground = "#333"
		}

		img := HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": track.AlbumArtURI},
			Styles: map[string]string{
				"width":         "3.5em",
				"height":        "3.5em",
				"margin":        imgMargin,
				"border":        imgBorder,
				"border-radius": imgBorderRadius,
			},
		}.String()

		title := HTML.HTML{Tag: "p",
			Styles: map[string]string{
				"color":         textColor,
				"text-overflow": "ellipsis",
				"overflow":      "hidden",
			},
			Inner: track.Title,
		}.String()
		creator := HTML.HTML{Tag: "p",
			Styles: map[string]string{
				"color":         textColor,
				"text-overflow": "ellipsis",
				"overflow":      "hidden",
				"font-size":     "75%",
			},
			Inner: track.Creator}.String()
		div := HTML.HTML{Tag: "div",
			Styles: map[string]string{
				"margin":     "auto 5px auto auto",
				"padding":    "0px",
				"background": divBackground,
			},
			Inner: title + creator,
		}.String()

		tracks += HTML.HTML{Tag: "div",
			Attributes: map[string]string{"id": "sonos_que_track_" + strconv.Itoa(i), "class": "sonos_que_tracks"},
			Styles: map[string]string{
				"display":       "flex",
				"max-width":     "20%",
				"background":    divBackground,
				"border-radius": "10px 0px 0px 10px",
				"white-space":   "nowrap",
				"padding":       "0px",
				"overflow":      "visible",
			},
			Inner: img + div,
		}.String()
	}

	el, err := DOM.GetElement("sonos_que")
	if err != nil {
		return err
	}
	el.InnerSet(tracks)

	els, err := DOM.GetElements("sonos_que_tracks")
	if err != nil {
		return err
	}
	els.EventsAdd("dblclick", func(el js.Value, evs []js.Value) {
		idSplit := strings.Split(el.Get("id").String(), "_")
		HTTP.Send(func(res string, resBytes []byte, resErr error) {}, "sonos", "position", idSplit[len(idSplit)-1])
	})

	JS.OnResizeAdd("Sonos", func() {
		el, err = DOM.GetElement("sonos_que_track_" + syncInfo.Track.QuePosition)
		if err != nil {
			JS.OnResizeDelete("Sonos")
			return
		}
		el.El.Call("scrollIntoView", map[string]any{"inline": "start"})
	})

	return nil
}

func showSonos() {
	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(getYTPlayer() + getTimeline() + getControls() + getVolume() + getQue())

	if err := setEventsYTPlayer(); err != nil {
		JS.Alert(err.Error())
		return
	}
	if err := setEventsTimeline(); err != nil {
		JS.Alert(err.Error())
		return
	}
	if err := setEventsControls(); err != nil {
		JS.Alert(err.Error())
		return
	}
	if err := setEventsVolume(); err != nil {
		JS.Alert(err.Error())
		return
	}

	HTTP.Send(syncCallback, "sonos", "sync")
}

func syncCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	oldSyncInfo := syncInfo

	err := json.Unmarshal(resBytes, &syncInfo)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	if syncInfo.Que.TotalCount != oldSyncInfo.Que.TotalCount {
		HTTP.Send(ytqueryCallback, "sonos", "ytquery", syncInfo.Track.Title+" - "+syncInfo.Track.Creator)
		HTTP.Send(queCallback, "sonos", "que")
	} else if syncInfo.Track.QuePosition != oldSyncInfo.Track.QuePosition {
		HTTP.Send(ytqueryCallback, "sonos", "ytquery", syncInfo.Track.Title+" - "+syncInfo.Track.Creator)
		if err := updateQue(); err != nil {
			return
		}
	}

	if err := updateTimeline(); err != nil {
		return
	}
	if err := updateControls(); err != nil {
		return
	}
	if err := updateVolume(); err != nil {
		return
	}

	JS.AfterDelay(1000, func() { HTTP.Send(syncCallback, "sonos", "sync") })
}

func ytqueryCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		SetLoginSuccessCallback(func() { JS.Async(func() { ForcePage("Tools:Sonos") }) })
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	err := json.Unmarshal(resBytes, &ytInfo)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	if err := updateYTPlayer(); err != nil {
		return
	}
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

	if err := updateQue(); err != nil {
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
