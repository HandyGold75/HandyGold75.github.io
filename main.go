//go:build js && wasm

package main

import (
	"WebKit"
	"fmt"
)

func main() {
	body, err := WebKit.GetElement("body")
	if err != nil {
		fmt.Println(err)
		return
	}
	txt := WebKit.HTML{Tag: "p", Attributes: map[string]string{"id": "someText"}, Styles: map[string]string{"color": "#55F"}, Inner: "Moving towards GO wasm instead of Python wasm<br>For reasons...<br>Old site should still be available at ./python"}.String()
	body.SetElement(txt)

	el, err := WebKit.GetElement("someText")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(el.Inner())
}
