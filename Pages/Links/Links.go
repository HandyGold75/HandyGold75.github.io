//go:build js && wasm

package Links

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"slices"
	"strconv"
	"strings"
)

type (
	link struct {
		Img  string
		Text string
		Url  string
		Cat  string
	}
)

var (
	Links = map[int]link{
		1:  {Img: "./docs/assets/Links/Outlook.png", Text: "Outlook", Url: "https://outlook.office.com/", Cat: "Microsoft/ Google"},
		2:  {Img: "./docs/assets/Links/OutlookCalendar.png", Text: "Outlook Calendar", Url: "https://outlook.office.com/calendar/", Cat: "Microsoft/ Google"},
		3:  {Img: "./docs/assets/Links/OneDrive.png", Text: "OneDrive", Url: "https://www.office.com/login?ru=%2Flaunch%2Fonedrive", Cat: "Microsoft/ Google"},
		4:  {Img: "./docs/assets/Links/M365.png", Text: "Microsoft 365", Url: "https://www.microsoft365.com/", Cat: "Microsoft/ Google"},
		5:  {Img: "./docs/assets/Links/G-Mail.png", Text: "Google Mail", Url: "https://mail.google.com/", Cat: "Microsoft/ Google"},
		6:  {Img: "./docs/assets/Links/G-Drive.png", Text: "Google Drive", Url: "https://drive.google.com/", Cat: "Microsoft/ Google"},
		7:  {Img: "./docs/assets/Links/G-Photos.png", Text: "Google Photos", Url: "https://photos.google.com/", Cat: "Microsoft/ Google"},
		8:  {Img: "./docs/assets/Links/G-Calendar.png", Text: "Google Calendar", Url: "https://calendar.google.com/", Cat: "Microsoft/ Google"},
		9:  {Img: "./docs/assets/Links/YouTube.png", Text: "YouTube", Url: "https://www.youtube.com/", Cat: "Media"},
		10: {Img: "./docs/assets/Links/YouTubeMusic.png", Text: "YouTube Music", Url: "https://music.youtube.com/", Cat: "Media"},
		11: {Img: "./docs/assets/Links/Spotify.png", Text: "Spotify", Url: "https://open.spotify.com/", Cat: "Media"},
		12: {Img: "./docs/assets/Links/OneTimeSecret.png", Text: "One Time Secret", Url: "https://onetimesecret.com/", Cat: "Tools"},
		13: {Img: "./docs/assets/Links/SpeedTest.png", Text: "SpeedTest Ookla", Url: "https://www.speedtest.net/", Cat: "Tools"},
		14: {Img: "./docs/assets/Links/DownDetector.png", Text: "Down Detector", Url: "https://downdetector.com/", Cat: "Tools"},
		15: {Img: "./docs/assets/Links/CloudConvert.png", Text: "Cloud Convert", Url: "https://cloudconvert.com/", Cat: "Tools"},
	}

	colCount = 5

	headers = []string{}
)

func accessCallback(hasAccess bool, err error) {
	if err != nil || !hasAccess {
		updateCols()
		return
	}

	if len(headers) == 0 {
		HTTP.Send(headerCallback, "db-query", "header", "Links")
		return
	}
	HTTP.Send(dbqueryCallback, "db-query", "read", "Links")
}

func headerCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		updateCols()
		return
	}

	err := json.Unmarshal(resBytes, &headers)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	HTTP.Send(dbqueryCallback, "db-query", "read", "Links")
}

func dbqueryCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		updateCols()
		return
	}

	remoteLinks := [][]string{}
	err := json.Unmarshal(resBytes, &remoteLinks)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	for i, record := range remoteLinks {
		if len(record)-1 < slices.Index(headers, "Active") {
			Widget.PopupAlert("Error", "invalid index for Active", func() {})
			continue
		}
		if record[slices.Index(headers, "Active")] != "true" {
			Widget.PopupAlert("Error", "record not active", func() {})
			continue
		}

		imgIndex := slices.Index(headers, "Img")
		if len(record)-1 < imgIndex {
			Widget.PopupAlert("Error", "invalid index for Img", func() {})
			continue
		}
		textIndex := slices.Index(headers, "Text")
		if len(record)-1 < textIndex {
			Widget.PopupAlert("Error", "invalid index for Text", func() {})
			continue
		}
		urlIndex := slices.Index(headers, "Url")
		if len(record)-1 < urlIndex {
			Widget.PopupAlert("Error", "invalid index for Url", func() {})
			continue
		}
		catIndex := slices.Index(headers, "Cat")
		if len(record)-1 < urlIndex {
			Widget.PopupAlert("Error", "invalid index for Cat", func() {})
			continue
		}

		Links[i] = link{
			Img:  record[imgIndex],
			Text: record[textIndex],
			Url:  record[urlIndex],
			Cat:  record[catIndex],
		}
	}

	updateCols()
}

func updateCols() {
	showLinks()
	JS.OnResizeAdd("links", func() {
		if _, err := DOM.GetElements("cat_divs"); err != nil {
			JS.OnResizeDelete("links")
		}

		oldColCount := colCount
		vp := JS.GetVP()
		if vp[1] < 300 {
			colCount = 3
		} else if vp[1] < 600 {
			colCount = 4
		} else if vp[1] < 900 {
			colCount = 5
		} else {
			colCount = 6
		}

		if oldColCount != colCount {
			showLinks()
		}
	})
}

func showLinks() {
	header := HTML.HTML{Tag: "h1", Inner: "Link"}.String()

	linkKeys := []int{}
	for k := range Links {
		linkKeys = append(linkKeys, k)
	}
	slices.Sort(linkKeys)

	linkByCat := map[string][]link{}
	for _, k := range linkKeys {
		if _, ok := linkByCat[Links[k].Cat]; !ok {
			linkByCat[Links[k].Cat] = []link{Links[k]}
			continue
		}
		linkByCat[Links[k].Cat] = append(linkByCat[Links[k].Cat], Links[k])
	}

	catDivs := ""
	for cat, links := range linkByCat {
		catDivs += HTML.HTML{Tag: "h2",
			Inner:  cat,
			Styles: map[string]string{"margin": "0px 5%"},
		}.String()

		catDiv := ""
		linkDivs := ""
		for i, l := range links {
			img := HTML.HTML{Tag: "img",
				Attributes: map[string]string{"src": l.Img, "alt": l.Text},
				Styles:     map[string]string{"width": "100%"},
			}.LinkWrap(l.Url).String()

			txt := HTML.HTML{Tag: "p",
				Styles: map[string]string{"width": "100%"},
				Inner: HTML.HTML{Tag: "a",
					Attributes: map[string]string{"href": l.Url, "target": "_blank"},
					Inner:      l.Text,
				}.String(),
			}.String()

			linkDivs += HTML.HTML{Tag: "div", Inner: img + txt}.String()

			if (i+1)%colCount == 0 {
				catDiv += HTML.HTML{Tag: "div",
					Attributes: map[string]string{},
					Styles:     map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", colCount)},
					Inner:      linkDivs,
				}.String()
				linkDivs = ""
			}
		}

		if linkDivs != "" {
			catDiv += HTML.HTML{Tag: "div",
				Attributes: map[string]string{},
				Styles:     map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", strings.Count(linkDivs, "<img "))},
				Inner:      linkDivs,
			}.String()
		}

		catDivs += HTML.HTML{Tag: "div",
			Attributes: map[string]string{"class": "cat_divs"},
			Inner:      catDiv,
		}.String()
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + catDivs)
}

func Page(forcePage func(string), setLoginSuccessCallback func(func())) {
	if !HTTP.IsMaybeAuthenticated() {
		updateCols()
		return
	}

	HTTP.HasAccessTo(accessCallback, "db-query")
}
