//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"
	"strings"
	"syscall/js"
)

type (
	User struct {
		Username  string   `json:"Username"`
		Password  string   `json:"Password"`
		AuthLevel int      `json:"AuthLevel"`
		Roles     []string `json:"Roles"`
		Enabled   bool     `json:"Enabled"`
	}
)

var (
	authMap         = map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}
	authMapReversed = map[int]string{0: "guest", 1: "user", 2: "admin", 3: "owner"}

	allRoles = []string{"CLI", "Home"}

	selectedUser = User{}
)

func createUserCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	}

	elUsername, err := DOM.GetElement("users_username")
	if err != nil {
		fmt.Println(err)
		return
	}
	username := elUsername.AttributeGet("value")

	elPassword, err := DOM.GetElement("users_password")
	if err != nil {
		fmt.Println(err)
		return
	}
	password := elPassword.AttributeGet("value")

	els, err := DOM.GetElements("users_inputs")
	if err != nil {
		fmt.Println(err)
		return
	}
	els.Enables()

	elSub, err := DOM.GetElement("users_submitnew")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.Enable()

	JS.AfterDelay(3000, func() { elSub.StyleSet("border", "2px solid #55F") })
	if resErr != nil {
		JS.Alert(resErr.Error())
		elSub.StyleSet("border", "2px solid #F55")
		return
	} else {
		elSub.StyleSet("border", "2px solid #5F5")
	}

	elList, err := DOM.GetElement("users_list")
	if err != nil {
		fmt.Println(err)
		return
	}

	userHash := HTTP.Sha1(username + HTTP.Sha512(password))

	elList.InnerAddPrefix(HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "users_list_buttons_" + userHash, "class": "dark small users_list_buttons"},
		Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
		Inner:      userHash,
	}.String())

	elBtn, err := DOM.GetElement("users_list_buttons_" + userHash)
	if err != nil {
		fmt.Println(err)
		return
	}

	elBtn.EventAdd("click", func(el js.Value, evs []js.Value) {
		elOut, err := DOM.GetElement("users_out")
		if err != nil {
			fmt.Println(err)
			return
		}

		delay := 0
		if elOut.StyleGet("max-height") != "0px" {
			elOut.StyleSet("max-height", "0px")
			delay = 250
		}

		JS.AfterDelay(delay, func() {
			HTTP.Send(getUserCallback, "users", "get", el.Get("innerHTML").String())
		})
	})
}

func createUser(el js.Value, els []js.Value) {
	elsInp, err := DOM.GetElements("users_inputs")
	if err != nil {
		fmt.Println(err)
		return
	}
	elsInp.Disables()

	elSub, err := DOM.GetElement("users_submitnew")
	if err != nil {
		fmt.Println(err)
		return
	}
	elSub.Disable()

	elUsername, err := DOM.GetElement("users_username")
	if err != nil {
		fmt.Println(err)
		return
	}
	username := elUsername.AttributeGet("value")

	elPassword, err := DOM.GetElement("users_password")
	if err != nil {
		fmt.Println(err)
		return
	}
	password := elPassword.AttributeGet("value")

	elAuthlevel, err := DOM.GetElement("users_authlevel")
	if err != nil {
		fmt.Println(err)
		return
	}
	authlevel := elAuthlevel.AttributeGet("value")

	elRoles, err := DOM.GetElement("users_roles")
	if err != nil {
		fmt.Println(err)
		return
	}
	roles := elRoles.AttributeGet("value")

	elBtn, err := DOM.GetElement("users_enabled_img")
	if err != nil {
		fmt.Println(err)
		return
	}
	state := "1"
	if elBtn.AttributeGet("alt") == "Disabled" {
		state = "0"
	}

	HTTP.Send(createUserCallback, "users", "create", username, password, authlevel, roles, state)
}

func modifyUserCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	}

	elsInp, err := DOM.GetElements("users_inputs")
	if err != nil {
		fmt.Println(err)
		return
	}
	elsInp.Enables()

	elsSub, err := DOM.GetElements("users_submits")
	if err != nil {
		fmt.Println(err)
		return
	}
	elsSub.Enables()

	JS.AfterDelay(3000, func() { elsSub.StylesSet("border", "2px solid #55F") })
	if resErr != nil {
		JS.Alert(resErr.Error())
		elsSub.StylesSet("border", "2px solid #F55")
		return
	} else {
		elsSub.StylesSet("border", "2px solid #5F5")
	}

	user := User{}
	err = json.Unmarshal(resBytes, &user)
	if err != nil {
		fmt.Println(err)
		return
	}

	oldHash := HTTP.Sha1(selectedUser.Username + selectedUser.Password)
	selectedUser = user

	el, err := DOM.GetElement("users_header")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(HTTP.Sha1(selectedUser.Username + selectedUser.Password))

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		fmt.Println(err)
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
		fmt.Println("evs was not parsed")
		return
	}
	if evs[0].Get("type").String() != "click" && evs[0].Get("key").String() != "Enter" {
		return
	}

	elSub, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_") + "_submit")
	if err != nil {
		fmt.Println(err)
		return
	}

	key := strings.Split(el.Get("id").String(), "_")[1]
	elInp, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_"))
	if err != nil {
		fmt.Println(err)
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
		fmt.Println("invalid key \"" + key + "\"")
		return
	}

	elInp.Disable()
	elSub.Disable()

	HTTP.Send(modifyUserCallback, "users", "modify", HTTP.Sha1(selectedUser.Username+selectedUser.Password), key, value)
}

func deletedUserCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())

		elsInp, err := DOM.GetElements("users_inputs")
		if err != nil {
			fmt.Println(err)
			return
		}
		elsInp.Enables()

		elsSub, err := DOM.GetElements("users_submits")
		if err != nil {
			fmt.Println(err)
			return
		}
		elsSub.Enables()

		elDel, err := DOM.GetElement("users_delete")
		if err != nil {
			fmt.Println(err)
			return
		}
		elDel.Enable()

		elDea, err := DOM.GetElement("users_deauth")
		if err != nil {
			fmt.Println(err)
			return
		}
		elDea.Enable()
		return
	}

	oldHash := HTTP.Sha1(selectedUser.Username + selectedUser.Password)
	selectedUser = User{}

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		fmt.Println(err)
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
		fmt.Println(err)
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
		fmt.Println(err)
		return
	}
	elsInp.Disables()

	elsSub, err := DOM.GetElements("users_submits")
	if err != nil {
		fmt.Println(err)
		return
	}
	elsSub.Disables()

	elDel, err := DOM.GetElement("users_delete")
	if err != nil {
		fmt.Println(err)
		return
	}
	elDel.Disable()

	elDea, err := DOM.GetElement("users_deauth")
	if err != nil {
		fmt.Println(err)
		return
	}
	elDea.Disable()

	HTTP.Send(deletedUserCallback, "users", "delete", HTTP.Sha1(selectedUser.Username+selectedUser.Password))
}

func toggleEnabledCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
	}
}

func toggleEnabled(el js.Value, els []js.Value) {
	elBtn, err := DOM.GetElement("users_enabled_img")
	if err != nil {
		fmt.Println(err)
		return
	}
	state := "Disabled"
	stateCode := "0"
	if elBtn.AttributeGet("alt") == "Disabled" {
		state = "Enabled"
		stateCode = "1"
	}

	elBtn.AttributeSet("alt", state)
	elBtn.AttributeSet("src", "./docs/assets/Admin/Users/"+state+".svg")

	HTTP.Send(toggleEnabledCallback, "users", "modify", HTTP.Sha1(selectedUser.Username+selectedUser.Password), "enabled", stateCode)
}

func deauthUserCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	}

	el, err := DOM.GetElement("users_deauth")
	if err != nil {
		fmt.Println(err)
		return
	}

	if resErr != nil {
		JS.Alert(resErr.Error())
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
		fmt.Println(err)
		return
	}
	elDea.Disable()

	HTTP.Send(deauthUserCallback, "users", "deauth", "user", HTTP.Sha1(selectedUser.Username+selectedUser.Password))
}

func userListCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	users := []string{}
	err := json.Unmarshal(resBytes, &users)
	if err != nil {
		fmt.Println(err)
		return
	}

	usersList := ""
	for _, v := range users {
		usersList += HTML.HTML{Tag: "button",
			Attributes: map[string]string{"class": "dark small users_list_buttons"},
			Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
			Inner:      v,
		}.String()
	}

	el, err := DOM.GetElement("users_list")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(usersList + HTML.HTML{Tag: "button",
		Attributes: map[string]string{"id": "users_newuser", "class": "dark small"},
		Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
		Inner:      "New user",
	}.String())

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		fmt.Println(err)
		return
	}

	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		elOut, err := DOM.GetElement("users_out")
		if err != nil {
			fmt.Println(err)
			return
		}

		delay := 0
		if elOut.StyleGet("max-height") != "0px" {
			elOut.StyleSet("max-height", "0px")
			delay = 250
		}

		JS.AfterDelay(delay, func() {
			HTTP.Send(getUserCallback, "users", "get", el.Get("innerHTML").String())
		})
	})

	el, err = DOM.GetElement("users_newuser")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		elOut, err := DOM.GetElement("users_out")
		if err != nil {
			fmt.Println(err)
			return
		}

		delay := 0
		if elOut.StyleGet("max-height") != "0px" {
			elOut.StyleSet("max-height", "0px")
			delay = 250
		}

		JS.AfterDelay(delay, func() {
			newUserForm()
		})
	})
}

func getUserCallback(res string, resBytes []byte, resErr error) {
	if HTTP.IsAuthError(resErr) {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		return
	} else if resErr != nil {
		JS.Alert(resErr.Error())
		return
	}

	user := User{}
	err := json.Unmarshal(resBytes, &user)
	if err != nil {
		fmt.Println(err)
		return
	}

	getRow := func(name string, typ string, autocomplete string, value string) []string {
		id := "users_" + strings.ToLower(name)

		txt := HTML.HTML{Tag: "p", Inner: name, Styles: map[string]string{"margin": "auto 0px", "padding": "5px 0px", "background": "#1f1f1f", "border": "2px solid #111"}}.String()
		inp := HTML.HTML{Tag: "input", Attributes: map[string]string{"type": typ, "id": id, "class": "users_inputs", "autocomplete": autocomplete, "placeholder": name, "value": value}}.String()
		btn := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": id + "_submit", "class": "dark medium users_submits"}, Inner: "Submit"}.String()

		return []string{txt, inp, btn}
	}

	selectedUser = user

	gridStyle := map[string]string{"display": "grid", "grid-template-columns": "20% 60% 20%"}

	header := HTML.HTML{Tag: "h1",
		Attributes: map[string]string{"id": "users_header"},
		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
		Inner:      HTTP.Sha1(user.Username + user.Password),
	}.String()

	username := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Username", "email", "username", user.Username), "")}.String()

	password := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Password", "password", "new-password", user.Password), "")}.String()

	row := getRow("authLevel", "", "", "")
	row[1] = HTML.HTML{Tag: "select",
		Attributes: map[string]string{"id": "users_authlevel", "class": "users_inputs", "size": "1"},
		Inner: func() string {
			s := ""
			for v := range authMap {
				if v == authMapReversed[user.AuthLevel] {
					s += HTML.HTML{Tag: "option", Attributes: map[string]string{"selected": ""}, Inner: v}.String()
					continue
				}
				s += HTML.HTML{Tag: "option", Inner: v}.String()
			}
			return s
		}(),
	}.String()
	authLevel := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(row, "")}.String()

	roles := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Roles", "text", "", strings.Join(user.Roles, ", ")), "")}.String()

	state := "Disabled"
	if user.Enabled {
		state = "Enabled"
	}
	enabledBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "users_enabled", "class": "imgBtn imgBtnMedium"},
		Inner:      HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "users_enabled_img", "src": "./docs/assets/Admin/Users/" + state + ".svg", "alt": state}}.String(),
	}.String()

	trashBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "users_delete", "class": "imgBtn imgBtnMedium"},
		Inner:      HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "users_delete_img", "src": "./docs/assets/General/Trash.svg", "alt": "delete"}}.String(),
	}.String()

	deauthBtn := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "users_deauth", "class": "dark large"}, Inner: "Deauth"}.String()

	spacer := HTML.HTML{Tag: "div"}.String()
	buttons := HTML.HTML{Tag: "div", Styles: map[string]string{"display": "grid", "grid-template-columns": "5% 25% 5% 25% 5% 30% 5%"}, Inner: spacer + enabledBtn + spacer + trashBtn + spacer + deauthBtn + spacer}.String()

	el, err := DOM.GetElement("users_out")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(header + username + password + authLevel + roles + buttons)
	el.StyleSet("max-height", "100vh")

	for _, key := range []string{"username", "password", "authlevel", "roles"} {
		el, err = DOM.GetElement("users_" + key)
		if err != nil {
			fmt.Println(err)
			return
		}
		el.EventAdd("keyup", modifyUser)

		el, err = DOM.GetElement("users_" + key + "_submit")
		if err != nil {
			fmt.Println(err)
			return
		}
		el.EventAdd("click", modifyUser)
	}

	el, err = DOM.GetElement("users_enabled")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", toggleEnabled)

	el, err = DOM.GetElement("users_delete")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", deleteUser)

	el, err = DOM.GetElement("users_deauth")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", deauthUser)
}

