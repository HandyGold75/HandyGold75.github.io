package srvs

import (
	"HG75/auth"
	"HG75/coms"
	"encoding/json"
	"io"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	CLIConfig struct {
		Prefix string
	}

	CLI struct {
		lgr  *logger.Logger
		Pipe chan string
		cfg  CLIConfig
		exit bool
	}
)

var CLIUser = auth.User{
	Username: "owner", Password: "",
	AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI", "Home"},
	Enabled: true,
}

func NewCLI(conf CLIConfig) *CLI {
	lgr, _ := logger.NewRel("data/logs/cli")

	Terminal.SetPrompt(conf.Prefix + " ")

	coms.HookAllCommands = &coms.AllCommands
	if con, _, _, err := coms.AllCommands["autocomplete"].Exec(CLIUser); err != nil {
		lgr.Log("error", "cli", "failed", "fetching autocomplete; error: "+err.Error())
	} else if err := json.Unmarshal(con, &autoComplete); err != nil {
		lgr.Log("error", "cli", "failed", "fetching autocomplete; error: "+err.Error())
	}

	return &CLI{cfg: conf, Pipe: make(chan string), lgr: lgr}
}

func (s *CLI) Run() {
	s.lgr.Log("debug", "cli", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.lgr.Log("error", "cli", "panic", rec)
			}
			s.exit = true
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
			if s.exit {
				break
			} else if err != nil {
				if err == io.EOF {
					s.Pipe <- "exit"
				}
				s.exit = true
				break
			} else if line != "" {
				s.Pipe <- line
			}
		}
	}()

	for !s.exit {
		time.Sleep(time.Second)
	}
}
