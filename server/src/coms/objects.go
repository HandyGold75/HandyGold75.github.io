package coms

import (
	"HG75/auth"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/sha512"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"maps"
	"net/http"
	"slices"
	"strconv"
	"strings"
	"time"
	"unicode"

	"github.com/HandyGold75/GOLib/gapo"
	"github.com/HandyGold75/GOLib/logger"
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

	Config struct {
		DataBaseOpenTimeout int
	}
	Hooks struct {
		Auth  *auth.Auth
		Pipe  chan string
		Sonos *Gonos.ZonePlayer
		Tapo  *map[string]*gapo.Tapo
	}
	Coms struct {
		lgr      *logger.Logger
		cfg      Config
		hooks    Hooks
		Commands Commands
		dbs      map[string]*DataBase
	}
)

var Errors = struct {
	AllCommandsNotHooked, AuthNotHooked, PipeNotHooked, SonosNotHooked, TapoNotHooked,
	CommandNotFound, CommandNotAuthorized,
	ArgumentInvalid, ArgumentNotBool,
	PathNotFound,
	SheetNotFound, IndexNotFound, InvalidDataLenght, InvalidDataContent,
	VideoNotFound, PlugNotFound error
}{
	AllCommandsNotHooked: errors.New("all commands not hooked"), AuthNotHooked: errors.New("auth not hooked"), PipeNotHooked: errors.New("pipe not hooked"), SonosNotHooked: errors.New("sonos not hooked"), TapoNotHooked: errors.New("tapo not hooked"),
	CommandNotFound: errors.New("command not found"), CommandNotAuthorized: errors.New("command not authorized"),
	ArgumentInvalid: errors.New("argument not valid"), ArgumentNotBool: errors.New("argument not true or false"),
	PathNotFound:  errors.New("path not found"),
	SheetNotFound: errors.New("sheet not found"), IndexNotFound: errors.New("index not found"),
	InvalidDataLenght: errors.New("invalid data lenght"), InvalidDataContent: errors.New("invalid data content"),
	VideoNotFound: errors.New("video not found"), PlugNotFound: errors.New("plug not found"),
}

const (
	TypeTXT   = "text/plain"
	TypeJSON  = "application/json"
	TypeVideo = "video/"
	TypeMP4   = "video/mp4"
)

func NewComs(conf Config, hooks Hooks) *Coms {
	lgr, _ := logger.NewRel("data/logs/coms")
	c := &Coms{
		lgr: lgr, cfg: conf,
		hooks:    hooks,
		Commands: Commands{},
		dbs:      map[string]*DataBase{},
	}
	c.Commands = func() Commands {
		coms := c.general()
		maps.Copy(coms, c.admin())
		maps.Copy(coms, c.databases())
		maps.Copy(coms, c.sonos())
		maps.Copy(coms, c.tapo())
		maps.Copy(coms, c.ytdl())
		return coms
	}()
	return c
}

func (c *Coms) Stop() {
	for name, db := range c.dbs {
		c.lgr.Log("debug", "coms", "dumping", name)
		for _, err := range db.Dump() {
			c.lgr.Log("error", "coms", "failed", "dumping db "+name+"; error: "+err.Error())
		}
		delete(c.dbs, name)
		c.lgr.Log("low", "coms", "dumped", name)
	}
}

func (c *Coms) general() Commands {
	return Commands{
		"help": {
			AuthLevel: auth.AuthLevelGuest, Roles: []string{},
			Description:     "Help message.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 2},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
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
						getComs(c.Commands)), TypeTXT, http.StatusOK, nil
				}
				comString := args[0]
				command, ok := c.Commands[args[0]]
				if !ok {
					return c.Commands["help"].Exec(user)
				}
				if command.AuthLevel > user.AuthLevel {
					return c.Commands["help"].Exec(user)
				} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
					return c.Commands["help"].Exec(user)
				}
				for _, p := range args[1:] {
					com, ok := command.Commands[p]
					if !ok {
						break
					}
					command = com
					comString += " " + p
					if command.AuthLevel > user.AuthLevel {
						return c.Commands["help"].Exec(user)
					} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
						return c.Commands["help"].Exec(user)
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
				jsonBytes, err := json.Marshal(getComs(c.Commands, ""))
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
				c.hooks.Pipe <- "exit"
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
				c.hooks.Pipe <- "restart"
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
		"tools": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
			Description: "Generic tools.",
			Commands: Commands{
				"sha1": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha1(value))",
					AutoComplete:    []string{},
					ArgsDescription: "[value]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						hash := sha1.Sum([]byte(args[0]))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
					},
				},
				"sha256": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha256(value))",
					AutoComplete:    []string{},
					ArgsDescription: "[value]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						hash := sha256.Sum256([]byte(args[0]))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
					},
				},
				"sha512": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha512(value))",
					AutoComplete:    []string{},
					ArgsDescription: "[value]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						hash := sha512.Sum512([]byte(args[0]))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
					},
				},
				"shaUserHash": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha1(username+sha512(password)))",
					AutoComplete:    []string{},
					ArgsDescription: "[username] [password]",
					ArgsLen:         [2]int{2, 2},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						pass := sha512.Sum512([]byte(args[1]))
						hash := sha1.Sum(append([]byte(args[0]), pass[:]...))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
					},
				},
				"shaAuthHash": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha1(sha512(password)+time.Now().Format(\"2006-01-02 15:04\")))",
					AutoComplete:    []string{},
					ArgsDescription: "[password]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						pass := sha512.Sum512([]byte(args[0]))
						hash := sha1.Sum(append(pass[:], []byte(time.Now().Format("2006-01-02 15:04"))...))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
					},
				},
				"shaTapo": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"CLI"},
					Description:     "base16(sha256(sha1(email)+sha1(password)))",
					AutoComplete:    []string{},
					ArgsDescription: "[email] [password]",
					ArgsLen:         [2]int{2, 2},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						email := sha1.Sum([]byte(args[0]))
						pass := sha1.Sum([]byte(args[1]))
						hash := sha256.Sum256(append(email[:], pass[:]...))
						return []byte(hex.EncodeToString(hash[:])), TypeTXT, http.StatusOK, nil
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
				state, err := strconv.ParseBool(args[0])
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				c.hooks.Pipe <- "debug " + strconv.FormatBool(state)
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
	}
}

func sanatize(title string) string {
	title = strings.Map(func(r rune) rune {
		if unicode.IsLetter(r) || unicode.IsSpace(r) || unicode.IsNumber(r) {
			return r
		}
		return -1
	}, title)
	return strings.ReplaceAll(title, "  ", " ")
}
