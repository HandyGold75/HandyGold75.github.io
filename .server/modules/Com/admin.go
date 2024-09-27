package Com

import (
	"HG75/modules/Auth"
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"strings"
	"time"
	"unicode"
)

var (
	AdminComs = Commands{
		"exit": Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Stop the server.",
			DetailedDescription: "Informs all routines to stop and then quit, the process exits when all routines have stopped.",
			ExampleDescription:  "",
			AutoComplete:        []string{},
			ArgsLen:             [2]int{0, 0},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				OutCh <- "exit"
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
		"restart": Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Restart the server.",
			DetailedDescription: "Informs all routines to stop, the routines will be started again when all routines have stopped.",
			ExampleDescription:  "",
			AutoComplete:        []string{},
			ArgsLen:             [2]int{0, 0},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				OutCh <- "restart"
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
		"users": Command{
			RequiredAuthLevel: Auth.AuthMap["admin"],
			RequiredRoles:     []string{"CLI"},
			Description:       "Interface for user managment.",
			DetailedDescription: "Interact with user data. Usage: users [list|get|create|modify|delete|deauth] [args?]...\r\n" +
				"  list\r\n    List user hashes.\r\n" +
				"  get [userHash]\r\n    Get user.\r\n" +
				"  create [username] [password] [guest|user|admin] [roles,...] [enabled]\r\n    Create user.\r\n" +
				"  modify [userHash] [username|password|authlevel|roles|enabled] [value]\r\n    Modify user.\r\n" +
				"  delete [userHash]\r\n    Delete user.\r\n" +
				"  deauth [user|token] [userHash|token]\r\n    Deauthorize user or token.",
			ExampleDescription: "get barry",
			AutoComplete:       []string{"list", "get", "create", "modify", "delete", "deauth"},
			ArgsLen:            [2]int{0, 5},
			Function:           UserInterface,
		},
		"tools": Command{
			RequiredAuthLevel: Auth.AuthMap["admin"],
			RequiredRoles:     []string{"CLI"},
			Description:       "Generic tools.",
			DetailedDescription: "Generic tools. Usage: tools [tool] [args?]...\r\n" +
				"  sha1 [arg]\r\n    Get sha1 of a string.\r\n" +
				"  sha512 [args]\r\n    Get sha512 of a string.",
			ExampleDescription: "sha1 sometext",
			AutoComplete:       []string{"sha1", "sha512"},
			ArgsLen:            [2]int{2, 2},
			Function:           ToolInterface,
		},
		"logs": Command{
			RequiredAuthLevel: Auth.AuthMap["admin"],
			RequiredRoles:     []string{"CLI"},
			Description:       "Print logs",
			DetailedDescription: "Print logs of a specific day or print an list of available logs. Usage: logs [list|get|listh|geth] [args?]...\r\n" +
				"  list\r\n    List available logs.\r\n" +
				"  get [module] [log]\r\n    Get log.\r\n" +
				"  listh\r\n    Same as list but human readable.\r\n" +
				"  geth [module] [log]\r\n    Same as get but human readable.\r\n",
			ExampleDescription: "server " + time.Now().Format("2006-01") + ".log",
			AutoComplete: func() []string {
				completes := []string{"list", "get", "listh", "geth"}
				fs.WalkDir(os.DirFS(files.LogDir), ".", func(path string, dir fs.DirEntry, err error) error {
					if err != nil || path == "." {
						return err
					}
					completes = append(completes, "get "+strings.ReplaceAll(path, "/", " "))
					completes = append(completes, "geth "+strings.ReplaceAll(path, "/", " "))
					return nil
				})
				return completes
			}(),
			ArgsLen:  [2]int{0, 2},
			Function: PrintLogs,
		},
		"debug": Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Enable/ disable debugging or print debug values.",
			DetailedDescription: "Enabled or disabled debugging or print debug values. Usage: debug [0|1|server|auth|https]\r\n  Restarting the server will reset the debug state to the orginial value.",
			ExampleDescription:  "1",
			AutoComplete:        []string{},
			ArgsLen:             [2]int{1, 1},
			Function:            setDebug,
		},
	}
)