func newUserForm() {
	getRow := func(name string, typ string, autocomplete string) []string {
		id := "users_" + strings.ToLower(name)

		txt := HTML.HTML{Tag: "p", Inner: name, Styles: map[string]string{"margin": "auto 0px", "padding": "5px 0px", "background": "#1f1f1f", "border": "2px solid #111"}}.String()
		inp := HTML.HTML{Tag: "input", Attributes: map[string]string{"type": typ, "id": id, "class": "users_inputs", "autocomplete": autocomplete, "placeholder": name}}.String()

		return []string{txt, inp}
	}

	gridStyle := map[string]string{"display": "grid", "grid-template-columns": "20% 80%"}

	header := HTML.HTML{Tag: "h1",
		Attributes: map[string]string{"id": "users_header"},
		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
		Inner:      "New User",
	}.String()

	username := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Username", "email", "username"), "")}.String()

	password := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Password", "password", "new-password"), "")}.String()

	row := getRow("authLevel", "", "")
	row[1] = HTML.HTML{Tag: "select",
		Attributes: map[string]string{"id": "users_authlevel", "class": "users_inputs", "size": "1"},
		Inner: func() string {
			s := ""
			for v := range authMap {
				if v == "user" {
					s += HTML.HTML{Tag: "option", Attributes: map[string]string{"selected": ""}, Inner: v}.String()
					continue
				}
				s += HTML.HTML{Tag: "option", Inner: v}.String()
			}
			return s
		}(),
	}.String()
	authLevel := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(row, "")}.String()

	roles := HTML.HTML{Tag: "div", Styles: gridStyle, Inner: strings.Join(getRow("Roles", "text", ""), "")}.String()

	enabledBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "users_enabled", "class": "imgBtn imgBtnMedium"},
		Inner:      HTML.HTML{Tag: "img", Attributes: map[string]string{"id": "users_enabled_img", "src": "./docs/assets/Admin/Users/Enabled.svg", "alt": "Enabled"}}.String(),
	}.String()

	submitBtn := HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "users_submitnew", "class": "dark large"}, Inner: "Confirm"}.String()

	spacer := HTML.HTML{Tag: "div"}.String()
	buttons := HTML.HTML{Tag: "div", Styles: map[string]string{"display": "grid", "grid-template-columns": "5% 25% 5% 60% 5%"}, Inner: spacer + enabledBtn + spacer + submitBtn + spacer}.String()

	el, err := DOM.GetElement("users_out")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(header + username + password + authLevel + roles + buttons)
	el.StyleSet("max-height", "100vh")

	el, err = DOM.GetElement("users_submitnew")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", createUser)
}

func PageAdminUsers() {
	if !HTTP.IsMaybeAuthenticated() {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		JS.Async(func() { ForcePage("Login") })
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Users"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_list"},
		Styles: map[string]string{
			"display":       "grid",
			"height":        "100%",
			"width":         "25%",
			"margin":        "0px 15px 0px auto",
			"background":    "#202020",
			"border":        "2px solid #111",
			"border-radius": "10px"},
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_out"},
		Styles: map[string]string{
			"width":       "75%",
			"max-height":  "0px",
			"margin":      "0px auto",
			"background":  "#202020",
			"border":      "2px solid #111",
			"transition":  "max-height 0.25s",
			"white-space": "pre",
			"font-family": "Hack",
		},
	}.String()

	mp, err := DOM.GetElement("mainpage")
	if err != nil {
		fmt.Println(err)
		return
	}
	mp.InnerSet(header + HTML.HTML{Tag: "div", Styles: map[string]string{"display": "flex"}, Inner: types + out}.String())

	HTTP.Send(userListCallback, "users", "list")
}
