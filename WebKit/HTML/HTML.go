//go:build js && wasm

package HTML

import (
	"fmt"
	"maps"
	"strings"
)

type (
	HTML struct {
		Tag        string
		Attributes map[string]string
		Styles     map[string]string
		Inner      string
		Prefix     string
		Surfix     string
	}
)

func (html HTML) String() string {
	styles := []string{}
	for k, v := range html.Styles {
		if strings.ContainsAny(k, ":;") || strings.ContainsAny(v, ":;") {
			fmt.Printf("Warning invalid style definition: %v: %v\r\n", strings.ToLower(k), v)
			continue
		}
		styles = append(styles, strings.ToLower(k)+": "+v)
	}

	attributes := []string{}
	for k, v := range html.Attributes {
		if strings.ContainsAny(k, "\"") || strings.ContainsAny(v, "\"") {
			fmt.Printf("Warning invalid attribute definition: %v=\"%v\"\r\n", strings.ToLower(k), v)
			continue
		}
		attributes = append(attributes, strings.ToLower(k)+"=\""+v+"\"")
	}
	if len(styles) > 0 {
		attributes = append(attributes, "style=\""+strings.Join(styles, "; ")+"\" ")
	}

	finalStr := html.Prefix + "<" + strings.ToLower(html.Tag)
	if len(attributes) > 0 {
		finalStr += " " + strings.Join(attributes, " ")
	}
	finalStr += ">" + html.Inner + "</" + strings.ToLower(html.Tag) + ">" + html.Surfix

	return finalStr
}

func (html HTML) LinkWrap(href string) HTML {
	return HTML{Tag: "a",
		Attributes: map[string]string{"href": href, "target": "_blank"},
		Inner:      html.String(),
	}
}

func (html HTML) ApplyTemplate(template HTML) HTML {
	if html.Tag == "" {
		html.Tag = template.Tag
	}
	if template.Attributes != nil {
		maps.Copy(template.Attributes, html.Attributes)
		html.Attributes = template.Attributes
	}
	if template.Styles != nil {
		maps.Copy(template.Styles, html.Styles)
		html.Styles = template.Styles
	}
	if html.Inner == "" {
		html.Inner = template.Inner
	}
	if html.Prefix == "" {
		html.Prefix = template.Prefix
	}
	if html.Surfix == "" {
		html.Surfix = template.Surfix
	}

	return html
}
