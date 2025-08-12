//go:build js && wasm

package main

import (
	"HandyGold75/Pages"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"strings"
)

func main() {
	page := JS.CacheGet("page")
	if page == "" {
		page = "Home"
	}

	HTTP.Config.Load()
	HTTP.UnauthorizedCallback = func() {
		Pages.DockerShowing = true
		Pages.ToggleDocker()
		Pages.Open("Login", true)
	}

	pageOnAuth := page
	if page == "Login" {
		pageOnAuth = "Home"
	}

	HTTP.AuthorizedCallback = func() {
		Pages.DockerShowing = true
		if err := Pages.ToggleDocker(); err != nil {
			if el, err := DOM.GetElement("docker"); err == nil {
				el.Remove()
			}
			Pages.Open(pageOnAuth, true)
			return
		}

		JS.AfterDelay(250, func() {
			if el, err := DOM.GetElement("docker"); err == nil {
				el.Remove()
			}
			Pages.Open(pageOnAuth, true)
		})
	}

	if !HTTP.Config.RememberSignIn {
		HTTP.Deauthenticate()
	}

	Pages.Open(page, true)

	if strings.HasPrefix(strings.ToLower(JS.Href()), "https://www.handygold75.com/spotify_auth_callback") {
		JS.Async(func() {
			url := strings.Split(JS.Href(), "/")
			Widget.PopupAlert("Spotify Token", url[len(url)-1], func() {})
			JS.SetUrl("")
		})
	}

	<-make(chan bool)
}
