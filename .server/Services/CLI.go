package Services

import (
	"math/rand/v2"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	CLIConfig struct{}

	cli struct {
		lgr     *logger.Logger
		Pipe    chan string
		cfg     CLIConfig
		exit    bool
		exitRes chan error
	}
)

func NewCLI(lgr *logger.Logger, cfg CLIConfig) *cli {
	return &cli{cfg: cfg, Pipe: make(chan string), lgr: lgr}
}

func (s *cli) Loop() {
	for !s.exit {
		time.Sleep(time.Second * time.Duration(rand.IntN(6)))
		s.lgr.Log("medium", "cli")
	}
	s.exitRes <- nil
}

func (s *cli) Stop() {
	for err := range s.exitRes {
		s.lgr.Log("error", "cli", err)
	}
}
