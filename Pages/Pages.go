//go:build js && wasm

package Pages

import (
	"HandyGold75/Pages/Admin"
	"HandyGold75/Pages/Console"
	"HandyGold75/Pages/Contact"
	"HandyGold75/Pages/Home"
	"HandyGold75/Pages/Links"
	"HandyGold75/Pages/Login"
	"HandyGold75/Pages/Sheets"
	"HandyGold75/Pages/Tools"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"errors"
	"slices"
	"strings"
	"syscall/js"
)

var (
	PagesOrdered   = []string{"Home", "Links", "Contact", "Console", "sub:Admin", "sub:Tools", "sub:Sheets"}
	SubPagesOrderd = []string{
		"Admin:Users",
		"Admin:Config",
		"Admin:Logs",
		"Tools:Sonos",
		"Tools:Tapo",
		"Tools:YTDL",
		"Sheets:Assets",
		"Sheets:Licenses",
		"Sheets:Querys",
		"Sheets:Tests",
	}

	PagesToEntry = map[string]func(func(string), func(func())){
		"Home":            Home.Page,
		"Links":           Links.Page,
		"Contact":         Contact.Page,
		"Console":         Console.Page,
		"Admin:Users":     Admin.PageUsers,
		"Admin:Config":    Admin.PageConfig,
		"Admin:Logs":      Admin.PageLogs,
		"Tools:Sonos":     Tools.PageSonos,
		"Tools:Tapo":      Tools.PageTapo,
		"Tools:YTDL":      Tools.PageYTDL,
		"Sheets:Assets":   Sheets.PageAssets,
		"Sheets:Licenses": Sheets.PageLicenses,
		"Sheets:Querys":   Sheets.PageQuerys,
		"Sheets:Tests":    Sheets.PageTests,
		"Login":           Login.Page,
	}

	PagesToRequiredComs = map[string][]string{
		"Console":         {"help"},
		"Admin:Users":     {"users"},
		"Admin:Config":    {"exit", "restart"},
		"Admin:Logs":      {"logs"},
		"Tools:Sonos":     {"sonos"},
		"Tools:Tapo":      {"tapo"},
		"Tools:YTDL":      {"ytdl"},
		"Sheets:Assets":   {"db-asset"},
		"Sheets:Licenses": {"db-license"},
		"Sheets:Querys":   {"db-query"},
		"Sheets:Tests":    {"db-test"},
	}

	ErrPages = struct {
		ErrPagesClosingPage error
	}{
		ErrPagesClosingPage: errors.New("page closing, please skip page load"),
	}

	dockerShowing = false
	inTransition  = false
	requestedPage = ""
)

func autocompleteCallback(res string, resBytes []byte, resErr error) {
	defer ForcePage(requestedPage)
	requestedPage = ""
	if resErr != nil {
		return
	}

	err := json.Unmarshal(resBytes, &HTTP.Autocompletes)
	if err != nil {
		JS.Alert(err.Error())
		return
	}
}

func isAuthorizedForPage(page string) bool {
	hasAccess := true
	if requirements, ok := PagesToRequiredComs[page]; ok {
		for _, req := range requirements {
			if !slices.Contains(HTTP.Autocompletes, req) {
				hasAccess = false
				break
			}
		}
	}
	return hasAccess
}

func ToggleDocker() error {
	buttons, _ := DOM.GetElements("docker_buttons")
	titles, _ := DOM.GetElements("docker_titles")
	subs, _ := DOM.GetElements("docker_subs")
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

	dockerShowing = !dockerShowing
	if dockerShowing {
		buttons.Enables()
		buttons.StylesSet("opacity", "1")
		titles.StylesSet("color", "#bff")
		titles.StylesSet("opacity", "1")
		subs.StylesSet("opacity", "1")
		docker.StyleSet("max-width", "250px")
		docker.StyleSet("max-height", "90vh")
		docker.StyleSet("margin", "0px")
		docker.StyleSet("padding", "4px")
		docker.StyleSet("overflow-y", "scroll")
		docker_showhide.AttributeSet("className", "imgBtn imgBtnBorder imgBtnSmall")
		docker_showhide_img.AttributeSet("src", "./docs/assets/General/Hide-H.svg")
		return nil
	}

	buttons.Disables()
	buttons.StylesSet("opacity", "0")
	titles.StylesSet("color", "#88b")
	titles.StylesSet("opacity", "0")
	subs.StylesSet("opacity", "0")
	docker.StyleSet("max-width", "50px")
	docker.StyleSet("max-height", "48px")
	docker.StyleSet("margin", "-20px 0px 0px -20px")
	docker.StyleSet("padding", "0px")
	docker.StyleSet("overflow-y", "hidden")
	docker_showhide.AttributeSet("className", "imgBtn imgBtnSmall")
	docker_showhide_img.AttributeSet("src", "./docs/assets/General/Show-H.svg")
	return nil
}

func InitMainpage() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "mainpage"},
		Styles:     map[string]string{"min-height": "10%", "transition": "max-height 0.25s"},
	}.String())

	return nil
}

