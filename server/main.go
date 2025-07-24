package main

import (
	"HG75/srvs"
	"errors"
	"fmt"
	"os"
	"slices"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"
	"golang.org/x/term"
)

type (
	Service interface {
		// Start service loop in a goroutine.
		Run()
		// Stop service loop.
		//
		// Should block until service is stopped.
		Stop()
	}
)

var (
	exit = false

	lgr *logger.Logger = nil

	Config = struct {
		IP                         string
		Port                       uint16
		SubDomain, Domain          string
		SonosIP                    string
		TapoPlugIPS                []string
		TapoUsername, TapoPassword string
		LogLevel, LogToFileLevel   int
		ModuleMaxRestartPerHour    int
	}{
		IP: "0.0.0.0", Port: 17500,
		SubDomain: "go", Domain: "HandyGold75.com",
		SonosIP:     "",
		TapoPlugIPS: []string{}, TapoUsername: "", TapoPassword: "",
		LogLevel: 1, LogToFileLevel: 3,
		ModuleMaxRestartPerHour: 3,
	}
)

func run() {
	confTapo := srvs.TapoConfig{TapoPlugIPS: []string{}, TapoUsername: "", TapoPassword: ""}
	confSite := srvs.SiteConfig{}
	confCLI := srvs.CLIConfig{}

	srvsTapo := srvs.NewTapo(confTapo)
	srvsSite := srvs.NewSite(confSite)
	srvsCLI := srvs.NewCLI(confCLI)

	for _, service := range []Service{srvsTapo, srvsSite, srvsCLI} {
		service.Run()
	}

	restarts := map[string][]time.Time{}
	checkRestarts := func(name string) bool {
		_, ok := restarts[name]
		if !ok {
			restarts[name] = []time.Time{time.Now()}
			return true
		}
		restarts[name] = slices.DeleteFunc(restarts[name], func(t time.Time) bool { return t.Before(time.Now().Add(-time.Hour)) })
		if len(restarts[name]) >= Config.ModuleMaxRestartPerHour {
			return false
		}
		restarts[name] = append(restarts[name], time.Now())
		return true
	}

	for !exit {
		out := ""
		var ok bool

		select {
		case out, ok = <-srvsTapo.Pipe:
			if !ok && checkRestarts("tapo") {
				lgr.Log("debug", "tapo", "restarting")
				srvsTapo.Stop()
				srvsTapo = srvs.NewTapo(confTapo)
				srvsTapo.Run()
				lgr.Log("high", "tapo", "restarted")
			}

		case out, ok = <-srvsSite.Pipe:
			if !ok && checkRestarts("site") {
				lgr.Log("debug", "site", "restarting")
				srvsSite.Stop()
				srvsSite = srvs.NewSite(confSite)
				srvsSite.Run()
				lgr.Log("high", "site", "restarted")
			}

		case out, ok = <-srvsCLI.Pipe:
			if !ok && checkRestarts("cli") {
				lgr.Log("debug", "cli", "restarting")
				srvsCLI.Stop()
				srvsCLI = srvs.NewCLI(confCLI)
				srvsCLI.Run()
				lgr.Log("high", "cli", "restarted")
			}

		case <-time.After(time.Second):
		}

		if out == "restart" {
			break
		} else if out == "exit" {
			exit = true
			break
		}
	}

	for _, service := range []Service{srvsTapo, srvsSite, srvsCLI} {
		service.Stop()
	}
}

func main() {
	if !term.IsTerminal(int(os.Stdin.Fd())) || !term.IsTerminal(int(os.Stdout.Fd())) {
		panic(errors.New("stdin/stdout should be term"))
	}
	oldState, err := term.MakeRaw(int(os.Stdin.Fd()))
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer func() { _ = term.Restore(int(os.Stdin.Fd()), oldState) }()

	_ = cfg.LoadRel("config", &Config)

	logger.Verbosities = map[string]int{"error": 5, "warning": 4, "high": 3, "medium": 2, "low": 1, "debug": 0}
	logger.VerboseToCLI, logger.VerboseToFile = Config.LogLevel, Config.LogToFileLevel
	logger.CharCountPerPart, logger.PrepentCLI = 16, "\r"
	logger.DynamicFileName = func() string { return time.Now().Format("2006-01") + ".log" }
	logger.MessageCLIHook = func(msg string) { _, _ = fmt.Fprint(srvs.Terminal, "\r") }
	lgr, _ = logger.NewRel("logs/server")

	for !exit {
		run()
	}
	fmt.Println("\r")
}
