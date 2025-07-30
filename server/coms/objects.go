package coms

import (
	"errors"
	"maps"

	"HG75/auth"
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
		ArgumentInvalid, ArgumentNotBool error
	}{
		AuthNotHooked:   errors.New("auth not hooked"),
		PipeNotHooked:   errors.New("pipe not hooked"),
		ArgumentInvalid: errors.New("argument not valid"),
		ArgumentNotBool: errors.New("argument not true or false"),
	}

	HookAuth *auth.Auth  = nil
	HookPipe chan string = nil

	AllCommands = func() Commands {
		coms := Commands{}
		maps.Copy(coms, adminCommands)
		return coms
	}()
)
