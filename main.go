//go:build js && wasm

package main

import "HandyGold75/Pages"

func main() {
	Pages.Open("Home")
	<-make(chan int)
}
