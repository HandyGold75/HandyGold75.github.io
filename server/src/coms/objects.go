package coms

import (
	"HG75/auth"
	"crypto/sha1"
	"crypto/sha512"
	"encoding/json"
	"errors"
	"fmt"
	"maps"
	"net/http"
	"slices"
	"strconv"
	"strings"
	"unicode"

	"github.com/HandyGold75/GOLib/gapo"
	"github.com/HandyGold75/Gonos"
)

type (
	Command struct {
		AuthLevel       auth.AuthLevel
		Roles           []string
		Description     string
		AutoComplete    []string
		ArgsDescription string
		ArgsLen         [2]int
		Exec            func(user auth.User, args ...string) (con []byte, typ string, code int, err error)
		Commands        Commands
	}

	Commands = map[string]Command
)

const (
	TypeTXT   = "text/plain"
	TypeJSON  = "application/json"
	TypeVideo = "video/"
	TypeMP4   = "video/mp4"
)

var (
	Errors = struct {
		AllCommandsNotHooked, AuthNotHooked, PipeNotHooked, SonosNotHooked, TapoNotHooked,
		CommandNotFound, CommandNotAuthorized,
		ArgumentInvalid, ArgumentNotBool,
		PathNotFound,
		VideoNotFound, PlugNotFound error
	}{
		AllCommandsNotHooked: errors.New("all commands not hooked"), AuthNotHooked: errors.New("auth not hooked"), PipeNotHooked: errors.New("pipe not hooked"), SonosNotHooked: errors.New("sonos not hooked"), TapoNotHooked: errors.New("tapo not hooked"),
		CommandNotFound: errors.New("command not found"), CommandNotAuthorized: errors.New("command not authorized"),
		ArgumentInvalid: errors.New("argument not valid"), ArgumentNotBool: errors.New("argument not true or false"),
		PathNotFound:  errors.New("path not found"),
		VideoNotFound: errors.New("video not found"), PlugNotFound: errors.New("plug not found"),
	}

	OpenDataBases = map[string]*DataBase{}

	HookAllCommands *Commands              = nil
	hookAuth        *auth.Auth             = nil
	hookPipe        chan string            = nil
	hookSonos       *Gonos.ZonePlayer      = nil
	hookTapo        *map[string]*gapo.Tapo = nil

	AllCommands = func() Commands {
		coms := generalCommands
		maps.Copy(coms, adminCommands)
		maps.Copy(coms, datebasesCommands)
		maps.Copy(coms, sonosCommands)
		maps.Copy(coms, tapoCommands)
		maps.Copy(coms, ytdlCommands)
		return coms
	}()
)

