//go:build js && wasm

package Admin

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"HandyGold75/WebKit/Widget"
	"encoding/json"
	"strings"
	"syscall/js"
)

var (
	selectedUser = User{}
)

func createUserCallback(res string, resBytes []byte, resErr error) {
	elUsername, err := DOM.GetElement("users_username")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	username := elUsername.AttributeGet("value")

	elPassword, err := DOM.GetElement("users_password")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	password := elPassword.AttributeGet("value")

	els, err := DOM.GetElements("users_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	els.Enables()

	elSub, err := DOM.GetElement("users_submitnew")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.Enable()

	JS.AfterDelay(3000, func() { elSub.StyleSet("border", "2px solid #55F") })
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		elSub.StyleSet("border", "2px solid #F55")
		return
	} else {
		elSub.StyleSet("border", "2px solid #5F5")
	}

	elList, err := DOM.GetElement("users_list")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	userHash := HTTP.Sha1(username + HTTP.Sha512(password))

	elList.InnerAddPrefix(HTML.HTML{Tag: "button", Inner: userHash,
		Attributes: map[string]string{"id": "users_list_buttons_" + userHash, "class": "dark small users_list_buttons"},
		Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
	}.String())

	elBtn, err := DOM.GetElement("users_list_buttons_" + userHash)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	elBtn.EventAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(getUserCallback, "users", "get", el.Get("innerHTML").String())
	})
}

func createUser(el js.Value, els []js.Value) {
	elsInp, err := DOM.GetElements("users_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elsInp.Disables()

	elSub, err := DOM.GetElement("users_submitnew")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elSub.Disable()

	elUsername, err := DOM.GetElement("users_username")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	username := elUsername.AttributeGet("value")

	elPassword, err := DOM.GetElement("users_password")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	password := elPassword.AttributeGet("value")

	elAuthlevel, err := DOM.GetElement("users_authlevel")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	authlevel := elAuthlevel.AttributeGet("value")

	elRoles, err := DOM.GetElement("users_roles")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	roles := elRoles.AttributeGet("value")

	elBtn, err := DOM.GetElement("users_enabled_img")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	state := "1"
	if elBtn.AttributeGet("alt") == "Disabled" {
		state = "0"
	}

	HTTP.Send(createUserCallback, "users", "create", username, password, authlevel, roles, state)
}

func modifyUserCallback(res string, resBytes []byte, resErr error) {
	elsInp, err := DOM.GetElements("users_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elsInp.Enables()

	elsSub, err := DOM.GetElements("users_submits")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elsSub.Enables()

	JS.AfterDelay(3000, func() { elsSub.StylesSet("border", "2px solid #55F") })
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		elsSub.StylesSet("border", "2px solid #F55")
		return
	} else {
		elsSub.StylesSet("border", "2px solid #5F5")
	}

	user := User{}
	err = json.Unmarshal(resBytes, &user)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	oldHash := HTTP.Sha1(selectedUser.Username + selectedUser.Password)
	selectedUser = user

	el, err := DOM.GetElement("users_header")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet(HTTP.Sha1(selectedUser.Username + selectedUser.Password))

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		if els.Els.Index(i).Get("innerHTML").String() == oldHash {
			els.Els.Index(i).Set("innerHTML", HTTP.Sha1(selectedUser.Username+selectedUser.Password))
			break
		}
	}
}

func modifyUser(el js.Value, evs []js.Value) {
	if len(evs) < 1 {
		Widget.PopupAlert("Error", "evs was not parsed", func() {})
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	elSub, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_") + "_submit")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	key := strings.Split(el.Get("id").String(), "_")[1]
	elInp, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_"))
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	value := elInp.AttributeGet("value")

	switch key {
	case "username":
		if value == selectedUser.Username {
			return
		}

	case "password":
		if value == selectedUser.Password {
			return
		}

	case "authlevel":
		if value == authMapReversed[selectedUser.AuthLevel] {
			return
		}

	case "roles":
		value = strings.ReplaceAll(value, ", ", ",")
		if value == strings.Join(selectedUser.Roles, ",") {
			return
		}

	default:
		Widget.PopupAlert("Error", "invalid key \""+key+"\"", func() {})
		return
	}

	elInp.Disable()
	elSub.Disable()

	HTTP.Send(modifyUserCallback, "users", "modify", HTTP.Sha1(selectedUser.Username+selectedUser.Password), key, value)
}

func deletedUserCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})

		elsInp, err := DOM.GetElements("users_inputs")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elsInp.Enables()

		elsSub, err := DOM.GetElements("users_submits")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elsSub.Enables()

		elDel, err := DOM.GetElement("users_delete")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elDel.Enable()

		elDea, err := DOM.GetElement("users_deauth")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		elDea.Enable()
		return
	}

	oldHash := HTTP.Sha1(selectedUser.Username + selectedUser.Password)
	selectedUser = User{}

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	for i := 0; i < els.Els.Length(); i++ {
		if els.Els.Index(i).Get("innerHTML").String() == oldHash {
			els.Els.Index(i).Call("remove")
			break
		}
	}

	el, err := DOM.GetElement("users_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet("")
}

