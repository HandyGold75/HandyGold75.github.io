//go:build js && wasm

package Pages

import (
	"HandyGold75/Pages/Admin"
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
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"slices"
	"strings"
	"syscall/js"
)

type (
	Page struct {
		Name         string
		Entry        func()
		RequiredComs []string
		Hidden       bool
	}
)

var (
	PagesTest = []Page{
		{Name: "Home", Entry: Home.Page, RequiredComs: []string{}, Hidden: false},
		{Name: "Links", Entry: Links.Page, RequiredComs: []string{}, Hidden: false},
		{Name: "Contact", Entry: Contact.Page, RequiredComs: []string{}, Hidden: false},
		{Name: "Login", Entry: Login.Page, RequiredComs: []string{}, Hidden: true},
		{Name: "Admin:Users", Entry: Admin.PageUsers, RequiredComs: []string{}, Hidden: false},
		{Name: "Admin:Config", Entry: Admin.PageConfig, RequiredComs: []string{}, Hidden: false},
		{Name: "Admin:Monitor", Entry: Admin.PageMonitor, RequiredComs: []string{}, Hidden: false},
		{Name: "Admin:Logs", Entry: Admin.PageLogs, RequiredComs: []string{}, Hidden: false},
		{Name: "Tools:Console", Entry: Tools.PageConsole, RequiredComs: []string{}, Hidden: false},
		{Name: "Tools:Sonos", Entry: Tools.PageSonos, RequiredComs: []string{}, Hidden: false},
		{Name: "Tools:Tapo", Entry: Tools.PageTapo, RequiredComs: []string{}, Hidden: false},
		{Name: "Tools:YTDL", Entry: Tools.PageYTDL, RequiredComs: []string{}, Hidden: false},
		{Name: "Sheets:Assets", Entry: Sheets.PageAssets, RequiredComs: []string{}, Hidden: false},
		{Name: "Sheets:Licenses", Entry: Sheets.PageLicenses, RequiredComs: []string{}, Hidden: false},
		{Name: "Sheets:Querys", Entry: Sheets.PageQuerys, RequiredComs: []string{}, Hidden: false},
		{Name: "Sheets:Tests", Entry: Sheets.PageTests, RequiredComs: []string{}, Hidden: false},
	}

	PagesOrdered   = []string{"Home", "Links", "Contact", "sub:Admin", "sub:Tools", "sub:Sheets"}
	SubPagesOrderd = []string{
		"Admin:Users",
		"Admin:Config",
		"Admin:Monitor",
		"Admin:Logs",
		"Tools:Console",
		"Tools:Sonos",
		"Tools:Tapo",
		"Tools:YTDL",
		"Sheets:Assets",
		"Sheets:Licenses",
		"Sheets:Querys",
		"Sheets:Tests",
	}

	PagesToEntry = map[string]func(){
		"Home":            Home.Page,
		"Links":           Links.Page,
		"Contact":         Contact.Page,
		"Admin:Users":     Admin.PageUsers,
		"Admin:Config":    Admin.PageConfig,
		"Admin:Monitor":   Admin.PageMonitor,
		"Admin:Logs":      Admin.PageLogs,
		"Tools:Console":   Tools.PageConsole,
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
		"Admin:Users":     {"users"},
		"Admin:Config":    {"exit", "restart"},
		"Admin:Monitor":   {"debug"},
		"Admin:Logs":      {"logs"},
		"Tools:Console":   {"help"},
		"Tools:Sonos":     {"sonos"},
		"Tools:Tapo":      {"tapo"},
		"Tools:YTDL":      {"ytdl"},
		"Sheets:Assets":   {"db-asset"},
		"Sheets:Licenses": {"db-license"},
		"Sheets:Querys":   {"db-query"},
		"Sheets:Tests":    {"db-test"},
	}

	DockerShowing = false
	inTransistion = false
	requestedPage = ""
)

func getPage(name string) Page {
	for _, page := range PagesTest {
		if page.Name == name {
			return page
		}
	}
	Widget.PopupAlert("Error", "Page \""+name+"\" not found!", func() {})
	return PagesTest[0]
}

