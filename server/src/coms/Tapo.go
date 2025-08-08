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
	"strconv"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"
)

func (c Coms) tapo() Commands {
	return Commands{"tapo": Command{
		AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
		Description: "Interact with tapo plugs.",
		Commands: Commands{
			"list": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "List available plugs.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					names := []string{}
					for name := range *c.hooks.Tapo {
						names = append(names, name)
					}
					jsonBytes, err := json.Marshal(names)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"on": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Turn plug on.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					tc, ok := (*c.hooks.Tapo)[args[0]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, Errors.PlugNotFound
					}
					_, err = tc.On()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					res, err := tc.GetDeviceInfo()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return []byte(strconv.FormatBool(res.DeviceOn)), TypeTXT, http.StatusOK, nil
				},
			},
			"off": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Turn plug off.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					tc, ok := (*c.hooks.Tapo)[args[0]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, Errors.PlugNotFound
					}
					_, err = tc.Off()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					res, err := tc.GetDeviceInfo()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return []byte(strconv.FormatBool(res.DeviceOn)), TypeTXT, http.StatusOK, nil
				},
			},
			"get": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get plug energy usage.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					tc, ok := (*c.hooks.Tapo)[args[0]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
					}
					res, err := tc.GetEnergyUsage()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(res)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"info": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get plug information.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					tc, ok := (*c.hooks.Tapo)[args[0]]
					if !ok {
						return []byte{}, "", http.StatusBadRequest, errors.New("invalid name")
					}
					res, err := tc.GetDeviceInfo()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					jsonBytes, err := json.Marshal(res)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
			"histlist": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "List available plugs and historys.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/tapo")
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
							tree[dirSplit[len(dirSplit)-2]] = append(tree[dirSplit[len(dirSplit)-2]], strings.TrimSuffix(dirSplit[len(dirSplit)-1], ".log"))
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
			"histget": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get plug energy usage history.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug] [log]",
				ArgsLen:         [2]int{2, 2},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/tapo")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					relPath := "/" + sanatize(args[0]) + "/" + sanatize(args[1]) + ".log"
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
			"histlisth": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Same as histlist but human readable.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/tapo")
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
							tree[dirSplit[len(dirSplit)-2]] = append(tree[dirSplit[len(dirSplit)-2]], strings.TrimSuffix(dirSplit[len(dirSplit)-1], ".log"))
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
			"histgeth": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Same as histget but human readable.",
				AutoComplete:    []string{},
				ArgsDescription: "[plug] [log]",
				ArgsLen:         [2]int{2, 2},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					path := cfg.CheckDirRel("data/tapo")
					if path == "" {
						return []byte{}, "", http.StatusBadRequest, Errors.PathNotFound
					}
					relPath := "/" + sanatize(args[0]) + "/" + sanatize(args[1]) + ".log"
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
			"sync": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "",
				AutoComplete:    []string{},
				ArgsDescription: "Get all plug energy usage.",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					result := map[string]any{}
					for name, tc := range *c.hooks.Tapo {
						res, err := tc.GetEnergyUsage()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						result[name] = res
					}
					jsonBytes, err := json.Marshal(result)
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					return jsonBytes, TypeJSON, http.StatusOK, nil
				},
			},
		},
	}}
}
