//go:build js && wasm

package main

import "Pages"

func main() {
	Pages.Open("TempMovePage")
}