var generalCommands = Commands{
	"help": {
		AuthLevel: auth.AuthLevelGuest, Roles: []string{},
		Description:     "Help message.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 2},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if HookAllCommands == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.AllCommandsNotHooked
			}
			getArgs := func(command Command) string {
				ret := command.ArgsDescription
				if ret == "" && len(command.Commands) > 0 {
					ret = "["
					for name := range command.Commands {
						ret += "|" + name
					}
					ret = strings.Replace(ret, "[|", "[", 1) + "]"
				}
				return ret
			}
			getComs := func(commands Commands) string {
				msg := ""
				for name, com := range commands {
					if com.AuthLevel > user.AuthLevel {
						continue
					} else if slices.ContainsFunc(com.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
						continue
					}
					msg += fmt.Sprintf("  %-10v %v\r\n", name, getArgs(com))
				}
				return msg
			}
			if len(args) == 0 {
				return []byte("<command> [args]...\r\n" +
					"\r\nExecute server commands.\r\n" +
					"\r\nAvailable:\r\n" +
					getComs(*HookAllCommands)), "", http.StatusOK, nil
			}
			comString := args[0]
			command, ok := (*HookAllCommands)[args[0]]
			if !ok {
				return (*HookAllCommands)["help"].Exec(user)
			}
			if command.AuthLevel > user.AuthLevel {
				return (*HookAllCommands)["help"].Exec(user)
			} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
				return (*HookAllCommands)["help"].Exec(user)
			}
			for _, p := range args[1:] {
				com, ok := command.Commands[p]
				if !ok {
					break
				}
				command = com
				comString += " " + p
				if command.AuthLevel > user.AuthLevel {
					return (*HookAllCommands)["help"].Exec(user)
				} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
					return (*HookAllCommands)["help"].Exec(user)
				}
			}
			msg := comString + " " + getArgs(command) + "\r\n" +
				"\r\n" + command.Description + "\r\n"
			if len(command.Commands) > 0 {
				msg += "\r\nArguments:\r\n" + getComs(command.Commands)
			}
			return []byte(msg), TypeTXT, http.StatusOK, nil
		},
	},
	"autocomplete": {
		AuthLevel: auth.AuthLevelGuest, Roles: []string{},
		Description:     "Get autocompletes.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if HookAllCommands == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.AllCommandsNotHooked
			}
			var getComs func(commands Commands, prefix string) []string
			getComs = func(commands Commands, prefix string) []string {
				ret := []string{}
				for name, command := range commands {
					if command.AuthLevel > user.AuthLevel {
						continue
					} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
						continue
					}
					ret = append(ret, prefix+name)
				}
				for name, command := range commands {
					if command.AuthLevel > user.AuthLevel {
						continue
					} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
						continue
					}
					if len(command.Commands) > 0 {
						ret = append(ret, getComs(command.Commands, prefix+name+" ")...)
					}
				}
				return ret
			}
			jsonBytes, err := json.Marshal(getComs(*HookAllCommands, ""))
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			return jsonBytes, TypeJSON, http.StatusOK, nil
		},
	},
	"exit": {
		AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI"},
		Description:     "Stop the server.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if hookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			hookPipe <- "exit"
			return []byte{}, "", http.StatusAccepted, nil
		},
	},
	"restart": {
		AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI"},
		Description:     "Restart the server.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if hookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			hookPipe <- "restart"
			return []byte{}, "", http.StatusAccepted, nil
		},
	},
	"tools": {
		AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
		Description: "Generic tools.",
		Commands: Commands{
			"sha1": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
				Description:     "Get sha1 of a string.",
				AutoComplete:    []string{},
				ArgsDescription: "[value]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					hasher := sha1.New()
					hasher.Write([]byte(args[0]))
					return fmt.Appendf([]byte{}, "%x", hasher.Sum(nil)), TypeTXT, http.StatusOK, nil
				},
			},
			"sha512": {
				AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
				Description:     "Get sha512 of a string.",
				AutoComplete:    []string{},
				ArgsDescription: "[value]",
				ArgsLen:         [2]int{1, 1},
				Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
					hasher := sha512.New()
					hasher.Write([]byte(args[0]))
					return fmt.Appendf([]byte{}, "%x", hasher.Sum(nil)), TypeTXT, http.StatusOK, nil
				},
			},
		},
	},
	"debug": {
		AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI"},
		Description:     "Enable or disable debuging.",
		AutoComplete:    []string{},
		ArgsDescription: "[true|false]",
		ArgsLen:         [2]int{1, 1},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if hookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			state, err := strconv.ParseBool(args[0])
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			hookPipe <- "debug " + strconv.FormatBool(state)
			return []byte{}, "", http.StatusAccepted, nil
		},
	},
}

func Hook(auth *auth.Auth, pipe chan string, sonos *Gonos.ZonePlayer, tapo *map[string]*gapo.Tapo) {
	HookAllCommands, hookAuth, hookPipe, hookSonos, hookTapo = &AllCommands, auth, pipe, sonos, tapo
}
func Unhook() { Hook(nil, nil, nil, nil) }

func sanatize(title string) string {
	title = strings.Map(func(r rune) rune {
		if unicode.IsLetter(r) || unicode.IsSpace(r) || unicode.IsNumber(r) {
			return r
		}
		return -1
	}, title)
	return strings.ReplaceAll(title, "  ", " ")
}
