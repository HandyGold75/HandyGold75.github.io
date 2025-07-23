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
	"strconv"
	"strings"
	"time"
)

var TapoComs = Commands{
	"tapo": Command{
		RequiredAuthLevel: Auth.AuthMap["user"],
		RequiredRoles:     []string{"Home"},
		Description:       "Tapo interface.",
		DetailedDescription: "Interact with tapo plugs. Usage: tapo [list|on|off|get|info|histlist|histget|histlisth|histgeth|sync] [args?]...\r\n" +
			"  list\r\n    List available plugs.\r\n" +
			"  on [plug]\r\n    Turn plug on.\r\n" +
			"  off [plug]\r\n    Turn plug off.\r\n" +
			"  get [plug]\r\n    Get plug energy usage.\r\n" +
			"  info [plug]\r\n    Get plug information.\r\n" +
			"  histlist\r\n    List available plugs and historys.\r\n" +
			"  histget [plug] [history]\r\n    Get plug energy usage history.\r\n" +
			"  histlisth\r\n    Same as histlist but human readable.\r\n" +
			"  histgeth [module] [log]\r\n    Same as histget but human readable.\r\n" +
			"  sync\r\n    Get all plug energy usage.\r\n",
		ExampleDescription: "list",
		AutoComplete:       []string{"list", "on", "off", "get", "info", "histlist", "histget", "histlisth", "histgeth", "sync"},
		ArgsLen:            [2]int{1, 5},
		Function:           TapoInterface,
	},
}

func TapoInterface(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("tapo requires at least 1 argument")
	}

	switch args[0] {
	case "list":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo on requires 0 argument")
		}

		plugNames := []string{}
		for tcName := range TapoClients {
			plugNames = append(plugNames, tcName)
		}

		jsonBytes, err := json.Marshal(plugNames)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "on":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo on requires 1 argument")
		}

		tc, ok := TapoClients[args[1]]
		if !ok {
			return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
		}

		_, err := tc.TurnOn()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		res, err := tc.DeviceInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return []byte(strconv.FormatBool(res.Result.DeviceOn)), "text/plain", http.StatusOK, nil

	case "off":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo off requires 1 argument")
		}

		tc, ok := TapoClients[args[1]]
		if !ok {
			return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
		}

		_, err := tc.TurnOff()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		res, err := tc.DeviceInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return []byte(strconv.FormatBool(res.Result.DeviceOn)), "text/plain", http.StatusOK, nil

	case "get":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo get requires 1 argument")
		}

		tc, ok := TapoClients[args[1]]
		if !ok {
			return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
		}

		res, err := tc.GetEnergyUsage()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(res.Result)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "info":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo info requires 1 argument")
		}

		tc, ok := TapoClients[args[1]]
		if !ok {
			return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
		}

		res, err := tc.DeviceInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(res.Result)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "histlist":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo histlist requires 0 argument")
		}

		tree := map[string][]string{}
		if _, err := os.Stat(files.TapoDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		fs.WalkDir(os.DirFS(files.TapoDir), ".", func(path string, dir fs.DirEntry, err error) error {
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

	case "histget":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo histget requires 2 arguments")
		}

		if _, err := os.Stat(files.TapoDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		relPath := "/" + strings.Join(args[1:3], "/")
		if fileInfo, err := os.Stat(files.TapoDir + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
			return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
		}

		tree := []string{}

		file, err := os.Open(files.TapoDir + relPath)
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

	case "histlisth":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo listh requires 0 argument")
		}

		tree := map[string][]string{}
		if _, err := os.Stat(files.TapoDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		fs.WalkDir(os.DirFS(files.TapoDir), ".", func(path string, dir fs.DirEntry, err error) error {
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

	case "histgeth":
		if len(args) != 3 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo geth requires 2 arguments")
		}

		if _, err := os.Stat(files.TapoDir); os.IsNotExist(err) {
			return []byte{}, "", http.StatusNotFound, err
		}

		relPath := "/" + strings.Join(args[1:3], "/")
		if fileInfo, err := os.Stat(files.TapoDir + relPath); os.IsNotExist(err) || fileInfo.IsDir() {
			return []byte{}, "", http.StatusNotFound, errors.New("file does not exists")
		}

		tree := ""

		file, err := os.Open(files.TapoDir + relPath)
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

	case "sync":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("tapo sync requires 0 argument")
		}

		result := map[string]any{}
		for tcName, tcClient := range TapoClients {
			res, err := tcClient.GetEnergyUsage()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			result[tcName] = res.Result
		}

		jsonBytes, err := json.Marshal(result)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("tapo operation should be list, on, off, get, info, histlist, histget histlisth, histgeth or sync")
}
