//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"fmt"
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
		{IMG: "Discord.png", Text: "HandyGold75", URL: "https:discordapp.com/users/296000826588004352"},
		{IMG: "Steam.png", Text: "HandyGold75", URL: "https:steamcommunity.com/id/HandyGold75"},
		{IMG: "YouTube.png", Text: "HandyGold75", URL: "https:youtube.com/@HandyGold75"},
		{IMG: "Twitch.png", Text: "HandyGold75", URL: "https:www.twitch.tv/handygold75"},
		{IMG: "Snapchat.png", Text: "HandyGold75", URL: "https:www.snapchat.com/add/handygold75"},
		{IMG: "Spotify.png", Text: "HandyGold75", URL: "https:open.spotify.com/user/11153222914"},
		{IMG: "Exchange.png", Text: "IZO@HandyGold75.com", URL: "mailto:IZO@HandyGold75.com"},
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

		img := HTML.HTML{}.String()
		txt := HTML.HTML{Inner: con.Text}.ApplyTemplate(HTML.HTML_Link).String()

		marginStyle := "5px 5px 5px auto"
		if i%2 == 0 {
			marginStyle = "5px auto 5px 5px"
		}

		contactDivs = HTML.HTML{Tag: "div",
			Attributes: map[string]string{},
			Styles:     map[string]string{"display": "flex", "width": "85%", "margin": marginStyle, "border": "4p solid #222", "transition": "margin 0.5s"},
			Inner:      img + txt,
			Surfix:     contactDivs,
		}.String()
	}

	mp.InnerSet(header + contactDivs)

}
