//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"
	"fmt"
	"strings"
	"syscall/js"
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

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}

	contactDivs := ""
	for i, con := range Contacts {
		splitIMG := strings.Split(con.IMG, "/")

		img := HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"src": con.IMG, "alt": strings.Replace(splitIMG[len(splitIMG)-1], ".png", "", 1), "href": con.URL, "target": "_blank"},
			Styles:     map[string]string{"width": "50px", "height": "50px"},
		}.ApplyTemplate(HTML.HTML_Link).String()

		txt := HTML.HTML{Inner: con.Text, Styles: map[string]string{"margin": "auto 10px"}}.ApplyTemplate(HTML.HTML_Link).String()

		marginStyle := "5px -100vw 5px auto"
		if i%2 == 0 {
			marginStyle = "5px auto 5px -100vw"
		}

		contactDivs = HTML.HTML{Tag: "div",
			Attributes: map[string]string{"class": "contact_divs"},
			Styles:     map[string]string{"display": "flex", "width": "85%", "margin": marginStyle, "border": "4px solid #111", "transition": "margin 0.5s"},
			Inner:      img + txt,
			Prefix:     contactDivs,
		}.String()

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
			JS.AfterDelay(i*500, func(event js.Value) { curEl.Get("style").Set("margin", "5px 0vw 5px auto") })
			continue
		}
		JS.AfterDelay(i*500, func(event js.Value) { curEl.Get("style").Set("margin", "5px auto 5px 0vw") })
	}
}
