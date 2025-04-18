//go:build js && wasm

package Tools

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"fmt"
	"slices"
	"strconv"
	"strings"
	"syscall/js"
	"time"
)

type (
	SyncInfo struct {
		Track struct {
			QuePosition int
			Duration    string
			Progress    string
			Title       string
			Creator     string
			Album       string
		}
		Que struct {
			Count      int
			TotalCount int
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

	SonosDBVersion = 1

	imgCacheKeys = []string{}
	toAddImgs    = [][]string{}
)

func getYTPlayer() string {
	ifr := HTML.HTML{
		Tag:        "div",
		Attributes: map[string]string{"id": "sonos_player_ifr", "frameborder": "0"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "75vh"},
	}.String()

	img := HTML.HTML{
		Tag:        "img",
		Attributes: map[string]string{"src": "docs/assets/General/Transparent.svg"},
		Styles:     map[string]string{"position": "absolute", "width": "100%", "height": "100%", "max-height": "75vh"},
	}.String()

	return HTML.HTML{
		Tag: "div", Inner: ifr + img,
		Styles: map[string]string{"position": "relative", "padding": "0px 0px min(75vh, 56.25%) 0px"},
	}.String()
}

func isYTPlayerActive() bool {
	if ytPlayer.IsUndefined() || ytPlayer.Get("loadVideoById").IsUndefined() {
		return false
	}
	return true
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
	if !isYTPlayerActive() {
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
	txtCur := HTML.HTML{
		Tag: "p", Inner: "00:00",
		Attributes: map[string]string{"id": "sonos_timeline_progress"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
	}.String()

	btnSeekBackward := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "sonos_actions_seek_backward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekBackward.svg", "alt": "seek_backward"},
		}.String(),
	}.String()

	sliderTimeline := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"id": "sonos_timeline_slider", "type": "range", "min": "0", "max": "0"},
		Styles:     map[string]string{"width": "75%", "accent-color": "#F7E163"},
	}.String()

	btnSeekForward := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "sonos_actions_seek_forward", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/SeekForward.svg", "alt": "seek_forward"},
		}.String(),
	}.String()

	txtMax := HTML.HTML{
		Tag: "p", Inner: "00:00",
		Attributes: map[string]string{"id": "sonos_timeline_duration"},
		Styles:     map[string]string{"margin": "auto 10px", "color": "#F7E163"},
	}.String()

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{
		Tag: "div", Inner: spacer + txtCur + btnSeekBackward + sliderTimeline + btnSeekForward + txtMax + spacer,
		Styles: map[string]string{"display": "flex"},
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
		Widget.PopupAlert("Error", err.Error(), func() {})
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

	if isYTPlayerActive() {
		curTime := ytPlayer.Call("getCurrentTime")
		if curTime.IsUndefined() {
			return nil
		}
		playerPos := curTime.Int()
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
		buttons += HTML.HTML{
			Tag:        "button",
			Attributes: map[string]string{"id": "sonos_actions_" + keys[0], "class": "imgBtn " + keys[2]},
			Inner: HTML.HTML{
				Tag:        "img",
				Attributes: map[string]string{"id": "sonos_actions_" + keys[0] + "_img", "src": "./docs/assets/Sonos/" + keys[1], "alt": keys[0]},
			}.String(),
		}.String()
	}

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{
		Tag:    "div",
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
		HTTP.Send(callback, "sonos", "previous")
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
		HTTP.Send(callback, "sonos", "next")
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
	if syncInfo.Track.QuePosition < 1 {
		el.StyleSet("display", "none")
	} else {
		el.StyleSet("display", "")
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
		if isYTPlayerActive() {
			ytPlayer.Call("playVideo")
		}
		el.AttributeSet("src", "./docs/assets/Sonos/Pause.svg")
		el.AttributeSet("alt", "pause")

	} else {
		if isYTPlayerActive() {
			ytPlayer.Call("pauseVideo")
		}
		el.AttributeSet("src", "./docs/assets/Sonos/Play.svg")
		el.AttributeSet("alt", "play")
	}

	el, err = DOM.GetElement("sonos_actions_repeat")
	if err != nil {
		return err
	}
	if syncInfo.Track.QuePosition < 1 {
		el.StyleSet("display", "none")
	} else {
		el.StyleSet("display", "")
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
	datalist := HTML.HTML{
		Tag:        "datalist",
		Attributes: map[string]string{"id": "sonos_actions_volume_slider_datalist"},
		Inner:      datalistItems,
	}.String()

	btnVolumeDown := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "sonos_actions_volume_down", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeDown.svg", "alt": "volume_down"},
		}.String(),
	}.String()

	sliderVolume := HTML.HTML{
		Tag:        "input",
		Attributes: map[string]string{"id": "sonos_actions_volume_slider", "type": "range", "min": "0", "max": "100", "list": "sonos_actions_volume_slider_datalist"},
		Styles:     map[string]string{"width": "30%", "margin": "10px", "padding": "0px", "accent-color": "#F7E163"},
	}.String()

	btnVolumeUp := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "sonos_actions_volume_up", "class": "imgBtn imgBtnSmall"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"src": "./docs/assets/Sonos/VolumeUp.svg", "alt": "volume_up"},
		}.String(),
	}.String()

	spacer := HTML.HTML{Tag: "div"}.String()

	return HTML.HTML{
		Tag:    "div",
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
	return HTML.HTML{
		Tag:        "div",
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
	el, err := DOM.GetElement("sonos_que")
	if err != nil {
		return err
	}
	if syncInfo.Track.QuePosition < 1 {
		el.StyleSet("display", "none")
		return nil
	}

	tracks := ""
	for i, track := range queInfo.Tracks {
		imgMargin := "-4px 5px -4px 0px"
		if i == 0 {
			imgMargin = "-4px 5px -4px -4px"
		}
		pos := strconv.Itoa(i + 1)

		imgBorder := "4px solid #111"
		imgBorderRadius := "10px"
		textColor := "#55F"
		divBackground := "#202020"
		if i+1 == syncInfo.Track.QuePosition {
			imgBorder = "4px solid #f7e163"
			imgBorderRadius = "0px"
			textColor = "#f7e163"
			divBackground = "#333"
		}

		img := HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"id": "sonos_que_track_" + pos + "_img", "src": "./docs/assets/General/Load.svg"},
			Styles: map[string]string{
				"width":         "3.5em",
				"height":        "3.5em",
				"margin":        imgMargin,
				"border":        imgBorder,
				"border-radius": imgBorderRadius,
			},
		}.String()

		title := HTML.HTML{
			Tag:        "p",
			Attributes: map[string]string{"id": "sonos_que_track_" + pos + "_title"},
			Styles: map[string]string{
				"color":         textColor,
				"text-overflow": "ellipsis",
				"overflow":      "hidden",
			},
			Inner: track.Title,
		}.String()
		creator := HTML.HTML{
			Tag:        "p",
			Attributes: map[string]string{"id": "sonos_que_track_" + pos + "_creator"},
			Styles: map[string]string{
				"color":         textColor,
				"text-overflow": "ellipsis",
				"overflow":      "hidden",
				"font-size":     "75%",
			},
			Inner: track.Creator,
		}.String()
		div := HTML.HTML{
			Tag:        "div",
			Attributes: map[string]string{"id": "sonos_que_track_" + pos + "_div"},
			Styles: map[string]string{
				"margin":     "auto 5px auto auto",
				"padding":    "0px",
				"background": divBackground,
			},
			Inner: title + creator,
		}.String()

		tracks += HTML.HTML{
			Tag:        "div",
			Attributes: map[string]string{"id": "sonos_que_track_" + pos, "class": "sonos_que_tracks"},
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

	el.StyleSet("display", "flex")
	el.InnerSet(tracks)

	els, err := DOM.GetElements("sonos_que_tracks")
	if err != nil {
		return err
	}
	els.EventsAdd("dblclick", func(el js.Value, evs []js.Value) {
		idSplit := strings.Split(el.Get("id").String(), "_")
		HTTP.Send(func(res string, resBytes []byte, resErr error) {}, "sonos", "position", idSplit[len(idSplit)-1])
	})

	toAddImgs = [][]string{}
	for i, track := range queInfo.Tracks {
		toAddImgs = append(toAddImgs, []string{"sonos_que_track_" + strconv.Itoa(i+1) + "_img", track.AlbumArtURI})
	}

	if len(toAddImgs) > 0 {
		nextUri := toAddImgs[0][1]
		if slices.Contains(imgCacheKeys, nextUri) {
			JS.DBNew(func(db JS.DB, dbErr error) {
				db.Get(func(value string) {
					JS.Async(func() { addImgCallback(value, []byte{0}, nil) })
				}, "uris", nextUri)
			}, "Sonos", []string{"uris"}, SonosDBVersion)
		} else {
			HTTP.Send(addImgCallback, "sonos", "uri", nextUri)
		}

	}
	JS.OnResizeAdd("Sonos", func() {
		el, err = DOM.GetElement("sonos_que_track_" + strconv.Itoa(syncInfo.Track.QuePosition))
		if err != nil {
			JS.OnResizeDelete("Sonos")
			return
		}
		el.El.Call("scrollIntoView", map[string]any{"inline": "start"})
	})

	return nil
}

func updatedSelectedQueTrack(oldTrackPos string, newTrackPos string) error {
	el, err := DOM.GetElement("sonos_que_track_" + oldTrackPos + "_img")
	if err != nil {
		return err
	}
	el.StyleSet("border", "4px solid #111")
	el.StyleSet("border-radius", "10px")

	el, err = DOM.GetElement("sonos_que_track_" + oldTrackPos + "_title")
	if err != nil {
		return err
	}
	el.StyleSet("color", "#55F")

	el, err = DOM.GetElement("sonos_que_track_" + oldTrackPos + "_creator")
	if err != nil {
		return err
	}
	el.StyleSet("color", "#55F")

	el, err = DOM.GetElement("sonos_que_track_" + oldTrackPos + "_div")
	if err != nil {
		return err
	}
	el.StyleSet("background", "#202020")

	el, err = DOM.GetElement("sonos_que_track_" + oldTrackPos)
	if err != nil {
		return err
	}
	el.StyleSet("background", "#202020")

	el, err = DOM.GetElement("sonos_que_track_" + newTrackPos + "_img")
	if err != nil {
		return err
	}
	el.StyleSet("border", "4px solid #f7e163")
	el.StyleSet("border-radius", "0px")

	el, err = DOM.GetElement("sonos_que_track_" + newTrackPos + "_title")
	if err != nil {
		return err
	}
	el.StyleSet("color", "#f7e163")

	el, err = DOM.GetElement("sonos_que_track_" + newTrackPos + "_creator")
	if err != nil {
		return err
	}
	el.StyleSet("color", "#f7e163")

	el, err = DOM.GetElement("sonos_que_track_" + newTrackPos + "_div")
	if err != nil {
		return err
	}
	el.StyleSet("background", "#333")

	el, err = DOM.GetElement("sonos_que_track_" + newTrackPos)
	if err != nil {
		return err
	}
	el.StyleSet("background", "#333")
	el.El.Call("scrollIntoView", map[string]any{"inline": "start"})

	return nil
}

func showSonos() {
	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(getYTPlayer() + getTimeline() + getControls() + getVolume() + getQue())

	if err := setEventsYTPlayer(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := setEventsTimeline(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := setEventsControls(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := setEventsVolume(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	syncInfo = SyncInfo{}
	HTTP.Send(syncCallbackSonos, "sonos", "sync")
}

func syncCallbackSonos(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		if strings.HasPrefix(resErr.Error(), "429: ") {
			JS.AfterDelay(5000, func() { HTTP.Send(syncCallbackSonos, "sonos", "sync") })
			return
		}
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	oldSyncInfo := syncInfo
	err := json.Unmarshal(resBytes, &syncInfo)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if syncInfo.Track.Title != oldSyncInfo.Track.Title || syncInfo.Track.Creator != oldSyncInfo.Track.Creator {
		HTTP.Send(ytqueryCallback, "sonos", "yt", syncInfo.Track.Title+" - "+syncInfo.Track.Creator)
	}

	if syncInfo.Que.TotalCount != oldSyncInfo.Que.TotalCount || syncInfo.Shuffle != oldSyncInfo.Shuffle {
		HTTP.Send(queCallback, "sonos", "que", "get")
	} else if syncInfo.Track.QuePosition != oldSyncInfo.Track.QuePosition {
		if err := updatedSelectedQueTrack(strconv.Itoa(oldSyncInfo.Track.QuePosition), strconv.Itoa(syncInfo.Track.QuePosition)); err != nil {
			return
		}
	}

	if err := updateTimeline(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := updateControls(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	if err := updateVolume(); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	JS.AfterDelay(1000, func() { HTTP.Send(syncCallbackSonos, "sonos", "sync") })
}

func ytqueryCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	err := json.Unmarshal(resBytes, &ytInfo)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if err := updateYTPlayer(); err != nil {
		return
	}
}

func queCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil { // Assume no que; for cases when 3th party apps have control of que
		queInfo = QueInfo{Count: "0", TotalCount: "0", Tracks: []QueTrack{}}
	} else {
		err := json.Unmarshal(resBytes, &queInfo)
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
	}

	JS.DBNew(func(db JS.DB, dbErr error) {
		db.GetAllKeys(func(keys []string) {
			imgCacheKeys = keys
			if err := updateQue(); err != nil {
				return
			}
		}, "uris")
	}, "Sonos", []string{"uris"}, SonosDBVersion)
}

func addImgCallback(res string, resBytes []byte, resErr error) {
	if len(toAddImgs) <= 0 {
		return
	} else if resErr != nil {
		if strings.HasPrefix(resErr.Error(), "429: ") {
			JS.AfterDelay(5000, func() { HTTP.Send(addImgCallback, "sonos", "uri", toAddImgs[0][1]) })
		}
		return
	}

	id, uri := toAddImgs[0][0], toAddImgs[0][1]
	toAddImgs = toAddImgs[1:]

	if len(resBytes) == 0 {
		JS.DBNew(func(db JS.DB, dbErr error) {
			db.Set("uris", uri, res)
		}, "Sonos", []string{"uris"}, SonosDBVersion)
	}

	el, err := DOM.GetElement(id)
	if err != nil {
		return
	}
	el.AttributeSet("src", "data:image/png;base64,"+res)

	if len(toAddImgs) <= 0 {
		return
	}

	nextUri := toAddImgs[0][1]
	if slices.Contains(imgCacheKeys, nextUri) {
		JS.DBNew(func(db JS.DB, dbErr error) {
			db.Get(func(value string) {
				JS.Async(func() { addImgCallback(value, []byte{0}, nil) })
			}, "uris", nextUri)
		}, "Sonos", []string{"uris"}, SonosDBVersion)
	} else {
		HTTP.Send(addImgCallback, "sonos", "uri", nextUri)
	}
}

func PageSonos() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("sonos", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showSonos()
		}
	})
}