func deleteUser(el js.Value, els []js.Value) {
	if !JS.Confirm("Deleting user " + selectedUser.Username + "!\n" +
		"\nAuthLevel: " + authMapReversed[selectedUser.AuthLevel] +
		"\nRoles: " + strings.Join(selectedUser.Roles, ", ") +
		"\nUserHash: " + HTTP.Sha1(selectedUser.Username+selectedUser.Password)) {
		return
	}

	elsInp, err := DOM.GetElements("users_inputs")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elsInp.Disables()

	elsSub, err := DOM.GetElements("users_submits")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elsSub.Disables()

	elDel, err := DOM.GetElement("users_delete")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDel.Disable()

	elDea, err := DOM.GetElement("users_deauth")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDea.Disable()

	HTTP.Send(deletedUserCallback, "users", "delete", HTTP.Sha1(selectedUser.Username+selectedUser.Password))
}

func toggleEnabledCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
	}
}

func toggleEnabled(el js.Value, els []js.Value) {
	elBtn, err := DOM.GetElement("users_enabled")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elBtnImg, err := DOM.GetElement("users_enabled_img")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	state := "Disabled"
	btnClass := "imgBtn imgBtnMedium"
	stateCode := "0"
	if elBtnImg.AttributeGet("alt") == "Disabled" {
		state = "Enabled"
		btnClass = "imgBtn imgBtnMedium imgBtnBorder"
		stateCode = "1"
	}

	elBtnImg.AttributeSet("alt", state)
	elBtnImg.AttributeSet("src", "./docs/assets/Admin/Users/"+state+".svg")
	elBtn.AttributeSet("className", btnClass)

	if selectedUser.Username != "" && selectedUser.Password != "" {
		HTTP.Send(toggleEnabledCallback, "users", "modify", HTTP.Sha1(selectedUser.Username+selectedUser.Password), "enabled", stateCode)
	}
}

func deauthUserCallback(res string, resBytes []byte, resErr error) {
	el, err := DOM.GetElement("users_deauth")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		el.StyleSet("border", "2px solid #F55")
	} else {
		el.StyleSet("border", "2px solid #5F5")
	}

	JS.AfterDelay(3000, func() { el.StyleSet("border", "") })
	el.Enable()
}

func deauthUser(el js.Value, els []js.Value) {
	elDea, err := DOM.GetElement("users_deauth")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	elDea.Disable()

	HTTP.Send(deauthUserCallback, "users", "deauth", "user", HTTP.Sha1(selectedUser.Username+selectedUser.Password))
}

func userListCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	users := []string{}
	err := json.Unmarshal(resBytes, &users)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	usersList := ""
	for _, v := range users {
		usersList += HTML.HTML{Tag: "button", Inner: v,
			Attributes: map[string]string{"class": "dark small users_list_buttons"},
			Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
		}.String()
	}

	el, err := DOM.GetElement("users_list")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet(usersList + HTML.HTML{Tag: "button", Inner: "New user",
		Attributes: map[string]string{"id": "users_newuser", "class": "dark small"},
		Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
	}.String())

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}

	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		HTTP.Send(getUserCallback, "users", "get", el.Get("innerHTML").String())
	})

	el, err = DOM.GetElement("users_newuser")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		Widget.AnimateReplace("users_out", "max-height", "0vh", "100vh", 250, showNewUser, func() {})
	})
}

func getUserCallback(res string, resBytes []byte, resErr error) {
	if resErr != nil {
		Widget.PopupAlert("Error", resErr.Error(), func() {})
		return
	}

	user := User{}
	err := json.Unmarshal(resBytes, &user)
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	selectedUser = user

	Widget.AnimateReplace("users_out", "max-height", "0vh", "100vh", 250, showUser, func() {})
}

