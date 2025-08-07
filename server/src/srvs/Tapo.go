package srvs

import (
	"encoding/base64"
	"time"

	"github.com/HandyGold75/GOLib/gapo"
	"github.com/HandyGold75/GOLib/logger"
	"github.com/HandyGold75/GOLib/scheduler"
)

type (
	TapoConfig struct {
		PlugIPS  []string
		AuthHash string
		Schedule scheduler.Schedule
	}

	Tapo struct {
		lgr     *logger.Logger
		Pipe    chan string
		cfg     TapoConfig
		exit    bool
		clients map[string]*gapo.Tapo
	}
)

func NewTapo(conf TapoConfig) *Tapo {
	lgr, _ := logger.NewRel("data/logs/tapo")

	clients := map[string]*gapo.Tapo{}
	for _, ip := range conf.PlugIPS {
		var e error
		for i := range 11 {
			if i == 10 {
				lgr.Log("error", "tapo", "failed", "connecting to tapo plug: "+ip+"; error: "+e.Error())
				break
			}
			tc, err := gapo.NewTapoHash(ip, conf.AuthHash)
			if err != nil {
				e = err
				continue
			}
			tcInfo, err := tc.GetDeviceInfo()
			if err != nil {
				e = err
				continue
			}
			nickname, err := base64.StdEncoding.DecodeString(tcInfo.Nickname)
			if err != nil {
				e = err
				continue
			}
			clients[string(nickname[:])] = tc
			lgr.Log("low", "tapo", "connected", "tapo plug: "+ip)
			break
		}
	}

	return &Tapo{
		cfg: conf, Pipe: make(chan string), lgr: lgr,
		clients: clients,
	}
}

func (s *Tapo) Run() {
	s.lgr.Log("debug", "tapo", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.lgr.Log("error", "tapo", "panic", rec)
			}
			s.exit = true
			close(s.Pipe)
		}()
		s.loop()
	}()
	s.lgr.Log("low", "tapo", "started")
}

func (s *Tapo) Stop() {
	s.lgr.Log("debug", "tapo", "stopping")
	s.exit = true
	for range s.Pipe {
	}
	s.lgr.Log("low", "tapo", "stopped")
}

func (s *Tapo) loop() {
	for !s.exit {
		nextLogging := time.Now()
		if err := scheduler.SetNextTime(&nextLogging, s.cfg.Schedule); err != nil {
			break
		}

		if time.Until(nextLogging) > 0 {
			s.lgr.Log("medium", "tapo", "sceduled", nextLogging.Format(time.DateTime))
			scheduler.SleepUntilFunc(func(t time.Duration) bool { return !s.exit }, nextLogging, time.Second)
			if s.exit {
				break
			}
		}

		failed := false
		for tcName, tc := range s.clients {
			tcLgr, _ := logger.NewRel("data/tapo/" + tcName)
			tcLgr.Verbosities = map[string]int{"error": 1, "info": 0}
			tcLgr.VerboseToCLI, tcLgr.VerboseToFile = 2, 0
			tcLgr.DynamicFileName = func() string { return time.Now().Format("2006") + ".log" }

			usage, err := tc.GetEnergyUsage()
			if err != nil {
				failed = true
				tcLgr.Log("error", err)
				s.lgr.Log("error", "tapo", "failed", "logging from tapo plug: "+tcName+"; error: "+err.Error())
				continue
			}
			tcLgr.Log("info", usage.TodayRuntime, usage.TodayEnergy)
			s.lgr.Log("high", "tapo", "logged", tcName)
		}

		scheduler.SleepForFunc(func(t time.Duration) bool { return !s.exit }, time.Until(nextLogging)+time.Minute, time.Second)
		if failed {
			break
		}
	}
}
