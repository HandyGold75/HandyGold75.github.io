package srvs

import (
	"io"
	"time"

	"github.com/HandyGold75/GOLib/logger"
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

func NewCLI(conf CLIConfig) *CLI {
	lgr, _ := logger.NewRel("data/logs/cli")
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
			if err != nil {
				if err == io.EOF {
					s.Pipe <- "exit"
				}
				s.exit = true
				break
			} else if line != "" {
				s.Pipe <- line // Somehow sometimes something gets send here after exit or ctrl_c command
			}
		}
	}()

	for !s.exit {
		time.Sleep(time.Second)
	}
}
