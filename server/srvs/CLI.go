package srvs

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/logger"
	"golang.org/x/term"
)

type (
	CLIConfig struct{}

	CLI struct {
		lgr  *logger.Logger
		Pipe chan string
		cfg  CLIConfig
		exit bool
	}
)

var (
	AutoComplete = []string{"testest"}

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

func NewCLI(cfg CLIConfig) *CLI {
	lgr, _ := logger.NewRel("logs/cli")
	return &CLI{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *CLI) init() {
}

func (s *CLI) Run() {
	s.lgr.Log("debug", "cli", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.exit = true
				s.lgr.Log("error", "cli", fmt.Sprintf("panic:%v; recovering", rec))
			}
			close(s.Pipe)
		}()
		s.loop()
	}()
	s.lgr.Log("medium", "cli", "started")
}

func (s *CLI) Stop() {
	s.lgr.Log("debug", "cli", "stopping")
	s.exit = true
	for range s.Pipe {
	}
	s.lgr.Log("medium", "cli", "stopped")
}

func (s *CLI) loop() {
	go func() {
		for !s.exit {
			line, err := Terminal.ReadLine()
			if err != nil {
				s.Pipe <- "exit"
				continue
			} else if line != "" {
				s.Pipe <- line
			}
		}
	}()

	for !s.exit {
		time.Sleep(time.Second)
		s.lgr.Log("medium", "cli", "TEST")
	}
}