func showUser() {
	getRow := func(name string, typ string, autocomplete string, value string) []string {
		id := "users_" + strings.ToLower(name)
		txt := HTML.HTML{Tag: "p", Inner: name,
			Styles: map[string]string{"margin": "auto 0px", "padding": "5px 0px", "background": "#222", "border": "2px solid #111"},
		}.String()
		inp := HTML.HTML{Tag: "input",
			Attributes: map[string]string{"type": typ, "id": id, "class": "users_inputs", "autocomplete": autocomplete, "placeholder": name, "value": value},
		}.String()
		btn := HTML.HTML{Tag: "button", Inner: "Submit",
			Attributes: map[string]string{"id": id + "_submit", "class": "dark medium users_submits"},
		}.String()
		return []string{txt, inp, btn}
	}

	gridStyle := map[string]string{"display": "grid", "grid-template-columns": "20% 60% 20%", "background": "#2A2A2A"}

	header := HTML.HTML{Tag: "h2", Inner: HTTP.Sha1(selectedUser.Username + selectedUser.Password),
		Attributes: map[string]string{"id": "users_header"},
		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
	}.String()

	username := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Username", "email", "username", selectedUser.Username), ""),
		Styles: gridStyle,
	}.String()

	password := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Password", "password", "new-password", selectedUser.Password), ""),
		Styles: gridStyle,
	}.String()

	row := getRow("authLevel", "", "", "")
	row[1] = HTML.HTML{Tag: "select",
		Attributes: map[string]string{"id": "users_authlevel", "class": "users_inputs", "size": "1"},
		Inner: func() string {
			s := ""
			for v := range authMap {
				if v == authMapReversed[selectedUser.AuthLevel] {
					s += HTML.HTML{Tag: "option", Inner: v,
						Attributes: map[string]string{"selected": ""},
					}.String()
					continue
				}
				s += HTML.HTML{Tag: "option", Inner: v}.String()
			}
			return s
		}(),
	}.String()
	authLevel := HTML.HTML{Tag: "div", Inner: strings.Join(row, ""),
		Styles: gridStyle,
	}.String()

	roles := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Roles", "text", "", strings.Join(selectedUser.Roles, ", ")), ""),
		Styles: gridStyle,
	}.String()

	state := "Disabled"
	btnClass := "imgBtn imgBtnMedium"
	if selectedUser.Enabled {
		state = "Enabled"
		btnClass = "imgBtn imgBtnMedium imgBtnBorder"
	}

	enabledBtn := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "users_enabled", "class": btnClass},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"id": "users_enabled_img", "src": "./docs/assets/Admin/Users/" + state + ".svg", "alt": state},
		}.String(),
	}.String()

	trashBtn := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "users_delete", "class": "imgBtn imgBtnMedium"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"id": "users_delete_img", "src": "./docs/assets/General/Trash.svg", "alt": "delete"},
		}.String(),
	}.String()

	deauthBtn := HTML.HTML{Tag: "button", Inner: "Deauth",
		Attributes: map[string]string{"id": "users_deauth", "class": "dark large"},
	}.String()

	spacer := HTML.HTML{Tag: "div", Styles: map[string]string{"background": "#2A2A2A"}}.String()
	buttons := HTML.HTML{Tag: "div", Inner: spacer + enabledBtn + spacer + trashBtn + spacer + deauthBtn + spacer,
		Styles: map[string]string{"display": "grid", "grid-template-columns": "5% 25% 5% 25% 5% 30% 5%", "background": "#2A2A2A"},
	}.String()

	el, err := DOM.GetElement("users_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet(header + username + password + authLevel + roles + buttons)

	for _, key := range []string{"username", "password", "authlevel", "roles"} {
		el, err = DOM.GetElement("users_" + key)
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		el.EventAdd("keyup", modifyUser)

		el, err = DOM.GetElement("users_" + key + "_submit")
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
			return
		}
		el.EventAdd("click", modifyUser)
	}

	el, err = DOM.GetElement("users_enabled")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", toggleEnabled)

	el, err = DOM.GetElement("users_delete")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", deleteUser)

	el, err = DOM.GetElement("users_deauth")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", deauthUser)
}

