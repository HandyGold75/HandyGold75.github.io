package coms

import (
	"HG75/coms/auth"
	"crypto/sha1"
	"crypto/sha512"
	"errors"
	"fmt"
	"maps"
	"net/http"
	"slices"
	"strings"
	"unicode"

	"github.com/HandyGold75/Gonos"
	"github.com/achetronic/tapogo/pkg/tapogo"
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
		AuthNotHooked, PipeNotHooked, SonosNotHooked, TapoNotHooked,
		CommandNotFound, CommandNotAuthorized,
		ArgumentInvalid, ArgumentNotBool,
		PathNotFound,
		VideoNotFound, PlugNotFound error
	}{
		AuthNotHooked: errors.New("auth not hooked"), PipeNotHooked: errors.New("pipe not hooked"), SonosNotHooked: errors.New("sonos not hooked"), TapoNotHooked: errors.New("tapo not hooked"),
		CommandNotFound: errors.New("command not found"), CommandNotAuthorized: errors.New("command not authorized"),
		ArgumentInvalid: errors.New("argument not valid"), ArgumentNotBool: errors.New("argument not true or false"),
		PathNotFound:  errors.New("path not found"),
		VideoNotFound: errors.New("video not found"), PlugNotFound: errors.New("plug not found"),
	}

	OpenDataBases = map[string]*DataBase{}

	HookAuth  *auth.Auth  = nil
	HookPipe  chan string = nil
	HookSonos             = &Gonos.ZonePlayer{}
	HookTapo              = &map[string]*tapogo.Tapo{}

	AllCommands = func() Commands {
		coms := generalCommands
		maps.Copy(coms, adminCommands)
		maps.Copy(coms, datebasesCommands)
		maps.Copy(coms, sonosCommands)
		maps.Copy(coms, tapoCommands)
		maps.Copy(coms, ytdlCommands)

		coms["help"] = Command{
			AuthLevel: auth.AuthLevelGuest, Roles: []string{},
			Description:     "Help message.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 2},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if len(args) == 0 {
					msg := "<command> [args]...\r\n" +
						"\r\nExecute server commands\r\n" +
						"\r\nAvailable:\r\n"
					for name, com := range coms {
						if com.AuthLevel > user.AuthLevel {
							continue
						} else if slices.ContainsFunc(com.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
							continue
						}

						comArgs := com.ArgsDescription
						if comArgs == "" && len(com.Commands) > 0 {
							comArgs = "["
							for subName := range com.Commands {
								comArgs += "|" + subName
							}
							comArgs = strings.Replace(comArgs, "[|", "[", 1) + "]"
						}

						msg += fmt.Sprintf("  %-10v %v\r\n", name, comArgs)
					}

					return []byte(msg), "", http.StatusOK, nil
				}

				comString := args[0]
				command, ok := coms[args[0]]
				if !ok {
					return coms["help"].Exec(user)
				}
				if command.AuthLevel > user.AuthLevel {
					return coms["help"].Exec(user)
				} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
					return coms["help"].Exec(user)
				}

				for _, p := range args[1:] {
					com, ok := command.Commands[p]
					if !ok {
						break
					}
					command = com
					comString += " " + p
					if command.AuthLevel > user.AuthLevel {
						return coms["help"].Exec(user)
					} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
						return coms["help"].Exec(user)
					}
				}

				comArgs := command.ArgsDescription
				if comArgs == "" && len(command.Commands) > 0 {
					comArgs = "["
					for subName := range command.Commands {
						comArgs += "|" + subName
					}
					comArgs = strings.Replace(comArgs, "[|", "[", 1) + "]"
				}

				msg := comString + " " + comArgs + "\r\n" +
					"\r\n" + command.Description + "\r\n"

				if len(command.Commands) > 0 {
					msg += "\r\nArguments:\r\n"
					for name, com := range command.Commands {
						if com.AuthLevel > user.AuthLevel {
							continue
						} else if slices.ContainsFunc(com.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
							continue
						}

						comArgs := com.ArgsDescription
						if comArgs == "" && len(com.Commands) > 0 {
							comArgs = "["
							for subName := range com.Commands {
								comArgs += "|" + subName
							}
							comArgs = strings.Replace(comArgs, "[|", "[", 1) + "]"
						}

						msg += fmt.Sprintf("  %-10v %v\r\n", name, comArgs)
					}
				}

				return []byte(msg), "", http.StatusOK, nil
			},
		}

		return coms
	}()
)

var generalCommands = Commands{
	"exit": {
		AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI"},
		Description:     "Stop the server.",
		AutoComplete:    []string{},
		ArgsDescription: "",
		ArgsLen:         [2]int{0, 0},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			if HookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			HookPipe <- "exit"
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
			if HookPipe == nil {
				return []byte{}, "", http.StatusInternalServerError, Errors.PipeNotHooked
			}
			HookPipe <- "restart"
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
}

// func setDebug(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
// 	if len(args) != 1 {
// 		return []byte{}, "", http.StatusBadRequest, errors.New("debug requires 1 argument")
// 	}

// 	switch args[0] {
// 	case "0":
// 		OutCh <- "debug 0"
// 		return []byte{}, "", http.StatusAccepted, nil

// 	case "1":
// 		OutCh <- "debug 1"
// 		return []byte{}, "", http.StatusAccepted, nil

// 	case "server":
// 		return []byte{}, "", http.StatusMethodNotAllowed, errors.New("unsupported from remote")

// 	case "auth":
// 		jsonBytes, err := json.Marshal(Auth.Debug())
// 		if err != nil {
// 			return []byte{}, "", http.StatusBadRequest, err
// 		}

// 		return jsonBytes, TypeJSON, http.StatusOK, nil

// 	case "https":
// 		return []byte{}, "", http.StatusMethodNotAllowed, errors.New("unsupported from remote")

// 	default:
// 	}

// 	return []byte{}, "", http.StatusBadRequest, errors.New("debug operation should be 0, 1, server, auth or https")
// }

func sanatize(title string) string {
	title = strings.Map(func(r rune) rune {
		if unicode.IsLetter(r) || unicode.IsSpace(r) || unicode.IsNumber(r) {
			return r
		}
		return -1
	}, title)
	return strings.ReplaceAll(title, "  ", " ")
}
