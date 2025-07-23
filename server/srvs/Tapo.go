package srvs

import (
	"fmt"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	TapoConfig struct {
		TapoPlugIPS                []string
		TapoUsername, TapoPassword string
	}

	Tapo struct {
		lgr  *logger.Logger
		Pipe chan string
		cfg  TapoConfig
		exit bool
	}
)

func NewTapo(cfg TapoConfig) *Tapo {
	lgr, _ := logger.NewRel("logs/tapo")
	return &Tapo{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *Tapo) Run() {
	s.lgr.Log("debug", "tapo", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.exit = true
				s.lgr.Log("error", "tapo", fmt.Sprintf("panic:%v; recovering", rec))
			}
			close(s.Pipe)
		}()
		s.loop()
	}()
	s.lgr.Log("medium", "tapo", "started")
}

func (s *Tapo) Stop() {
	s.lgr.Log("debug", "tapo", "stopping")
	s.exit = true
	for range s.Pipe {
	}
	s.lgr.Log("medium", "tapo", "stopped")
}

func (s *Tapo) loop() {
	for !s.exit {
		time.Sleep(time.Second)
	}
}
