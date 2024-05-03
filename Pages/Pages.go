//go:build js && wasm

package Pages

import (
	"WebKit/DOM"
	"WebKit/HTML"
	"fmt"
	"syscall/js"
)

var (
	AvailablePages = map[string]func(){
		"Home": PageHome,
	}

	AvailablePagesOrdered = []string{"Home", "TempMovePage", "TempMovePage1", "TempMovePage2", "TempMovePage3", "TempMovePage4"}
)

func ToggleDocker() error {
	els, err := DOM.GetElements("docker_buttons")
	if err != nil {
		return err
	}
	els.Disables()

	return nil
}

func Init() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		body.InnerAddPrefix(HTML.HTML{Tag: "div", Attributes: map[string]string{"id": "mainpage"}}.String())
		mp, err = DOM.GetElement("mainpage")
		if err != nil {
			return err
		}
	}
	mp.InnerClear()

	_, err = DOM.GetElement("docker")
	if err == nil {
		return nil
	}

	items := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "docker_showhide", "class": "imgBtn imgBtnSmall"}, Inner: HTML.HTML{Tag: "img", Attributes: map[string]string{"src": "./docs/assets/General/Hide-H.svg", "alt": "Fold"}}.String()}.String()
	for _, v := range AvailablePagesOrdered {
		items += HTML.HTML{Tag: "button", Attributes: map[string]string{"class": "dark large docker_buttons"}, Styles: map[string]string{"max-width": "100%", "transition": "max-width 0.25s"}, Inner: v}.String()
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"position": "fixed",
			"display":  "grid",
			"top":      "25px",
			"left":     "25px",
			"border":   "4px solid #111",
			"z-index":  "9999",
		},
		Attributes: map[string]string{"id": "docker"},
		Inner:      items,
	}.String())

	el, err := DOM.GetElement("docker_showhide")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(event js.Value) { ToggleDocker() })

	els, err := DOM.GetElements("docker_buttons")
	if err != nil {
		return err
	}
	els.EventsAdd("click", func(event js.Value) { Open(event.Get("innerHTML").String()) })

	return nil
}

func Open(page string) {
	pageEntry, ok := AvailablePages[page]
	if !ok {
		fmt.Println("Page \"" + page + "\" not found!")
		return
	}

	err := Init()
	if err != nil {
		fmt.Println(err)
		return
	}

	pageEntry()
}