func InitDocker() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	items := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "docker_showhide", "class": "imgBtn imgBtnSmall"},
		Styles:     map[string]string{"max-width": "250px"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"id": "docker_showhide_img", "src": "./docs/assets/General/Show-H.svg", "alt": "ShowHide"},
			Styles:     map[string]string{"max-width": "250px"},
		}.String(),
	}.String()

	for _, page := range PagesOrdered {
		if !isAuthorizedForPage(page) {
			continue
		}

		if strings.HasPrefix(page, "sub:") {
			subPages := ""
			for _, subPage := range SubPagesOrderd {
				if !isAuthorizedForPage(subPage) {
					continue
				}

				if strings.Replace(page, "sub:", "", 1) == strings.Split(subPage, ":")[0] {
					subPages += HTML.HTML{Tag: "button",
						Attributes: map[string]string{"id": "page_" + subPage, "class": "dark large docker_buttons"},
						Styles:     map[string]string{"opacity": "0"},
						Inner:      strings.Split(subPage, ":")[1],
					}.String()
				}
			}

			if subPages == "" {
				continue
			}

			subPages = HTML.HTML{Tag: "p",
				Attributes: map[string]string{"class": "docker_titles"},
				Styles:     map[string]string{"opacity": "0", "color": "#88b", "font-size": "125%", "transition": "opacity 0.25s"},
				Inner:      strings.Replace(page, "sub:", "", 1),
				Surfix:     subPages,
			}.String()

			items += HTML.HTML{Tag: "div",
				Attributes: map[string]string{"class": "docker_subs"},
				Styles: map[string]string{
					"display":       "grid",
					"max-height":    "2.4em",
					"margin":        "4px 6px",
					"padding":       "4px 6px 4px 3px",
					"border-left":   "3px solid #55f",
					"border-radius": "0px",
					"opacity":       "0",
					"transition":    "max-height 0.25s, opacity 0.25s",
				},
				Inner: subPages,
			}.String()

			continue
		}

		items += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"id": "page_" + page, "class": "dark large docker_buttons"},
			Styles:     map[string]string{"opacity": "0"},
			Inner:      page,
		}.String()
	}

	body.InnerAddPrefix(HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "docker"},
		Styles: map[string]string{
			"position":   "fixed",
			"display":    "grid",
			"max-width":  "50px",
			"max-height": "48px",
			"margin":     "-20px 0px 0px -20px",
			"padding":    "0px",
			"overflow-y": "hidden",
			"top":        "25px",
			"left":       "25px",
			"border":     "4px solid #111",
			"transition": "max-width 0.25s, max-height 0.25s, margin 0.25s, padding 0.25s",
			"z-index":    "9999",
		},
		Inner: items,
	}.String())

	if el, err := DOM.GetElement("docker_showhide"); err == nil {
		el.EventAdd("click", func(el js.Value, evs []js.Value) { ToggleDocker() })
	}

	if els, err := DOM.GetElements("docker_buttons"); err == nil {
		els.Disables()
		els.EventsAdd("click", func(el js.Value, evs []js.Value) {
			ToggleDocker()
			Open(strings.Replace(el.Get("id").String(), "page_", "", 1))
		})
	}

	if els, err := DOM.GetElements("docker_subs"); err == nil {
		els.EventsAdd("mouseover", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "25em") })
		els.EventsAdd("mouseout", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "2.4em") })
	}

	dockerShowing = false
	JS.Async(func() { ToggleDocker() })

	return nil
}

func InitFooter() error {
	body, err := DOM.GetElement("body")
	if err != nil {
		return err
	}

	txt := HTML.HTML{Tag: "p", Styles: map[string]string{"font-weight": "bold", "margin": "auto auto auto 0px"}, Attributes: map[string]string{"class": "light"}, Inner: "HandyGold75 - 2022 / 2024"}.String()

	loginText := "Login"
	if HTTP.IsMaybeAuthenticated() {
		loginText = "Logout"
	}

	btnBackToTop := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_backtotop", "class": "small light"}, Inner: "Back to top"}.String()
	btnLogin := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_login", "class": "small light"}, Inner: loginText}.String()
	btnClearCache := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "footer_clearcache", "class": "small light"}, Inner: "Clear cache"}.String()

	body.InnerAddSurfix(HTML.HTML{Tag: "div",
		Styles: map[string]string{
			"display":    "flex",
			"margin-top": "10px",
			"padding":    "0px 10px",
		},
		Attributes: map[string]string{"id": "footer", "class": "light"},
		Inner:      txt + btnBackToTop + btnLogin + btnClearCache,
	}.String())

	el, err := DOM.GetElement("footer_backtotop")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) { JS.ScrollToTop() })

	el, err = DOM.GetElement("footer_login")
	if err != nil {
		return err
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		if HTTP.IsMaybeAuthenticated() {
			HTTP.Config.Set("token", "")
			HTTP.Autocompletes = []string{}

			if el, err := DOM.GetElement("docker"); err == nil {
				el.Remove()
			}
			if el, err := DOM.GetElement("footer_login"); err == nil {
				el.AttributeSet("innerHTML", "Login")
			}

			HTTP.UnauthorizedCallback()

		} else {
			ForcePage("Login")
		}
	})

	els, err := DOM.GetElement("footer_clearcache")
	if err != nil {
		return err
	}
	els.EventAdd("click", func(el js.Value, evs []js.Value) {
		JS.CacheClear()
		JS.DBClear()
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
	pageEntry, ok := PagesToEntry[page]
	if !ok {
		JS.Alert("Page \"" + page + "\" not found!")
		pageEntry = PagesToEntry[PagesOrdered[0]]
	}

	err := Init(func() { pageEntry(ForcePage, SetOnLoginSuccess) })
	if err != nil {
		JS.Alert(err.Error())
		return
	}

	JS.CacheSet("page", page)
}

func Open(page string) {
	if inTransition {
		return
	}

	if !HTTP.IsMaybeAuthenticated() {
		ForcePage(page)
		return
	}

	if len(HTTP.Autocompletes) == 0 {
		requestedPage = page
		HTTP.Send(autocompleteCallback, "autocomplete")
		return
	}

	ForcePage(page)
}
