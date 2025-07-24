package srvs

import (
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	SiteConfig struct {
		SonosIP string
	}

	Site struct {
		lgr  *logger.Logger
		Pipe chan string
		cfg  SiteConfig
		exit bool
	}
)

func NewSite(cfg SiteConfig) *Site {
	lgr, _ := logger.NewRel("data/logs/site")
	return &Site{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *Site) Run() {
	s.lgr.Log("debug", "site", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.lgr.Log("error", "site", "panic", rec)
			}
			s.exit = true
			close(s.Pipe)
		}()
		s.loop()
	}()
	s.lgr.Log("medium", "site", "started")
}

func (s *Site) Stop() {
	s.lgr.Log("debug", "site", "stopping")
	s.exit = true
	for range s.Pipe {
	}
	s.lgr.Log("medium", "site", "stopped")
}

func (s *Site) loop() {
	for !s.exit {
		time.Sleep(time.Second)
	}
}
