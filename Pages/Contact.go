//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"fmt"
	"strings"
)

type (
	contact struct {
		IMG  string
		Text string
		URL  string
	}
)

var (
	Contacts = []contact{
		{IMG: "./docs/assets/Contact/Discord.png", Text: "HandyGold75", URL: "https:discordapp.com/users/296000826588004352"},
		{IMG: "./docs/assets/Contact/Steam.png", Text: "HandyGold75", URL: "https:steamcommunity.com/id/HandyGold75"},
		{IMG: "./docs/assets/Contact/YouTube.png", Text: "HandyGold75", URL: "https:youtube.com/@HandyGold75"},
		{IMG: "./docs/assets/Contact/Twitch.png", Text: "HandyGold75", URL: "https:www.twitch.tv/handygold75"},
		{IMG: "./docs/assets/Contact/Snapchat.png", Text: "HandyGold75", URL: "https:www.snapchat.com/add/handygold75"},
		{IMG: "./docs/assets/Contact/Spotify.png", Text: "HandyGold75", URL: "https:open.spotify.com/user/11153222914"},
		{IMG: "./docs/assets/Contact/Exchange.png", Text: "IZO@HandyGold75.com", URL: "mailto:IZO@HandyGold75.com"},
	}
)

func PageContact() {
	header := HTML.HTML{Tag: "h1", Inner: "Contact"}.String()

	contactDivs := ""
	for i, con := range Contacts {
		splitIMG := strings.Split(con.IMG, "/")

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

		img := HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"class": classImg, "src": con.IMG, "alt": strings.Replace(splitIMG[len(splitIMG)-1], ".png", "", 1), "href": con.URL, "target": "_blank"},
			Styles:     map[string]string{"width": "10vw", "height": "10vw", "margin": marginImg, "transition": "margin 1s"},
		}.ApplyTemplate(HTML.HTML_Link).String()

		txt := HTML.HTML{Inner: con.Text, Attributes: map[string]string{"class": classTxt}, Styles: map[string]string{"font-size": "3vw", "margin": marginTxt, "transition": "margin 1s"}}.ApplyTemplate(HTML.HTML_Link).String()

		contactDivs = HTML.HTML{Tag: "div",
			Attributes: map[string]string{"class": "contact_divs"},
			Styles:     map[string]string{"display": "flex", "width": "85%", "margin": marginDiv, "background": "#1F1F1F", "border": "4px solid #111", "transition": "margin 1s"},
			Inner:      img + txt,
			Prefix:     contactDivs,
		}.String()

	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + contactDivs)

	els, err := DOM.GetElements("contact_divs")
	if err != nil {
		fmt.Println(err)
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
		fmt.Println(err)
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		curEl := els.Els.Index(i)
		JS.AfterDelay(((i+1)*1000)-500, func() { curEl.Get("style").Set("margin-right", "10%") })
	}

	els, err = DOM.GetElements("contact_imgInsides")
	if err != nil {
		fmt.Println(err)
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		curEl := els.Els.Index(i)
		JS.AfterDelay((i+1)*1000, func() { curEl.Get("style").Set("margin-left", "10%") })
	}
}
