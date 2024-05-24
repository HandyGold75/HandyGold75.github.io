//go:build js && wasm

package main

import (
	"HandyGold75/Pages"
	"HandyGold75/WebKit/JS"
)

func main() {
	mainPage := JS.CacheGet("mainPage")
	if mainPage == "" {
		mainPage = "Home"
	}

	Pages.Open(mainPage)
	<-make(chan int)
}
