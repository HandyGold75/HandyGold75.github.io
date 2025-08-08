package srvs

import (
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
		cfg  CLIConfig
		Pipe chan string
		exit bool
	}
)

func NewCLI(conf CLIConfig) *CLI {
	lgr, _ := logger.NewRel("data/logs/cli")

	Terminal.SetPrompt(conf.Prefix + " ")

	return &CLI{lgr: lgr, cfg: conf, Pipe: make(chan string)}
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
	s.lgr.Log("low", "cli", "started")
}

func (s *CLI) Stop() {
	s.lgr.Log("debug", "cli", "stopping")
	s.exit = true
	for range s.Pipe {
	}
	s.lgr.Log("low", "cli", "stopped")
}

func (s *CLI) loop() {
	go func() {
		s.lgr.Log("medium", "cli", "listening", "stdin/stdout")
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
