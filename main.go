//go:build js && wasm

package main

import "Pages"

func main() {
	Pages.Open("Home")
	<-make(chan int)
}
