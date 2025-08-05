package main

import (
	"HG75/coms/auth"
	"HG75/srvs"
	"errors"
	"fmt"
	"os"
	"slices"
	"strings"
	"sync"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"
	"github.com/HandyGold75/GOLib/scheduler"
	"golang.org/x/term"
)

type (
	Service interface {
		// Start service loop in a goroutine.
		//
		// Should not block for extended time.
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
		CLIConfig                srvs.CLIConfig
		SiteConfig               srvs.SiteConfig
		TapoConfig               srvs.TapoConfig
		AuthConfig               auth.Config
		LogLevel, LogToFileLevel int
		ModuleMaxRestartPerHour  int
	}{
		CLIConfig: srvs.CLIConfig{},
		SiteConfig: srvs.SiteConfig{
			IP: "0.0.0.0", Port: 17500,
			SubDomain: "go", Domain: "HandyGold75.com",
			SonosIP:          "",
			RequestsLimitCom: 180, RequestsLimitTimoutCom: 1,
			RequestsLimitAuth: 10, RequestsLimitTimoutAuth: 10,
		},
		TapoConfig: srvs.TapoConfig{
			PlugIPS:  []string{},
			Username: "", Password: "",
			Schedule: scheduler.Schedule{
				Months:  []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},
				Weeks:   []int{1, 2, 3, 4, 5},
				Days:    []int{0, 1, 2, 3, 4, 5, 6},
				Hours:   []int{23},
				Minutes: []int{59},
			},
		},
		AuthConfig: auth.Config{
			TokenExpiresAfterDays: 7,
		},
		LogLevel: 1, LogToFileLevel: 3,
		ModuleMaxRestartPerHour: 3,
	}
)

func run() {
	srvsCLI := srvs.NewCLI(Config.CLIConfig)
	srvsSite := srvs.NewSite(Config.SiteConfig, Config.TapoConfig, Config.AuthConfig)
	srvsTapo := srvs.NewTapo(Config.TapoConfig)

	wg := sync.WaitGroup{}
	for _, service := range []Service{srvsCLI, srvsSite, srvsTapo} {
		wg.Add(1)
		go func() { service.Run(); wg.Done() }()
	}
	wg.Wait()

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
		select {
		case out, ok := <-srvsCLI.Pipe:
			if !ok && checkRestarts("cli") {
				lgr.Log("debug", "cli", "restarting")
				srvsCLI.Stop()
				srvsCLI = srvs.NewCLI(Config.CLIConfig)
				srvsCLI.Run()
				lgr.Log("high", "cli", "restarted")
			} else if !ok || out == "" {
				continue
			}

			go func() {
				comOut, _, _, err := srvsSite.ProssesCommand(auth.User{
					Username: "owner", Password: "",
					AuthLevel: auth.AuthLevelOwner, Roles: []string{"CLI", "Home"},
					Enabled: true,
				}, strings.Split(out, " ")...)
				if err != nil {
					lgr.Log("error", "owner", "command", err.Error())
				} else if len(comOut) > 0 {
					_, _ = fmt.Fprint(srvs.Terminal, "\r\n"+string(comOut)+"\n\r")
				}
			}()

		case out, ok := <-srvsSite.Pipe:
			if !ok && checkRestarts("site") {
				lgr.Log("debug", "site", "restarting")
				srvsSite.Stop()
				srvsSite = srvs.NewSite(Config.SiteConfig, Config.TapoConfig, Config.AuthConfig)
				srvsSite.Run()
				lgr.Log("high", "site", "restarted")
			} else if !ok || out == "" {
				continue
			}

			switch out {
			case "exit":
				exit = true
			case "restart":
				exit = true
				defer func() { exit = false }()
			}

		case _, ok := <-srvsTapo.Pipe:
			if !ok && checkRestarts("tapo") {
				lgr.Log("debug", "tapo", "restarting")
				srvsTapo.Stop()
				srvsTapo = srvs.NewTapo(Config.TapoConfig)
				srvsTapo.Run()
				lgr.Log("high", "tapo", "restarted")
			}

		case <-time.After(time.Second):
		}
	}

	wg = sync.WaitGroup{}
	for _, service := range []Service{srvsCLI, srvsSite, srvsTapo} {
		wg.Add(1)
		go func() { service.Stop(); wg.Done() }()
	}
	wg.Wait()
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
	lgr, _ = logger.NewRel("data/logs/server")

	for !exit {
		run()
	}
	fmt.Println("\r")
}
