//go:build js && wasm

package main

import (
	"HandyGold75/Pages"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
)

func main() {
	mainPage := JS.CacheGet("mainPage")
	if mainPage == "" {
		mainPage = "Home"
	}

	HTTP.Config.Load()
	HTTP.UnauthorizedCallback = func() { JS.Async(func() { Pages.ForcePage("Login") }) }

	if !HTTP.Config.RememberSignIn {
		HTTP.Config.Set("Token", "")
	}

	Pages.Open(mainPage)
	<-make(chan bool)
}
