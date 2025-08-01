package coms

import (
	"HG75/auth"
	"errors"
	"fmt"
	"maps"
	"net/http"
	"slices"
	"strings"

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
		Exec            func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error)
		Commands        Commands
	}

	Commands = map[string]Command
)

var (
	Errors = struct {
		AuthNotHooked, PipeNotHooked,
		CommandNotFound,
		ArgumentInvalid, ArgumentNotBool error
	}{
		AuthNotHooked:   errors.New("auth not hooked"),
		PipeNotHooked:   errors.New("pipe not hooked"),
		CommandNotFound: errors.New("unknown command"),
		ArgumentInvalid: errors.New("argument not valid"),
		ArgumentNotBool: errors.New("argument not true or false"),
	}

	HookAuth  *auth.Auth  = nil
	HookPipe  chan string = nil
	HookSonos             = &Gonos.ZonePlayer{}
	HookTapo              = &map[string]*tapogo.Tapo{}

	AllCommands = func() Commands {
		coms := generalCommands
		maps.Copy(coms, adminCommands)
		maps.Copy(coms, datebasesCommands)
		maps.Copy(coms, sonosCommands)

		coms["help"] = Command{
			AuthLevel: auth.AuthLevelGuest, Roles: []string{},
			Description:     "Help message.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 2},
			Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
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

var generalCommands = Commands{}
