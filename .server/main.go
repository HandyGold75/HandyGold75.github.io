package main

import (
	srvs "HG75/Services"
	"fmt"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"
)

type (
	Service interface {
		// `Loop()` is called in a goroutine.
		//
		// Should block until `Stop()` is called.
		Loop()
		// `Stop()` is called when the service is expected to stop.
		//
		// Should block until `Loop()` is stopped.
		Stop()
	}
)

var (
	exit = false

	lgr, _ = logger.NewRel("logs/server")

	Config = struct {
		IP                         string
		Port                       uint16
		SubDomain, Domain          string
		SonosIP                    string
		TapoPlugIPS                []string
		TapoUsername, TapoPassword string
		LogLevel, LogToFileLevel   int
		ModuleMaxRestartPerMinute  int
	}{
		IP: "0.0.0.0", Port: 17500,
		SubDomain: "go", Domain: "HandyGold75.com",
		SonosIP:     "",
		TapoPlugIPS: []string{}, TapoUsername: "", TapoPassword: "",
		LogLevel: 1, LogToFileLevel: 3,
		ModuleMaxRestartPerMinute: 3,
	}
)

func configureLogger(lgr *logger.Logger) {
	lgr.Verbosities = map[string]int{"error": 5, "warning": 4, "high": 3, "medium": 2, "low": 1, "debug": 0}
	lgr.VerboseToCLI, lgr.VerboseToFile = Config.LogLevel, Config.LogToFileLevel
	lgr.CharCountPerPart, lgr.PrepentCLI = 16, "\r"
	lgr.DynamicFileName = func() string { return time.Now().Format("2006-01") + ".log" }
	lgr.MessageCLIHook = func(msg string) { fmt.Print("\r> ") }
}

func run() {
	lgrTapo, _ := logger.NewRel("logs/tapo")
	configureLogger(lgrTapo)
	srvsTapo := srvs.NewTapo(lgrTapo, srvs.TapoConfig{
		TapoPlugIPS: []string{}, TapoUsername: "", TapoPassword: "",
	})

	lgrSite, _ := logger.NewRel("logs/site")
	configureLogger(lgrSite)
	srvsSite := srvs.NewSite(lgrSite, srvs.SiteConfig{})

	lgrCLI, _ := logger.NewRel("logs/cli")
	configureLogger(lgrCLI)
	srvsCLI := srvs.NewCLI(lgrCLI, srvs.CLIConfig{})

	for _, service := range []Service{srvsTapo, srvsSite, srvsCLI} {
		go service.Loop()
		defer service.Stop()
	}

	for {
		var out string

		select {
		case out = <-srvsTapo.Pipe:
		case out = <-srvsSite.Pipe:
		case out = <-srvsCLI.Pipe:
		case <-time.After(time.Second):
		}

		switch out {
		case "restart":
			return
		case "exit":
			exit = true
			return
		}
	}
}

func main() {
	_ = cfg.LoadRel("config", &Config)
	configureLogger(lgr)

	for !exit {
		run()
	}

	fmt.Println()
}
