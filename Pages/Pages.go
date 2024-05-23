//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/JS"

	"errors"
	"fmt"
	"syscall/js"
)

var (
	AvailablePages = map[string]func(){
		"Home":    PageHome,
		"Contact": PageContact,
	}
	AvailablePagesOrdered = []string{"Home", "Contact"}

	ErrPages = struct {
		ErrPagesClosingPage error
	}{
		ErrPagesClosingPage: errors.New("page closing, please skip page load"),
	}

	dockerShowing = true
	inTransition  = false
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

func InitMainpage() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div", Attributes: map[string]string{"id": "mainpage"}, Styles: map[string]string{"transition": "max-height 0.25s"}}.String())

	return nil
}

func InitDocker() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
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
	els.EventsAdd("click", func(event js.Value) {
		ToggleDocker()
		Open(event.Get("innerHTML").String())
	})

	return nil
}

func InitFooter() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	txt := HTML.HTML{Tag: "p", Styles: map[string]string{"font-wight": "bold", "margin": "auto auto auto 0px"}, Attributes: map[string]string{"class": "light"}, Inner: "HandyGold75 - 2022 / 2024"}.String()

	btnBackToTop := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_backtotop", "class": "small light"}, Inner: "Back to top"}.String()
	btnClearCache := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_clearcache", "class": "small light"}, Inner: "Clear cache"}.String()

	body.InnerAddSurfix(HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"display":    "flex",
			"margin-top": "10px",
			"padding":    "0px 10px",
		},
		Attributes: map[string]string{"id": "footer", "class": "light"},
		Inner:      txt + btnBackToTop + btnClearCache,
	}.String())

	el, err := DOM.GetElement("footer_backtotop")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(event js.Value) {
		if body, err := DOM.GetElement("body"); err != nil {
			body.Call("scrollIntoView")
		}
	})

	els, err := DOM.GetElement("footer_clearcache")
	if err != nil {
		return err
	}
	els.EventAdd("click", func(event js.Value) { JS.CacheClear() })

	return nil
}

func Init(onDeloadedCallback func()) error {
	if _, err := DOM.GetElement("docker"); err != nil {
		if err := InitDocker(); err != nil {
			return err
		}
	}

	if _, err := DOM.GetElement("mainpage"); err != nil {
		if err := InitMainpage(); err != nil {
			return err
		}
	}

	if _, err := DOM.GetElement("footer"); err != nil {
		if err := InitFooter(); err != nil {
			return err
		}
	}

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		return err
	}

	if mp.InnerGet() != "" {
		inTransition = true
		mp.StyleSet("max-height", "100vh")
		JS.Async(func(event js.Value) { mp.StyleSet("max-height", "0vh") })
		JS.AfterDelay(250, func(event js.Value) {
			mp.InnerSet("")
			Init(onDeloadedCallback)
		})
		return nil

	} else {
		mp.StyleSet("max-height", "100vh")
		JS.AfterDelay(250, func(event js.Value) {
			mp.StyleSet("max-height", "")
			inTransition = false
		})
	}

	onDeloadedCallback()
	return nil
}

func Open(page string) {
	if inTransition {
		return
	}

	pageEntry, ok := AvailablePages[page]
	if !ok {
		fmt.Println("Page \"" + page + "\" not found!")
		return
	}

	err := Init(pageEntry)
	if err != nil {
		fmt.Println(err)
		return
	}
}
