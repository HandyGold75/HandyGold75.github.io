//go:build js && wasm

package main

import (
	"WebKit"
	"fmt"
	"syscall/js"
)

func main() {
	fmt.Println("Hello, WebsdadAssembly!")

	dom := js.Global().Get("document")
	body := dom.Call("getElementsByTagName", "body").Index(0)
	body.Set("innerHTML", "Moving towards GO wasm instead of Python wasm<br>For reasons...<br>Old site should still be available at ./python")
	fmt.Println(body.Get("innerHTML"))

	el, err := WebKit.GetElement("testId")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(el)
}
