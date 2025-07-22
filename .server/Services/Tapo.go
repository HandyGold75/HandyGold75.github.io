package Services

import (
	"math/rand/v2"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	TapoConfig struct {
		TapoPlugIPS                []string
		TapoUsername, TapoPassword string
	}

	tapo struct {
		lgr     *logger.Logger
		Pipe    chan string
		cfg     TapoConfig
		exit    bool
		exitRes chan error
	}
)

func NewTapo(lgr *logger.Logger, cfg TapoConfig) *tapo {
	return &tapo{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *tapo) Loop() {
	for !s.exit {
		time.Sleep(time.Second * time.Duration(rand.IntN(6)))
		s.lgr.Log("medium", "tapo")
	}
	s.exitRes <- nil
}

func (s *tapo) Stop() {
	for err := range s.exitRes {
		s.lgr.Log("error", "tapo", err)
	}
}