func showNewUser() {
	getRow := func(name string, typ string, autocomplete string) []string {
		id := "users_" + strings.ToLower(name)

		txt := HTML.HTML{Tag: "p", Inner: name,
			Styles: map[string]string{"margin": "auto 0px", "padding": "5px 0px", "background": "#222", "border": "2px solid #111"},
		}.String()
		inp := HTML.HTML{Tag: "input", Attributes: map[string]string{"type": typ, "id": id, "class": "users_inputs", "autocomplete": autocomplete, "placeholder": name}}.String()

		return []string{txt, inp}
	}

	selectedUser = User{}

	gridStyle := map[string]string{"display": "grid", "grid-template-columns": "20% 80%", "background": "#2A2A2A"}

	header := HTML.HTML{Tag: "h2", Inner: "New User",
		Attributes: map[string]string{"id": "users_header"},
		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
	}.String()

	username := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Username", "email", "username"), ""),
		Styles: gridStyle,
	}.String()

	password := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Password", "password", "new-password"), ""),
		Styles: gridStyle,
	}.String()

	row := getRow("authLevel", "", "")
	row[1] = HTML.HTML{Tag: "select",
		Attributes: map[string]string{"id": "users_authlevel", "class": "users_inputs", "size": "1"},
		Inner: func() string {
			s := ""
			for v := range authMap {
				if v == "user" {
					s += HTML.HTML{Tag: "option", Inner: v,
						Attributes: map[string]string{"selected": ""},
					}.String()
					continue
				}
				s += HTML.HTML{Tag: "option", Inner: v}.String()
			}
			return s
		}(),
	}.String()
	authLevel := HTML.HTML{Tag: "div", Inner: strings.Join(row, ""),
		Styles: gridStyle,
	}.String()

	roles := HTML.HTML{Tag: "div", Inner: strings.Join(getRow("Roles", "text", ""), ""),
		Styles: gridStyle,
	}.String()

	enabledBtn := HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "users_enabled", "class": "imgBtn imgBtnMedium imgBtnBorder"},
		Inner: HTML.HTML{Tag: "img",
			Attributes: map[string]string{"id": "users_enabled_img", "src": "./docs/assets/Admin/Users/Enabled.svg", "alt": "Enabled"},
		}.String(),
	}.String()

	submitBtn := HTML.HTML{Tag: "button", Inner: "Confirm",
		Attributes: map[string]string{"id": "users_submitnew", "class": "dark large"},
	}.String()

	spacer := HTML.HTML{Tag: "div", Styles: map[string]string{"background": "#2A2A2A"}}.String()
	buttons := HTML.HTML{Tag: "div", Inner: spacer + enabledBtn + spacer + submitBtn + spacer,
		Styles: map[string]string{"display": "grid", "grid-template-columns": "5% 25% 5% 60% 5%", "background": "#2A2A2A"},
	}.String()

	el, err := DOM.GetElement("users_out")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.InnerSet(header + username + password + authLevel + roles + buttons)

	el, err = DOM.GetElement("users_enabled")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", toggleEnabled)

	el, err = DOM.GetElement("users_submitnew")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	el.EventAdd("click", createUser)
}

func showUsers() {
	header := HTML.HTML{Tag: "h1", Inner: "Users"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_list"},
		Styles: map[string]string{
			"display":       "grid",
			"height":        "100%",
			"width":         "25%",
			"margin":        "0px 15px 0px auto",
			"background":    "#2A2A2A",
			"border":        "2px solid #111",
			"border-radius": "10px"},
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_out"},
		Styles: map[string]string{
			"width":       "75%",
			"max-height":  "0vh",
			"margin":      "0px auto",
			"background":  "#2A2A2A",
			"border":      "2px solid #111",
			"white-space": "pre",
			"font-family": "Hack",
		},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		Widget.PopupAlert("Error", err.Error(), func() {})
		return
	}
	mp.InnerSet(header + HTML.HTML{Tag: "div", Inner: types + out,
		Styles: map[string]string{"display": "flex"},
	}.String())

	HTTP.Send(userListCallback, "users", "list")
}

func PageUsers() {
	if !HTTP.IsMaybeAuthenticated() {
		HTTP.UnauthorizedCallback()
		return
	}
	HTTP.HasAccessTo("users", func(hasAccess bool, err error) {
		if err != nil {
			Widget.PopupAlert("Error", err.Error(), func() {})
		} else if !hasAccess {
			Widget.PopupAlert("Error", "unauthorized", func() {})
		} else {
			showUsers()
		}
	})
}
