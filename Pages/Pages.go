//go:build js && wasm

package Pages

import (
	"WebKit/DOM"
	"WebKit/HTML"
	"WebKit/JS"
	"errors"
	"fmt"
	"syscall/js"
)

var (
	AvailablePages = map[string]func(){
		"Home": PageHome,
	}
	AvailablePagesOrdered = []string{"Home", "TempMovePage", "TempMovePage1", "TempMovePage2", "TempMovePage3", "TempMovePage4"}

	ErrPages = struct {
		ClosingPage error
	}{
		ClosingPage: errors.New("page closing, please rerun after 0.25s"),
	}

	dockerShowing = true
)

func ToggleDocker() error {
	docker, err := DOM.GetElement("docker")
	if err != nil {
		return err
	}

	docker_showhide, err := DOM.GetElement("docker_showhide")
	if err != nil {
		return err
	}

	docker_showhide_img, err := DOM.GetElement("docker_showhide_img")
	if err != nil {
		return err
	}

	buttons, err := DOM.GetElements("docker_buttons")
	if err != nil {
		return err
	}

	if dockerShowing {
		buttons.Disables()
		buttons.StylesSet("opacity", "0")

		docker.StyleSet("max-width", "50px")
		docker.StyleSet("max-height", "48px")
		docker.StyleSet("margin", "-20px 0px 0px -20px")

		docker_showhide.AttributeSet("className", "imgBtn imgBtnSmall")
		docker_showhide.StyleSet("max-width", "42px")
		docker_showhide.StyleSet("max-height", "40px")

		docker_showhide_img.AttributeSet("src", "./docs/assets/General/Show-H.svg")

	} else {
		buttons.Enables()
		buttons.StylesSet("opacity", "1")

		docker.StyleSet("max-width", "250px")
		docker.StyleSet("max-height", "500px")
		docker.StyleSet("margin", "0px")

		docker_showhide.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
		docker_showhide.StyleSet("max-width", "250px")
		docker_showhide.StyleSet("max-height", "500px")

		docker_showhide_img.AttributeSet("src", "./docs/assets/General/Hide-H.svg")
	}

	dockerShowing = !dockerShowing

	return nil
}

func Init() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		body.InnerAddPrefix(HTML.HTML{Tag: "div", Attributes: map[string]string{"id": "mainpage"}, Styles: map[string]string{"overflow-y": "scroll", "max-height": "0vh", "transition": "max-height 0.25s"}}.String())
		mp, err = DOM.GetElement("mainpage")
		if err != nil {
			return err
		}
	}

	if mp.InnerGet() != "" {
		mp.StyleSet("max-height", "0vh")
		JS.AfterDelay(250, func(e js.Value) { mp.InnerClear() })
		return ErrPages.ClosingPage
	}
	mp.StyleSet("max-height", "100vh")

	_, err = DOM.GetElement("docker")
	if err == nil {
		return nil
	}

	dockerStyle := map[string]string{"max-width": "250px", "max-height": "500px", "transition": "max-width 0.25s, max-height 0.25s"}
	img := HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "docker_showhide_img", "src": "./docs/assets/General/Hide-H.svg", "alt": "Fold"}, Styles: dockerStyle}.String()
	items := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "docker_showhide", "class": "imgBtn imgBtnBorder imgBtnSmall"}, Styles: dockerStyle, Inner: img}.String()
	for _, v := range AvailablePagesOrdered {
		items += HTML.HTML{Tag: "button", Attributes: map[string]string{"class": "dark large docker_buttons"}, Styles: map[string]string{"opacity": "1", "transition": "opacity 0.25s"}, Inner: v}.String()
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"position":   "fixed",
			"display":    "grid",
			"max-width":  "250px",
			"max-height": "500px",
			"margin":     "0px",
			"top":        "25px",
			"left":       "25px",
			"border":     "4px solid #111",
			"transition": "max-width 0.25s, max-height 0.25s, margin 0.25s",
			"z-index":    "9999",
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

// If page is already loaded it will return early
func Open(page string) {
	pageEntry, ok := AvailablePages[page]
	if !ok {
		fmt.Println("Page \"" + page + "\" not found!")
		return
	}

	err := Init()
	if err == ErrPages.ClosingPage {
		JS.AfterDelay(250, func(e js.Value) { Open(page) })
		return
	} else if err != nil {
		fmt.Println(err)
		return
	}

	pageEntry()
}
