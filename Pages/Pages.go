//go:build js && wasm

package Pages

import (
	"HandyGold75/Pages/Admin"
	"HandyGold75/Pages/Console"
	"HandyGold75/Pages/Contact"
	"HandyGold75/Pages/Home"
	"HandyGold75/Pages/Links"
	"HandyGold75/Pages/Login"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"errors"
	"fmt"
	"strings"
	"syscall/js"
)

var (
	AvailablePages           = map[string]func(func(string), func(func())){}
	AvailablePagesOrdered    = []string{"Home", "Links", "Contact", "Console", "sub:Admin"}
	AvailableSubPagesOrdered = []string{"Admin:Users", "Admin:Config", "Admin:Logs"}

	ErrPages = struct {
		ErrPagesClosingPage error
	}{
		ErrPagesClosingPage: errors.New("page closing, please skip page load"),
	}

	dockerShowing = true
	inTransition  = false
)

func ToggleDocker() error {
	buttons, err := DOM.GetElements("docker_buttons")
	if err != nil {
		return err
	}

	titles, err := DOM.GetElements("docker_titles")
	if err != nil {
		return err
	}

	subs, err := DOM.GetElements("docker_subs")
	if err != nil {
		return err
	}

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

	if dockerShowing {
		buttons.Disables()
		buttons.StylesSet("opacity", "0")

		titles.StylesSet("color", "#88b")
		titles.StylesSet("opacity", "0")

		subs.StylesSet("opacity", "0")

		docker.StyleSet("max-width", "50px")
		docker.StyleSet("max-height", "48px")
		docker.StyleSet("margin", "-20px 0px 0px -20px")

		docker_showhide.AttributeSet("className", "imgBtn imgBtnSmall")
		docker_showhide.StyleSet("max-width", "42px")

		docker_showhide_img.AttributeSet("src", "./docs/assets/General/Show-H.svg")

	} else {
		buttons.Enables()
		buttons.StylesSet("opacity", "1")

		titles.StylesSet("opacity", "1")
		titles.StylesSet("color", "#bff")

		subs.StylesSet("opacity", "1")

		docker.StyleSet("max-width", "250px")
		docker.StyleSet("max-height", "1000px")
		docker.StyleSet("margin", "0px")

		docker_showhide.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
		docker_showhide.StyleSet("max-width", "250px")

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

	items := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "docker_showhide", "class": "imgBtn imgBtnBorder imgBtnSmall"},
		Styles:     map[string]string{"max-width": "250px"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"id": "docker_showhide_img", "src": "./docs/assets/General/Hide-H.svg", "alt": "Fold"},
			Styles:     map[string]string{"max-width": "250px"},
		}.String(),
	}.String()

	for _, page := range AvailablePagesOrdered {
		if strings.HasPrefix(page, "sub:") {
			subPages := HTML.HTML{Tag: "p",
				Attributes: map[string]string{"class": "docker_titles"},
				Styles:     map[string]string{"color": "#bff", "font-size": "125%", "transition": "opacity 0.25s"},
				Inner:      strings.Replace(page, "sub:", "", 1),
			}.String()

			for _, subPage := range AvailableSubPagesOrdered {
				if strings.Replace(page, "sub:", "", 1) == strings.Split(subPage, ":")[0] {
					subPages += HTML.HTML{Tag: "button",
						Attributes: map[string]string{"id": "page_" + subPage, "class": "dark large docker_buttons"},
						Styles:     map[string]string{"opacity": "1"},
						Inner:      strings.Split(subPage, ":")[1],
					}.String()
				}
			}

			items += HTML.HTML{Tag: "div",
				Attributes: map[string]string{"class": "docker_subs"},
				Styles: map[string]string{
					"display":       "grid",
					"max-height":    "2.4em",
					"margin":        "4px 6px",
					"padding":       "4px 6px 4px 3px",
					"border-left":   "3px solid #55f",
					"border-radius": "0px",
					"opacity":       "1",
					"transition":    "max-height 0.25s, opacity 0.25s",
				},
				Inner: subPages,
			}.String()

			continue
		}

		items += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"id": "page_" + page, "class": "dark large docker_buttons"},
			Styles:     map[string]string{"opacity": "1"},
			Inner:      page,
		}.String()
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "docker"},
		Styles: map[string]string{
			"position":   "fixed",
			"display":    "grid",
			"max-width":  "250px",
			"max-height": "1000px",
			"margin":     "0px",
			"top":        "25px",
			"left":       "25px",
			"border":     "4px solid #111",
			"transition": "max-width 0.25s, max-height 0.25s, margin 0.25s",
			"z-index":    "9999",
		},
		Inner: items,
	}.String())

	el, err := DOM.GetElement("docker_showhide")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) { ToggleDocker() })

	els, err := DOM.GetElements("docker_buttons")
	if err != nil {
		return err
	}
	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		ToggleDocker()
		Open(strings.Replace(el.Get("id").String(), "page_", "", 1))
	})

	els, err = DOM.GetElements("docker_subs")
	if err != nil {
		return err
	}
	els.EventsAdd("mouseover", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "25em") })
	els.EventsAdd("mouseout", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "2.4em") })

	return nil
}

