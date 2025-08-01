package coms

import (
	"HG75/auth"
	"crypto/sha1"
	"crypto/sha512"
	"encoding/json"
	"fmt"
	"net/http"
	"slices"
	"strings"
)

var adminCommands = Commands{
	"exit": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
		Description:     "Stop the server.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
			if HookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			HookPipe <- "exit"
			return []byte{}, "", http.StatusAccepted, nil
		},
	},
	"restart": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
		Description:     "Restart the server.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
			if HookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			HookPipe <- "restart"
			return []byte{}, "", http.StatusAccepted, nil
		},
	},
	"users": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
		Description: "Interact with user data.",
		Commands: Commands{
			"list": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "List user hashes.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					if HookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					hashes, err := HookAuth.ListUsers()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(hashes)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, "application/json", http.StatusOK, nil
				},
			},
			"get": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Get user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					if HookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					userData, err := HookAuth.GetUser(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, "application/json", http.StatusOK, nil
				},
			},
			"create": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Create user.",
				AutoComplete:    []string{},
				ArgsDescription: "[username] [password] [guest|user|admin] [enabled] [roles,...]",
				ArgsLen:         [2]int{3, 5},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					if HookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					enabled := false
					if len(args) > 3 {
						if args[3] != "true" && args[3] != "false" {
							return []byte{}, "", http.StatusBadRequest, Errors.ArgumentNotBool
						}
						enabled = args[3] == "true"
					}
					roles := []string{}
					if len(args) > 4 {
						roles = slices.DeleteFunc(strings.Split(args[4], ","), func(r string) bool { return r == "" })
					}

					authLevel, ok := auth.AuthMap[args[2]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, auth.Errors.InvalidAuthLevel
					}

					hash, err := HookAuth.CreateUser(auth.User{
						Username: args[0], Password: args[1],
						AuthLevel: authLevel, Roles: roles,
						Enabled: enabled,
					})
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					userData, err := HookAuth.GetUser(hash)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, "application/json", http.StatusOK, nil
				},
			},

			"modify": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Modify user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash] [username|password|authlevel|roles|enabled] [value]",
				ArgsLen:         [2]int{3, 3},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					if HookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					userData, err := HookAuth.GetUser(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}

					switch strings.ToLower(args[1]) {
					case "username":
						userData.Username = args[2]
					case "password":
						userData.Password = args[2]
					case "authlevel":
						authLevel, ok := auth.AuthMap[args[2]]
						if !ok {
							return []byte{}, "", http.StatusBadRequest, auth.Errors.InvalidAuthLevel
						}
						userData.AuthLevel = authLevel
					case "roles":
						userData.Roles = strings.Split(args[2], ",")
					case "enabled":
						if args[2] != "true" && args[2] != "false" {
							return []byte{}, "", http.StatusBadRequest, Errors.ArgumentNotBool
						}
						userData.Enabled = args[2] == "true"
					default:
						return []byte{}, "", http.StatusBadRequest, Errors.ArgumentInvalid
					}

					userHash, err := HookAuth.ModifyUser(args[0], userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					userData, err = HookAuth.GetUser(userHash)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, "application/json", http.StatusOK, nil
				},
			},

			"delete": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Delete user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					if err := HookAuth.DeleteUser(args[0]); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return []byte(args[1]), "text/plain", http.StatusOK, nil
				},
			},

			"deauth": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description: "Deauthorize user or token.",

				Commands: Commands{
					"user": Command{
						AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
						Description:     "Deauthorize user.",
						AutoComplete:    []string{},
						ArgsDescription: "[hash]",
						ArgsLen:         [2]int{1, 1},
						Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
							HookAuth.Deauthenticate(args[0])
							return []byte(args[0]), "text/plain", http.StatusOK, nil
						},
					},

					"token": Command{
						AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
						Description:     "Deauthorize token.",
						AutoComplete:    []string{},
						ArgsDescription: "[token]",
						ArgsLen:         [2]int{1, 1},
						Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
							HookAuth.DeauthenticateToken(args[0])
							return []byte(args[0]), "text/plain", http.StatusOK, nil
						},
					},
				},
			},
		},
	},
	"tools": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
		Description: "Generic tools.",
		Commands: Commands{
			"sha1": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Get sha1 of a string.",
				AutoComplete:    []string{},
				ArgsDescription: "[value]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					hasher := sha1.New()
					hasher.Write([]byte(args[0]))
					return fmt.Appendf([]byte{}, "%x", hasher.Sum(nil)), "text/plain", http.StatusOK, nil
				},
			},
			"sha512": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
				Description:     "Get sha512 of a string.",
				AutoComplete:    []string{},
				ArgsDescription: "[value]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					hasher := sha512.New()
					hasher.Write([]byte(args[0]))
					return fmt.Appendf([]byte{}, "%x", hasher.Sum(nil)), "text/plain", http.StatusOK, nil
				},
			},
		},
	},
	// "logs": {
	// 	AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
	// 	Description: "Print logs",
	// 	DetailedDescription: "Print logs of a specific day or print an list of available logs. Usage: logs [list|get|listh|geth] [args?]...\r\n" +
	// 		"  list\r\n    List available logs.\r\n" +
	// 		"  get [module] [log]\r\n    Get log.\r\n" +
	// 		"  listh\r\n    Same as list but human readable.\r\n" +
	// 		"  geth [module] [log]\r\n    Same as get but human readable.\r\n",
	// 	AutoComplete: func() []string {
	// 		completes := []string{"list", "get", "listh", "geth"}
	// 		fs.WalkDir(os.DirFS(files.LogDir), ".", func(path string, dir fs.DirEntry, err error) error {
	// 			if err != nil || path == "." {
	// 				return err
	// 			}
	// 			completes = append(completes, "get "+strings.ReplaceAll(path, "/", " "))
	// 			completes = append(completes, "geth "+strings.ReplaceAll(path, "/", " "))
	// 			return nil
	// 		})
	// 		return completes
	// 	}(),
	// 	ArgsLen:  [2]int{0, 2},
	// 	Exec:     PrintLogs,
	// 	Commands: Commands{},
	// },
	// "debug": {
	// 	AuthLevel: auth.AuthLevelAdmin, Roles: []string{"CLI"},
	// 	Description:         "Enable/ disable debugging or print debug values.",
	// 	DetailedDescription: "Enabled or disabled debugging or print debug values. Usage: debug [0|1|server|auth|https]\r\n  Restarting the server will reset the debug state to the orginial value.",
	// 	AutoComplete:        []string{},
	// 	ArgsLen:             [2]int{1, 1},
	// 	Exec:                setDebug,
	// 	Commands:            []Command{},
	// },
}
