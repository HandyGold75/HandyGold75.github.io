//go:build js && wasm

package main

import (
	"HandyGold75/Pages"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
)

func main() {
	page := JS.CacheGet("page")
	if page == "" {
		page = "Home"
	}

	HTTP.Config.Load()
	HTTP.UnauthorizedCallback = func() { Pages.ForcePage("Login") }

	if page == "Login" {
		HTTP.AuthorizedCallback = func() { Pages.ForcePage("Home") }
	} else {
		HTTP.AuthorizedCallback = func() { Pages.ForcePage(page) }
	}

	if !HTTP.Config.RememberSignIn {
		HTTP.Config.Set("Token", "")
	}

	Pages.Open(page)
	<-make(chan bool)
}