func InitFooter() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	txt := HTML.HTML{Tag: "p", Styles: map[string]string{"font-weight": "bold", "margin": "auto auto auto 0px"}, Attributes: map[string]string{"class": "light"}, Inner: "HandyGold75 - 2022 / 2024"}.String()

	btnBackToTop := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_backtotop", "class": "small light"}, Inner: "Back to top"}.String()
	btnLogout := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_logout", "class": "small light"}, Inner: "Logout"}.String()
	btnClearCache := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_clearcache", "class": "small light"}, Inner: "Clear cache"}.String()

	body.InnerAddSurfix(HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"display":    "flex",
			"margin-top": "10px",
			"padding":    "0px 10px",
		},
		Attributes: map[string]string{"id": "footer", "class": "light"},
		Inner:      txt + btnBackToTop + btnLogout + btnClearCache,
	}.String())

	el, err := DOM.GetElement("footer_backtotop")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) { JS.ScrollToTop() })

	el, err = DOM.GetElement("footer_logout")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Config.Set("token", "")
		HTTP.UnauthorizedCallback()
	})

	els, err := DOM.GetElement("footer_clearcache")
	if err != nil {
		return err
	}
	els.EventAdd("click", func(el js.Value, evs []js.Value) {
		JS.CacheClear()
		HTTP.Config.Load()
		JS.Async(func() { ForcePage("Home") })
	})

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
		JS.Async(func() { mp.StyleSet("max-height", "0vh") })
		JS.AfterDelay(250, func() {
			mp.InnerSet("")
			Init(onDeloadedCallback)
		})
		return nil

	} else {
		mp.StyleSet("max-height", "100vh")
		JS.AfterDelay(250, func() {
			mp.StyleSet("max-height", "")
			inTransition = false
		})
	}

	onDeloadedCallback()
	return nil
}

func SetOnLoginSuccess(f func()) {
	Login.OnLoginSuccessCallback = f
}

func ForcePage(page string) {
	AvailablePages = map[string]func(func(string), func(func())){
		"Home":         Home.Page,
		"Links":        Links.Page,
		"Contact":      Contact.Page,
		"Console":      Console.Page,
		"Admin:Users":  Admin.PageUsers,
		"Admin:Config": Admin.PageConfig,
		"Admin:Logs":   Admin.PageLogs,
		"Login":        Login.Page,
	}

	pageEntry, ok := AvailablePages[page]
	if !ok {
		fmt.Println("Page \"" + page + "\" not found!")
		pageEntry = AvailablePages[AvailablePagesOrdered[0]]
	}

	err := Init(func() { pageEntry(ForcePage, SetOnLoginSuccess) })
	if err != nil {
		fmt.Println(err)
		return
	}

	JS.CacheSet("mainPage", page)
}

func Open(page string) {
	if inTransition {
		return
	}
	ForcePage(page)
}