func UserInterface(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("users requires at least 1 arguments")
	}

	switch args[0] {
	case "list":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users list requires 0 argument")
		}

		hashes, err := Auth.ListHashes()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(hashes)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "get":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users get requires 1 argument")
		}

		userData, err := Auth.GetUser(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(userData)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "create":
		if len(args) < 4 || len(args) > 6 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users create requires 3 or 5 arguments")
		}

		if len(args[1]) < 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("username should be at least 3 caracters")
		}
		for _, name := range []string{"server", "cli", "https", "owner", "auth", "com", "tapo"} {
			if strings.Contains(strings.ToLower(args[1]), name) {
				return []byte{}, "", http.StatusBadRequest, errors.New("username may not contain: " + name)
			}
		}

		if len(args[2]) < 10 {
			return []byte{}, "", http.StatusBadRequest, errors.New("password is to short")
		} else if !strings.ContainsFunc(args[2], unicode.IsLower) {
			return []byte{}, "", http.StatusBadRequest, errors.New("password does not contain a lower caracter")
		} else if !strings.ContainsFunc(args[2], unicode.IsUpper) {
			return []byte{}, "", http.StatusBadRequest, errors.New("password does not contain a upper caracter")
		} else if !strings.ContainsFunc(args[2], unicode.IsNumber) {
			return []byte{}, "", http.StatusBadRequest, errors.New("password does not contain a number caracter")
		} else if !strings.ContainsFunc(args[2], unicode.IsPunct) {
			return []byte{}, "", http.StatusBadRequest, errors.New("password does not contain a symbol caracter")
		}

		authLevel, ok := Auth.AuthMap[args[3]]
		if !ok {
			return []byte{}, "", http.StatusBadRequest, errors.New("users create type should be guest, user, admin or owner")
		}

		roles := []string{}
		if len(args) > 4 {
			roles = strings.Split(args[4], ",")
		}

		enabled := false
		if len(args) > 5 {
			if args[5] != "0" && args[5] != "1" {
				return []byte{}, "", http.StatusBadRequest, errors.New("users create enabled should be 0 or 1")
			}
			enabled = args[5] == "1"
		}

		userData := Auth.User{
			Username:  args[1],
			Password:  Auth.Sha512(args[2]),
			AuthLevel: authLevel,
			Roles:     roles,
			Enabled:   enabled,
		}

		_, err := Auth.CreateUser(userData)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(userData)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "modify":
		if len(args) != 4 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users modify requires 3 arguments")
		}

		userData, err := Auth.GetUser(args[1])
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		switch strings.ToLower(args[2]) {
		case "username":
			for _, name := range []string{"server", "cli", "https", "owner", "auth", "com", "tapo"} {
				if strings.Contains(strings.ToLower(args[3]), name) {
					return []byte{}, "", http.StatusBadRequest, errors.New("username may not contain: " + name)
				}
			}
			userData.Username = args[3]

		case "password":
			userData.Password = Auth.Sha512(args[3])

		case "authlevel":
			authLevel, ok := map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}[args[3]]
			if !ok {
				return []byte{}, "", http.StatusBadRequest, errors.New("users modify authlevel should be guest, user, admin or owner")
			}
			userData.AuthLevel = authLevel

		case "roles":
			userData.Roles = strings.Split(args[3], ",")

		case "enabled":
			if args[3] != "0" && args[3] != "1" {
				return []byte{}, "", http.StatusBadRequest, errors.New("users modify enabled should be 0 or 1")
			}
			userData.Enabled = args[3] == "1"

		default:
			return []byte{}, "", http.StatusBadRequest, errors.New("users modify key should be username, password, authlevel or roles")
		}

		userHash, err := Auth.ModifyUser(args[1], userData)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		userData, err = Auth.GetUser(userHash)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(userData)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "delete":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users delete requires 1 argument")
		}

		if err := Auth.DelUser(args[1]); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return []byte(args[1]), "text/plain", http.StatusOK, nil

	case "deauth":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("users deauth requires 2 argument")
		}

		if args[1] == "user" {
			for authToken := range Auth.GetAuthTokens(args[2]) {
				Auth.Deautherize(authToken)
			}

			return []byte(args[2]), "text/plain", http.StatusOK, nil

		} else if args[1] == "token" {
			Auth.Deautherize(args[2])
			return []byte(args[2]), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("users deauth state should be user or token")

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("users operation should be list, get, create, modify or delete")
}

