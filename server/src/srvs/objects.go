package srvs

import (
	"errors"
	"fmt"
	"io"
	"os"
	"slices"
	"strconv"
	"strings"

	"golang.org/x/term"
)

var (
	Errors = struct {
		FullchainNotFound, PrivkeyNotFound,
		MissingArgs, AdditionalArgs,
		PathNotFound error
	}{
		FullchainNotFound: errors.New("fullchain not found"), PrivkeyNotFound: errors.New("privkey not found"),
		MissingArgs: errors.New("missing args"), AdditionalArgs: errors.New("additional args"),
		PathNotFound: errors.New("path not found"),
	}

	autoComplete = []string{}

	Terminal = func() *term.Terminal {
		if !term.IsTerminal(int(os.Stdin.Fd())) || !term.IsTerminal(int(os.Stdout.Fd())) {
			panic(errors.New("stdin/stdout should be term"))
		}
		terminal := term.NewTerminal(struct {
			io.Reader
			io.Writer
		}{os.Stdin, os.Stdout}, "> ")
		terminal.AutoCompleteCallback = func(line string, pos int, key rune) (newLine string, newPos int, ok bool) {
			if key == 55302 && line != "" && len([]rune(line)) >= pos+1 { // 55302 represents Unknown Key which includes DEL
				return string(slices.Delete([]rune(line), pos, pos+1)), pos, true
			} else if key != '	' || line == "" {
				_, _ = fmt.Fprint(terminal, "<"+strconv.Itoa(int(key))+">\n\r")
				return line, pos, false
			}

			options := slices.DeleteFunc(slices.Clone(autoComplete), func(v string) bool {
				return !strings.HasPrefix(v, line) || strings.Contains(strings.TrimSpace(strings.Replace(v, line, "", 1)), " ")
			})
			if len(options) < 1 {
			} else if len(options) == 1 {
				return options[0], len(options[0]), true
			} else if len(options) > 1 {
				_, _ = fmt.Fprint(terminal, "["+strings.Join(options, ", ")+"]\n\r")
			}

			return line, pos, false
		}
		return terminal
	}()
)
