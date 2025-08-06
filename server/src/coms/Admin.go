package coms

import (
	"HG75/auth"
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"
)

var adminCommands = Commands{
	"users": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
		Description: "Interact with user data.",
		Commands: Commands{
			"list": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "List user hashes.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					hashes, err := hookAuth.ListUsers()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(hashes)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"get": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Get user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					userData, err := hookAuth.GetUser(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"create": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Create user.",
				AutoComplete:    []string{},
				ArgsDescription: "[username] [password] [guest|user|admin] [enabled] [roles,...]",
				ArgsLen:         [2]int{3, 5},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					enabled := false
					if len(args) > 3 {
						state, err := strconv.ParseBool(args[3])
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						enabled = state
					}
					roles := []string{}
					if len(args) > 4 {
						roles = slices.DeleteFunc(strings.Split(args[4], ","), func(r string) bool { return r == "" })
					}
					authLevel, ok := auth.AuthMap[args[2]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, auth.Errors.InvalidAuthLevel
					}
					if authLevel > user.AuthLevel {
						return []byte{}, "", http.StatusBadRequest, Errors.CommandNotAuthorized
					}
					hash, err := hookAuth.CreateUser(auth.User{
						Username: args[0], Password: args[1],
						AuthLevel: authLevel, Roles: roles,
						Enabled: enabled,
					})
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					userData, err := hookAuth.GetUser(hash)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"modify": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Modify user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash] [username|password|authlevel|roles|enabled] [value]",
				ArgsLen:         [2]int{3, 3},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					userData, err := hookAuth.GetUser(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if userData.AuthLevel > user.AuthLevel {
						return []byte{}, "", http.StatusBadRequest, Errors.CommandNotAuthorized
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
						if authLevel > user.AuthLevel {
							return []byte{}, "", http.StatusBadRequest, Errors.CommandNotAuthorized
						}
						userData.AuthLevel = authLevel
					case "roles":
						userData.Roles = strings.Split(args[2], ",")
					case "enabled":
						state, err := strconv.ParseBool(args[2])
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						userData.Enabled = state
					default:
						return []byte{}, "", http.StatusBadRequest, Errors.ArgumentInvalid
					}
					userHash, err := hookAuth.ModifyUser(args[0], userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					userData, err = hookAuth.GetUser(userHash)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(userData)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"delete": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Delete user.",
				AutoComplete:    []string{},
				ArgsDescription: "[hash]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					userData, err := hookAuth.GetUser(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if userData.AuthLevel > user.AuthLevel {
						return []byte{}, "", http.StatusBadRequest, Errors.CommandNotAuthorized
					}
					if err := hookAuth.DeleteUser(args[0]); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return []byte(args[0]), TypeTXT, http.StatusOK, nil
				},
			},
			"deauth": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description: "Deauthorize user or token.",
				Commands: Commands{
					"user": {
						AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
						Description:     "Deauthorize user.",
						AutoComplete:    []string{},
						ArgsDescription: "[hash]",
						ArgsLen:         [2]int{1, 1},
						Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
							if hookAuth == nil {
								return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
							}
							hookAuth.Deauthenticate(args[0])
							return []byte(args[0]), TypeTXT, http.StatusOK, nil
						},
					},
					"token": {
						AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
						Description:     "Deauthorize token.",
						AutoComplete:    []string{},
						ArgsDescription: "[token]",
						ArgsLen:         [2]int{1, 1},
						Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
							if hookAuth == nil {
								return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
							}
							hookAuth.DeauthenticateToken(args[0])
							return []byte(args[0]), TypeTXT, http.StatusOK, nil
						},
					},
				},
			},
		},
	},
	"tokens": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
		Description: "Interact with user data.",
		Commands: Commands{
			"list": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "List tokens.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					data := hookAuth.ListTokens()
					jsonBytes, err := json.Marshal(data)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"get": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Get token.",
				AutoComplete:    []string{},
				ArgsDescription: "[token]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					data, err := hookAuth.GetToken(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(data)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"geth": {
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Get token in human readable format..",
				AutoComplete:    []string{},
				ArgsDescription: "[token]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					if hookAuth == nil {
						return []byte{}, "", http.StatusInternalServerError, Errors.AuthNotHooked
					}
					data, err := hookAuth.GetToken(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.MarshalIndent(data, "\r", "\t")
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
		},
	},
	"logs": {
		AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
		Description: "Interact with log data.",
		// AutoComplete: func() []string {
		// 	completes := []string{"list", "get", "listh", "geth"}
		// 	fs.WalkDir(os.DirFS(files.LogDir), ".", func(path string, dir fs.DirEntry, err error) error {
		// 		if err != nil || path == "." {
		// 			return err
		// 		}
		// 		completes = append(completes, "get "+strings.ReplaceAll(path, "/", " "))
		// 		completes = append(completes, "geth "+strings.ReplaceAll(path, "/", " "))
		// 		return nil
		// 	})
		// 	return completes
		// }(),
		ArgsLen: [2]int{0, 2},
		Commands: Commands{
			"list": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "List available logs.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/logs")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					tree := map[string][]string{}
					if err := fs.WalkDir(os.DirFS(path), ".", func(path string, dir fs.DirEntry, err error) error {
						if err != nil || path == "." {
							return err
						}
						dirSplit := strings.Split(path, "/")
						if dir.IsDir() {
							if _, ok := tree[dirSplit[len(dirSplit)-1]]; !ok {
								tree[dirSplit[len(dirSplit)-1]] = []string{}
							}
						} else {
							tree[dirSplit[len(dirSplit)-2]] = append(tree[dirSplit[len(dirSplit)-2]], dirSplit[len(dirSplit)-1])
						}
						return nil
					}); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(tree)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"get": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Get log.",
				AutoComplete:    []string{},
				ArgsDescription: "[module] [log]",
				ArgsLen:         [2]int{2, 2},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/logs")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					relPath := "/" + sanatize(strings.Join(args[0:2], "/"))
					if fileInfo, err := os.Stat(path + "/" + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
						return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
					}
					tree := []string{}
					file, err := os.Open(path + "/" + relPath)
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
					defer func() { _ = file.Close() }()
					reader := bufio.NewReader(file)
					for {
						line, err := reader.ReadString('\n')
						if err == io.EOF {
							break
						}
						if err != nil {
							return []byte{}, "", http.StatusInternalServerError, err
						}
						tree = append(tree, line)
					}
					jsonBytes, err := json.Marshal(tree)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"listh": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "List available logs in human readable format.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/logs")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					tree := map[string][]string{}
					if err := fs.WalkDir(os.DirFS(path), ".", func(path string, dir fs.DirEntry, err error) error {
						if err != nil || path == "." {
							return err
						}
						dirSplit := strings.Split(path, "/")
						if dir.IsDir() {
							if _, ok := tree[dirSplit[len(dirSplit)-1]]; !ok {
								tree[dirSplit[len(dirSplit)-1]] = []string{}
							}
						} else {
							tree[dirSplit[len(dirSplit)-2]] = append(tree[dirSplit[len(dirSplit)-2]], dirSplit[len(dirSplit)-1])
						}
						return nil
					}); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.MarshalIndent(tree, "\r", "\t")
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"geth": Command{
				AuthLevel: auth.AuthLevelAdmin, Roles: []string{},
				Description:     "Get log in human readable format.",
				AutoComplete:    []string{},
				ArgsDescription: "[module] [log]",
				ArgsLen:         [2]int{2, 2},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/logs")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					relPath := "/" + sanatize(strings.Join(args[0:2], "/"))
					if fileInfo, err := os.Stat(path + "/" + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
						return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
					}
					tree := ""
					file, err := os.Open(path + "/" + relPath)
					if err != nil {
						return []byte{}, "", http.StatusInternalServerError, err
					}
					defer func() { _ = file.Close() }()
					reader := bufio.NewReader(file)
					for {
						line, err := reader.ReadString('\n')
						if err == io.EOF {
							break
						}
						if err != nil {
							return []byte{}, "", http.StatusInternalServerError, err
						}
						tree += "\r"
						// TODO: Change logger.* to actual configuration instead of default value.
						for i, v := range strings.Split(strings.Replace(line, logger.EORSepperator, "", 1), logger.RecordSepperator) {
							if i == 0 {
								t, err := time.Parse(time.RFC3339Nano, v)
								if err == nil {
									tree += t.Format(time.DateTime) + " "
									continue
								}
							}
							tree += fmt.Sprintf("%-10v ", v)
						}
						tree += "\n"
					}
					return []byte(tree), TypeTXT, http.StatusOK, nil
				},
			},
		},
	},
}
