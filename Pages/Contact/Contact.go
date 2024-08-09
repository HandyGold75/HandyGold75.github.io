//go:build js && wasm

package Contact

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"slices"
)

type (
	contact struct {
		Img  string
		Text string
		Url  string
	}
)

var (
	Contacts = map[int]contact{
		0: {Img: "./docs/assets/Contact/Discord.png", Text: "HandyGold75", Url: "https:discordapp.com/users/296000826588004352"},
		1: {Img: "./docs/assets/Contact/Steam.png", Text: "HandyGold75", Url: "https:steamcommunity.com/id/HandyGold75"},
		2: {Img: "./docs/assets/Contact/YouTube.png", Text: "HandyGold75", Url: "https:youtube.com/@HandyGold75"},
		3: {Img: "./docs/assets/Contact/Twitch.png", Text: "HandyGold75", Url: "https:www.twitch.tv/handygold75"},
		4: {Img: "./docs/assets/Contact/Snapchat.png", Text: "HandyGold75", Url: "https:www.snapchat.com/add/handygold75"},
		5: {Img: "./docs/assets/Contact/Spotify.png", Text: "HandyGold75", Url: "https:open.spotify.com/user/11153222914"},
		6: {Img: "./docs/assets/Contact/Exchange.png", Text: "IZO@HandyGold75.com", Url: "mailto:IZO@HandyGold75.com"},
	}

	headers = []string{}
)

func accessCallback(hasAccess bool, err error) {
	if err != nil {
		showContacts()
		return
	}

	if len(headers) == 0 {
		HTTP.Send(headerCallback, "db-query", "header", "Contact")
		return
	}
	HTTP.Send(dbqueryCallback, "db-query", "read", "Contact")
}

func headerCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		showContacts()
		return
	}

	err := json.Unmarshal(resBytes, &headers)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	HTTP.Send(dbqueryCallback, "db-query", "read", "Contact")
}

func dbqueryCallback(res string, resBytes []byte, resErr error) {
	defer showContacts()
	if resErr != nil {
		return
	}

	remoteContacts := [][]string{}
	err := json.Unmarshal(resBytes, &remoteContacts)
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	for i, record := range remoteContacts {
		if len(record)-1 < slices.Index(headers, "Active") {
			JS.Alert("invalid index for Active")
			continue
		}
		if record[slices.Index(headers, "Active")] != "true" {
			JS.Alert("record not active")
			continue
		}

		imgIndex := slices.Index(headers, "Img")
		if len(record)-1 < imgIndex {
			JS.Alert("invalid index for Img")
			continue
		}
		textIndex := slices.Index(headers, "Text")
		if len(record)-1 < textIndex {
			JS.Alert("invalid index for Text")
			continue
		}
		urlIndex := slices.Index(headers, "Url")
		if len(record)-1 < urlIndex {
			JS.Alert("invalid index for Url")
			continue
		}

		Contacts[i] = contact{
			Img:  record[imgIndex],
			Text: record[textIndex],
			Url:  record[urlIndex],
		}
	}
}

func showContacts() {
	header := HTML.HTML{Tag: "h1", Inner: "Contact"}.String()

	contactKeys := []int{}
	for k := range Contacts {
		contactKeys = append(contactKeys, k)
	}
	slices.Sort(contactKeys)

	contactDivs := ""
	for i, k := range contactKeys {
		marginDiv := "5px -100vw 5px auto"
		classImg := "contact_imgInsides"
		classTxt := ""
		marginImg := "0px 10px 0px 100%"
		marginTxt := "auto auto auto 10px"
		if i%2 == 0 {
			marginDiv = "5px auto 5px -100vw"
			classImg = ""
			classTxt = "contact_txtInsides"
			marginImg = "0px 10px 0px auto"
			marginTxt = "auto 100% auto 10px"
		}

		img := HTML.HTML{Tag: "a",
			Attributes: map[string]string{"class": classImg, "href": Contacts[k].Url, "target": "_blank"},
			Styles:     map[string]string{"width": "10vh", "height": "10vh", "margin": marginImg, "transition": "margin 1s"},
			Inner: HTML.HTML{Tag: "img",
				Attributes: map[string]string{"src": Contacts[k].Img, "alt": Contacts[k].Text},
				Styles:     map[string]string{"width": "10vh", "height": "10vh"},
			}.String(),
		}.String()

		txt := HTML.HTML{Tag: "a",
			Attributes: map[string]string{"class": classTxt, "href": Contacts[k].Url, "target": "_blank"},
			Styles:     map[string]string{"font-size": "3vh", "margin": marginTxt, "transition": "margin 1s"},
			Inner:      Contacts[k].Text,
		}.String()

		contactDivs += HTML.HTML{Tag: "div",
			Attributes: map[string]string{"class": "contact_divs"},
			Styles:     map[string]string{"display": "flex", "width": "85%", "margin": marginDiv, "background": "#1F1F1F", "border": "4px solid #111", "transition": "margin 1s"},
			Inner:      img + txt,
		}.String()
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	mp.InnerSet(header + contactDivs)

	els, err := DOM.GetElements("contact_divs")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		curEl := els.Els.Index(i)
		if i%2 == 0 {
			JS.AfterDelay((i+1)*500, func() { curEl.Get("style").Set("margin-left", "-2vw") })
			continue
		}
		JS.AfterDelay((i+1)*500, func() { curEl.Get("style").Set("margin-right", "-2vw") })
	}

	els, err = DOM.GetElements("contact_txtInsides")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		curEl := els.Els.Index(i)
		JS.AfterDelay(((i+1)*1000)-500, func() { curEl.Get("style").Set("margin-right", "10%") })
	}

	els, err = DOM.GetElements("contact_imgInsides")
	if err != nil {
		JS.Alert(err.Error())
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		curEl := els.Els.Index(i)
		JS.AfterDelay((i+1)*1000, func() { curEl.Get("style").Set("margin-left", "10%") })
	}
}

func Page(forcePage func(string), setLoginSuccessCallback func(func())) {
	if !HTTP.IsMaybeAuthenticated() {
		showContacts()
		return
	}

	HTTP.HasAccessTo(accessCallback, "db-query")
}
