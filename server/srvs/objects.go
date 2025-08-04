package srvs

import (
	"errors"
	"io"
	"os"
	"strings"

	"golang.org/x/term"
)

var (
	Errors = struct {
		FullchainNotFound, PrivkeyNotFound,
		MissingArgs, AdditionalArgs error
	}{
		FullchainNotFound: errors.New("fullchain not found"), PrivkeyNotFound: errors.New("privkey not found"),
		MissingArgs: errors.New("missing args"), AdditionalArgs: errors.New("additional args"),
	}

	AutoComplete = []string{"restart", "exit"}

	Terminal = func() *term.Terminal {
		if !term.IsTerminal(int(os.Stdin.Fd())) || !term.IsTerminal(int(os.Stdout.Fd())) {
			panic(errors.New("stdin/stdout should be term"))
		}
		terminal := term.NewTerminal(struct {
			io.Reader
			io.Writer
		}{os.Stdin, os.Stdout}, "> ")
		terminal.SetPrompt(string(terminal.Escape.Red) + "> " + string(terminal.Escape.Reset))
		terminal.AutoCompleteCallback = func(line string, pos int, key rune) (newLine string, newPos int, ok bool) {
			if key != 9 || line == "" {
				return line, pos, false
			}
			for _, com := range AutoComplete {
				if strings.HasPrefix(com, strings.ToLower(line)) {
					return com, len(com), true
				}
			}
			return line, pos, false
		}
		return terminal
	}()
)