func ToolInterface(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 2 {
		return []byte{}, "", http.StatusBadRequest, errors.New("tools requires at least 2 arguments")
	}

	switch args[0] {
	case "sha1":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tools sha1 requires 1 argument")
		}
		return []byte(Auth.Sha1(args[1])), "text/plain", http.StatusOK, nil

	case "sha512":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tools sha512 requires 1 argument")
		}
		return []byte(Auth.Sha512(args[1])), "text/plain", http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("tools operation should be sha1 or sha512")
}

func PrintLogs(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("logs requires at least 1 arguments")
	}

	switch args[0] {
	case "list":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("logs list requires 0 argument")
		}

		tree := map[string][]string{}
		if _, err := os.Stat(files.LogDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		fs.WalkDir(os.DirFS(files.LogDir), ".", func(path string, dir fs.DirEntry, err error) error {
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
		})

		jsonBytes, err := json.Marshal(tree)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "get":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("logs get requires 2 arguments")
		}

		if _, err := os.Stat(files.LogDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		relPath := "/" + strings.Join(args[1:3], "/")
		if fileInfo, err := os.Stat(files.LogDir + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
			return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
		}

		tree := []string{}

		file, err := os.Open(files.LogDir + relPath)
		if err != nil {
			return []byte{}, "", http.StatusInternalServerError, err
		}
		defer file.Close()

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

		return jsonBytes, "application/json", http.StatusOK, nil

	case "listh":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("logs listh requires 0 argument")
		}

		tree := map[string][]string{}
		if _, err := os.Stat(files.LogDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		fs.WalkDir(os.DirFS(files.LogDir), ".", func(path string, dir fs.DirEntry, err error) error {
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
		})

		jsonBytes, err := json.MarshalIndent(tree, "\r", "\t")
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "geth":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("logs geth requires 2 arguments")
		}

		if _, err := os.Stat(files.LogDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		relPath := "/" + strings.Join(args[1:3], "/")
		if fileInfo, err := os.Stat(files.LogDir + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
			return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
		}

		tree := ""

		file, err := os.Open(files.LogDir + relPath)
		if err != nil {
			return []byte{}, "", http.StatusInternalServerError, err
		}
		defer file.Close()

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

			for i, v := range strings.Split(strings.Replace(line, lgr.EORSepperator, "", 1), lgr.RecordSepperator) {
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

		return []byte(tree), "text/plain", http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("logs operation should be list, get, listh or geth")
}

func setDebug(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) != 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("debug requires 1 argument")
	}

	switch args[0] {
	case "0":
		OutCh <- "debug 0"
		return []byte{}, "", http.StatusAccepted, nil

	case "1":
		OutCh <- "debug 1"
		return []byte{}, "", http.StatusAccepted, nil

	case "server":
		return []byte{}, "", http.StatusMethodNotAllowed, errors.New("unsupported from remote")

	case "auth":
		jsonBytes, err := json.Marshal(Auth.Debug())
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "https":
		return []byte{}, "", http.StatusMethodNotAllowed, errors.New("unsupported from remote")

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("debug operation should be 0, 1, server, auth or https")
}
