package Services

import (
	"math/rand/v2"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	SiteConfig struct{}

	site struct {
		lgr     *logger.Logger
		Pipe    chan string
		cfg     SiteConfig
		exit    bool
		exitRes chan error
	}
)

func NewSite(lgr *logger.Logger, cfg SiteConfig) *site {
	return &site{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *site) Loop() {
	for !s.exit {
		time.Sleep(time.Second * time.Duration(rand.IntN(6)))
		s.lgr.Log("medium", "site")
	}
	s.exitRes <- nil
}

func (s *site) Stop() {
	for err := range s.exitRes {
		s.lgr.Log("error", "site", err)
	}
}