func autocompleteCallback(res string, resBytes []byte, resErr error) {
	defer Open(requestedPage, true)
	requestedPage = ""
	if resErr != nil {
		return
	}

	err := json.Unmarshal(resBytes, &HTTP.Autocompletes)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
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

	DockerShowing = !DockerShowing
	if DockerShowing {
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

	docker.El.Call("scroll", map[string]any{"top": 0})

	return nil
}

func showMain() error {
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
					subPages += HTML.HTML{Tag: "button", Inner: strings.Split(subPage, ":")[1],
						Attributes: map[string]string{"id": "page_" + subPage, "class": "dark large docker_buttons"},
						Styles:     map[string]string{"opacity": "0"},
					}.String()
				}
			}

			if subPages == "" {
				continue
			}

			subPages = HTML.HTML{Tag: "p", Inner: strings.Replace(page, "sub:", "", 1),
				Attributes: map[string]string{"class": "docker_titles"},
				Styles:     map[string]string{"opacity": "0", "color": "#88b", "font-size": "125%", "transition": "opacity 0.25s"},
				Surfix:     subPages,
			}.String()

			items += HTML.HTML{Tag: "div", Inner: subPages,
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
			}.String()

			continue
		}

		items += HTML.HTML{Tag: "button", Inner: page,
			Attributes: map[string]string{"id": "page_" + page, "class": "dark large docker_buttons"},
			Styles:     map[string]string{"opacity": "0"},
		}.String()
	}

	docker := HTML.HTML{Tag: "div", Inner: items,
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
	}.String()

	mainpage := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "mainpage"},
		Styles:     map[string]string{"max-height": "0vh"},
	}.String()

	txt := HTML.HTML{Tag: "p", Inner: "HandyGold75 - 2022 / 2024",
		Styles:     map[string]string{"font-weight": "bold", "margin": "auto auto auto 0px"},
		Attributes: map[string]string{"class": "light"},
	}.String()

	loginText := "Login"
	if HTTP.IsMaybeAuthenticated() {
		loginText = "Logout"
	}

	btnBackToTop := HTML.HTML{Tag: "button", Inner: "Back to top",
		Attributes: map[string]string{"id": "footer_backtotop", "class": "small light"},
	}.String()
	btnLogin := HTML.HTML{Tag: "button", Inner: loginText,
		Attributes: map[string]string{"id": "footer_login", "class": "small light"},
	}.String()
	btnClearCache := HTML.HTML{Tag: "button", Inner: "Clear cache",
		Attributes: map[string]string{"id": "footer_clearcache", "class": "small light"},
	}.String()

	footer := HTML.HTML{Tag: "div", Inner: txt + btnBackToTop + btnLogin + btnClearCache,
		Attributes: map[string]string{"id": "footer", "class": "light"},
		Styles: map[string]string{
			"display":    "flex",
			"max-height": "0px",
			"margin-top": "10px",
			"padding":    "0px 10px",
		},
	}.String()

	body.InnerSet(docker + mainpage + footer)

	if el, err := DOM.GetElement("docker_showhide"); err == nil {
		el.EventAdd("click", func(el js.Value, evs []js.Value) { ToggleDocker() })
	}

	if els, err := DOM.GetElements("docker_buttons"); err == nil {
		els.Disables()
		els.EventsAdd("click", func(el js.Value, evs []js.Value) {
			ToggleDocker()
			Open(strings.Replace(el.Get("id").String(), "page_", "", 1), false)
		})
	}

	if els, err := DOM.GetElements("docker_subs"); err == nil {
		els.EventsAdd("mouseover", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "25em") })
		els.EventsAdd("mouseout", func(el js.Value, evs []js.Value) { el.Get("style").Set("max-height", "2.4em") })
	}

	DockerShowing = false
	JS.Async(func() { ToggleDocker() })

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
			Open("Login", false)
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
		JS.Async(func() { Open("Home", true) })
	})

	el, err = DOM.GetElement("footer")
	if err != nil {
		return err
	}

	if err := Widget.AnimateStyle("footer", "max-height", "0px", "50px", 250); err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
	}

	return nil
}

func Open(page string, force bool) {
	if (inTransistion || requestedPage != "") && !force {
		return
	}

	if HTTP.IsMaybeAuthenticated() && len(HTTP.Autocompletes) == 0 {
		requestedPage = page
		HTTP.Send(autocompleteCallback, "autocomplete")
		return
	}

	for _, id := range []string{"mainpage", "docker", "footer"} {
		if _, err := DOM.GetElement(id); err != nil {
			if err := showMain(); err != nil {
				Widget.PopupAlert("Error", err.Error(), func() {})
				return
			}
			break
		}
	}

	p := getPage(page)
	if page != "Login" {
		HTTP.AuthorizedCallback = func() {
			DockerShowing = true
			if err := ToggleDocker(); err != nil {
				if el, err := DOM.GetElement("docker"); err == nil {
					el.Remove()
				}
				Open(p.Name, true)
				return
			}

			JS.AfterDelay(250, func() {
				if el, err := DOM.GetElement("docker"); err == nil {
					el.Remove()
				}
				Open(p.Name, true)
			})
		}
	}
	JS.CacheSet("page", page)

	el, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.StyleSet("max-height", "100vh")

	inTransistion = true
	JS.Async(func() {
		if err := Widget.AnimateFunction("mainpage", "max-height", "0vh", "100vh", 250, func() { el.InnerSet(""); p.Entry() }, func() { inTransistion = false; el.StyleSet("max-height", "") }); err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		}
	})
}
