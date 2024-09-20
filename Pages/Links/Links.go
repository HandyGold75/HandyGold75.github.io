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
	"syscall/js"
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
		1:  {Img: "Outlook.png", Text: "Outlook", Url: "https://outlook.office.com/", Cat: "Microsoft/ Google"},
		2:  {Img: "OutlookCalendar.png", Text: "Outlook Calendar", Url: "https://outlook.office.com/calendar/", Cat: "Microsoft/ Google"},
		3:  {Img: "OneDrive.png", Text: "OneDrive", Url: "https://www.office.com/login?ru=%2Flaunch%2Fonedrive", Cat: "Microsoft/ Google"},
		4:  {Img: "M365.png", Text: "Microsoft 365", Url: "https://www.microsoft365.com/", Cat: "Microsoft/ Google"},
		5:  {Img: "G-Mail.png", Text: "Google Mail", Url: "https://mail.google.com/", Cat: "Microsoft/ Google"},
		6:  {Img: "G-Drive.png", Text: "Google Drive", Url: "https://drive.google.com/", Cat: "Microsoft/ Google"},
		7:  {Img: "G-Photos.png", Text: "Google Photos", Url: "https://photos.google.com/", Cat: "Microsoft/ Google"},
		8:  {Img: "G-Calendar.png", Text: "Google Calendar", Url: "https://calendar.google.com/", Cat: "Microsoft/ Google"},
		9:  {Img: "YouTube.png", Text: "YouTube", Url: "https://www.youtube.com/", Cat: "Media"},
		10: {Img: "YouTubeMusic.png", Text: "YouTube Music", Url: "https://music.youtube.com/", Cat: "Media"},
		11: {Img: "Spotify.png", Text: "Spotify", Url: "https://open.spotify.com/", Cat: "Media"},
		12: {Img: "OneTimeSecret.png", Text: "One Time Secret", Url: "https://onetimesecret.com/", Cat: "Tools"},
		13: {Img: "SpeedTest.png", Text: "SpeedTest Ookla", Url: "https://www.speedtest.net/", Cat: "Tools"},
		14: {Img: "DownDetector.png", Text: "Down Detector", Url: "https://downdetector.com/", Cat: "Tools"},
		15: {Img: "CloudConvert.png", Text: "Cloud Convert", Url: "https://cloudconvert.com/", Cat: "Tools"},
	}

	colCount  = 5
	firstLoad = true

	headers = []string{}
)

func toggleFold(el js.Value, evs []js.Value) {
	idSplit := strings.Split(el.Get("id").String(), "_")
	id := idSplit[len(idSplit)-1]

	elsDivs, err := DOM.GetElements("cat_divs_" + id)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	folded := strings.Split(JS.CacheGet("Page/Links"), ";")
	if slices.Contains(folded, id) {
		folded = slices.DeleteFunc(folded, func(item string) bool {
			if item == id {
				return true
			}
			return false
		})
		for _, divId := range elsDivs.AttributesGet("id") {
			if err := Widget.AnimateStyle(divId, "max-height", "0px", "300px", 250); err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
			}
		}
	} else {
		folded = append(folded, id)
		for _, divId := range elsDivs.AttributesGet("id") {
			if err := Widget.AnimateStyle(divId, "max-height", "300px", "0px", 250); err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
			}
		}
	}

	JS.CacheSet("Page/Links", strings.Join(folded, ";"))
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
	header := HTML.HTML{Tag: "h1", Inner: "Link", Attributes: map[string]string{"id": "links_header"}}.String()
	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header)

	colCount = -1
	JS.OnResizeAdd("links", func() {
		if _, err := DOM.GetElement("links_header"); err != nil {
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
	header := HTML.HTML{Tag: "h1", Inner: "Link", Attributes: map[string]string{"id": "links_header"}}.String()

	linkIndexes := []int{}
	for k := range Links {
		linkIndexes = append(linkIndexes, k)
	}
	slices.Sort(linkIndexes)

	catsIndexes := []string{}
	cats := map[string][]string{}

	for _, i := range linkIndexes {
		l := Links[i]

		if !slices.Contains(catsIndexes, l.Cat) {
			catsIndexes = append(catsIndexes, l.Cat)
			cats[l.Cat] = []string{}
		}

		img := HTML.HTML{Tag: "img",
			Attributes: map[string]string{"src": "./docs/assets/Links/" + l.Img, "alt": l.Text},
			Styles:     map[string]string{"width": "100%"},
		}.LinkWrap(l.Url).String()
		txt := HTML.HTML{Tag: "p",
			Styles: map[string]string{"width": "100%"},
			Inner: HTML.HTML{Tag: "a",
				Attributes: map[string]string{"href": l.Url, "target": "_blank"},
				Inner:      l.Text,
			}.String(),
		}.String()
		link := HTML.HTML{Tag: "div", Inner: img + txt}.String()

		cats[l.Cat] = append(cats[l.Cat], link)
	}

	ids := []string{}
	divs := ""
	for _, cat := range catsIndexes {
		title := HTML.HTML{Tag: "h2", Inner: cat,
			Attributes: map[string]string{"id": "cat_headers_" + cat},
		}.String()

		rows := ""
		links := ""
		for i, link := range cats[cat] {
			links += link
			if (i+1)%colCount != 0 {
				continue
			}

			style := map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", colCount)}
			if firstLoad {
				style = map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", colCount), "max-height": "0px"}
			}

			ids = append(ids, "cat_divs_"+cat+"_"+strconv.Itoa(i))
			rows += HTML.HTML{Tag: "div", Inner: links,
				Attributes: map[string]string{"id": "cat_divs_" + cat + "_" + strconv.Itoa(i), "class": "cat_divs_" + cat},
				Styles:     style,
			}.String()
			links = ""
		}

		if links != "" {
			style := map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", strings.Count(links, "<img "))}
			if firstLoad {
				style = map[string]string{"display": "grid", "justify-content": "space-evenly", "grid-template-columns": strings.Repeat(strconv.FormatFloat((100/float64(colCount))-10, 'f', -1, 64)+"% ", strings.Count(links, "<img ")), "max-height": "0px"}
			}

			ids = append(ids, "cat_divs_"+cat+"_etc")
			rows += HTML.HTML{Tag: "div", Inner: links,
				Attributes: map[string]string{"id": "cat_divs_" + cat + "_etc", "class": "cat_divs_" + cat},
				Styles:     style,
			}.String()
		}

		divs += HTML.HTML{Tag: "div", Inner: title + rows}.String()
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + divs)

	for _, cat := range catsIndexes {
		el, err := DOM.GetElement("cat_headers_" + cat)
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		el.EventAdd("click", toggleFold)
	}

	if !firstLoad {
		return
	}
	firstLoad = false

	folded := strings.Split(JS.CacheGet("Page/Links"), ";")
	i := 0
	for _, id := range ids {
		if slices.Contains(folded, strings.Split(id, "_")[2]) {
			continue
		}
		JS.AfterDelay(i*250, func() {
			if err := Widget.AnimateStyle(id, "max-height", "0px", "300px", 250); err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
			}
		})
		i++
	}
}

func Page() {
	firstLoad = true

	if !HTTP.IsMaybeAuthenticated() {
		updateCols()
		return
	}
	HTTP.HasAccessTo("db-query", func(hasAccess bool, err error) {
		if err != nil || !hasAccess {
			updateCols()
		} else if len(headers) == 0 {
			HTTP.Send(headerCallback, "db-query", "header", "Links")
		} else {
			HTTP.Send(dbqueryCallback, "db-query", "read", "Links")
		}
	})
}
