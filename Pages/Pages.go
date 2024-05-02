//go:build js && wasm

package Pages

import (
	"WebKit"
	"fmt"
)

var (
	AvailablePages = map[string]func(){
		"TempMovePage": TempMovePage,
	}

	AvailablePagesOrdered = []string{"TempMovePage"}
)

func TempMovePage() {
	mp, err := WebKit.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	txt := WebKit.HTML{
		Tag:        "p",
		Attributes: map[string]string{"id": "someText"},
		Styles:     map[string]string{"color": "#55F"},
		Inner:      "Moving towards GO wasm instead of Python wasm<br>For reasons...<br>Old site should still be available at " + WebKit.HTML{Attributes: map[string]string{"href": "./python"}, Inner: "./python"}.ApplyTemplate(WebKit.HTML_Link).String(),
	}.String()

	mp.InnerSet(txt)

	el, err := WebKit.GetElement("someText")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(el.InnerGet())
}

func Init() {
	body, err := WebKit.GetElement("body")
	if err != nil {
		fmt.Println(err)
		return
	}

	mp, err := WebKit.GetElement("mainpage")
	if err != nil {
		body.InnerAddPrefix(WebKit.HTML{Tag: "div", Attributes: map[string]string{"id": "mainpage"}}.String())
		mp, err = WebKit.GetElement("mainpage")
		if err != nil {
			fmt.Println(err)
			return
		}
	}
	mp.InnerClear()

	_, err = WebKit.GetElement("docker")
	if err == nil {
		return
	}

	items := ""
	for _, v := range AvailablePagesOrdered {
		items += WebKit.HTML{Tag: "button", Attributes: map[string]string{"class": "dark large"}, Inner: v}.String()
	}

	body.InnerAddPrefix(WebKit.HTML{Tag: "div",
		Styles: map[string]string{
			"position":   "fixed",
			"display":    "grid",
			"top":        "25px",
			"left":       "25px",
			"border":     "4px solid #111",
			"transition": "left 0.25s",
			"z-index":    "9999",
		}, Attributes: map[string]string{"id": "docker"}, Inner: items}.String())
}

func Open(page string) {
	pageEntry, ok := AvailablePages[page]
	if !ok {
		fmt.Println("Page \"" + page + "\" not found!")
		return
	}

	Init()
	pageEntry()
}
