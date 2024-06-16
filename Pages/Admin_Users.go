//go:build js && wasm

package Pages

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/DOM"
	"HandyGold75/WebKit/HTML"
	"HandyGold75/WebKit/HTTP"
	"HandyGold75/WebKit/JS"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
	"syscall/js"
)

type (
	User struct {
		Username  string   `json:"Username"`
		Password  string   `json:"Password"`
		AuthLevel int      `json:"AuthLevel"`
		Roles     []string `json:"Roles"`
	}
)

var (
	authMap         = map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}
	authMapReversed = map[int]string{0: "guest", 1: "user", 2: "admin", 3: "owner"}

	allRoles = []string{"CLI", "Home"}

	selectedUser = User{}
)

func createUserCallback(res string, resBytes []byte, resErr error) {
	// TODO
}

func createUser(el js.Value, els []js.Value) {
	// TODO
}

func modifyUserCallback(res string, resBytes []byte, resErr error) {
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
		elsSub.StylesSet("border", "2px solid #F55")
		fmt.Println(resErr.Error())
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

	key := strings.Split(el.Get("id").String(), "_")[1]
	elInp, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_"))
	if err != nil {
		fmt.Println(err)
		return
	}

	elSub, err := DOM.GetElement(strings.Join(strings.Split(el.Get("id").String(), "_")[0:2], "_") + "_submit")
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
	if resErr != nil {
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

func deauthUserCallback(res string, resBytes []byte, resErr error) {
	el, err := DOM.GetElement("users_deauth")
	if err != nil {
		fmt.Println(err)
		return
	}

	if resErr != nil {
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
	if resErr == WebKit.ErrWebKit.HTTPUnauthorized || resErr == WebKit.ErrWebKit.HTTPNoServerSpecified {
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
	el.InnerSet(usersList)

	els, err := DOM.GetElements("users_list_buttons")
	if err != nil {
		fmt.Println(err)
		return
	}

	els.EventsAdd("click", func(el js.Value, evs []js.Value) {
		els.StylesSet("min-width", strconv.Itoa(min(5, 100/len(users)))+"%")
		els.EventsAdd("click", func(el js.Value, evs []js.Value) {
			HTTP.Send(getUserCallback, "users", "get", el.Get("innerHTML").String())
		})
	})
}

func getUserCallback(res string, resBytes []byte, resErr error) {
	user := User{}
	err := json.Unmarshal(resBytes, &user)
	if err != nil {
		fmt.Println(err)
		return
	}

	selectedUser = user

	textStyle := map[string]string{"width": "20%", "margin": "auto", "padding": "5px 0px", "background": "#1f1f1f", "border": "2px solid #111"}
	inpStyle := map[string]string{"width": "60%", "margin": "auto"}

	header := HTML.HTML{Tag: "h1",
		Attributes: map[string]string{"id": "users_header"},
		Styles:     map[string]string{"user-select": "all", "overflow-x": " scroll"},
		Inner:      HTTP.Sha1(user.Username + user.Password)}.String()

	username := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p", Inner: "Username", Styles: textStyle}.String() +
			HTML.HTML{Tag: "input",
				Attributes: map[string]string{"type": "email", "id": "users_username", "class": "users_inputs", "autocomplete": "username", "placeholder": "Username", "value": user.Username},
				Styles:     inpStyle,
			}.String() +
			HTML.HTML{Tag: "button",
				Attributes: map[string]string{"id": "users_username_submit", "class": "dark medium users_submits"},
				Inner:      "Submit"}.String(),
	}.String()

	password := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p", Inner: "Password", Styles: textStyle}.String() +
			HTML.HTML{Tag: "input",
				Attributes: map[string]string{"type": "password", "id": "users_password", "class": "users_inputs", "autocomplete": "new-password", "placeholder": "Password", "value": user.Password},
				Styles:     inpStyle,
			}.String() +
			HTML.HTML{Tag: "button",
				Attributes: map[string]string{"id": "users_password_submit", "class": "dark medium users_submits"},
				Inner:      "Submit"}.String(),
	}.String()

	authLevel := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p", Inner: "authLevel", Styles: textStyle}.String() +
			HTML.HTML{Tag: "select",
				Attributes: map[string]string{"id": "users_authlevel", "class": "users_inputs", "size": "1"},
				Styles:     inpStyle,
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
			}.String() +
			HTML.HTML{Tag: "button",
				Attributes: map[string]string{"id": "users_authlevel_submit", "class": "dark medium users_submits"},
				Inner:      "Submit"}.String(),
	}.String()

	roles := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: HTML.HTML{Tag: "p", Inner: "Password", Styles: textStyle}.String() +
			HTML.HTML{Tag: "input",
				Attributes: map[string]string{"type": "text", "id": "users_roles", "class": "users_inputs", "placeholder": "Roles", "value": strings.Join(user.Roles, ", ")},
				Styles:     inpStyle}.String() +
			HTML.HTML{Tag: "button",
				Attributes: map[string]string{"id": "users_roles_submit", "class": "dark medium users_submits"},
				Inner:      "Submit"}.String(),
	}.String()

	trashBtn := HTML.HTML{
		Tag:        "button",
		Attributes: map[string]string{"id": "users_delete", "class": "imgBtn imgBtnMedium"},
		// Styles:     map[string]string{"margin-top": "auto", "margin-bottom": "auto"},
		Inner: HTML.HTML{
			Tag:        "img",
			Attributes: map[string]string{"id": "users_delete_img", "src": "./docs/assets/General/Trash.svg", "alt": "delete"},
		}.String()}.String()

	spacer := HTML.HTML{Tag: "div"}.String()
	buttons := HTML.HTML{
		Tag:    "div",
		Styles: map[string]string{"display": "flex"},
		Inner: spacer +
			trashBtn +
			HTML.HTML{Tag: "div", Styles: map[string]string{"width": "25%"}}.String() +
			HTML.HTML{Tag: "button", Attributes: map[string]string{"id": "users_deauth", "class": "dark large"}, Inner: "Deauth"}.String() +
			spacer,
	}.String()

	el, err := DOM.GetElement("users_out")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.InnerSet(header + username + password + authLevel + roles + buttons)

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

func PageAdminUsers() {
	if !HTTP.IsMaybeAuthenticated() {
		OnLoginSuccessCallback = func() { JS.Async(func() { ForcePage("Admin:Users") }) }
		JS.Async(func() { ForcePage("Login") })
		return
	}

	header := HTML.HTML{Tag: "h1", Inner: "Users"}.String()

	types := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_list"},
		Styles: map[string]string{"display": "flex",
			"height":        "100%",
			"max-width":     "25%",
			"margin":        "0px 15px 0px 0px",
			"background":    "#202020",
			"border":        "2px solid #111",
			"border-radius": "10px"},
		Inner: HTML.HTML{Tag: "button",
			Attributes: map[string]string{"id": "users_newuser", "class": "dark small users_list_buttons"},
			Styles:     map[string]string{"white-space": "pre", "overflow-x": "scroll"},
			Inner:      "New user",
		}.String(),
	}.String()

	out := HTML.HTML{Tag: "div",
		Attributes: map[string]string{"id": "users_out"},
		Styles: map[string]string{
			"min-width":   "50%",
			"margin":      "15px auto",
			"background":  "#202020",
			"border":      "2px solid #111",
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

	el, err := DOM.GetElement("users_newuser")
	if err != nil {
		fmt.Println(err)
		return
	}
	el.EventAdd("click", func(el js.Value, evs []js.Value) {
		// TODO
	})

	HTTP.Send(userListCallback, "users", "list")
}
