package main

import (
	"HG75/modules/Auth"
	"HG75/modules/Com"
	"HG75/services/CLI"
	"HG75/services/HTTPS"
	"HG75/services/Tapo"
	"encoding/json"
	"errors"
	"fmt"
	"maps"
	"net/http"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/logger"

	"golang.org/x/term"
)

type (
	Files struct {
		TopDir      string
		UserDir     string
		SSLDir      string
		DBDir       string
		TapoDir     string
		LogDir      string
		SrvLogDir   string
		CLILogDir   string
		HTTPSLogDir string
		TapoLogDir  string
		ComLogDir   string
		AuthLogDir  string
	}

	Config struct {
		IP                        string   `json:"IP"`
		Port                      uint16   `json:"Port"`
		Domain                    string   `json:"Domain"`
		SubDomainHTTPS            string   `json:"SubDomainHTTPS"`
		SonosIPS                  []string `json:"SonosIps"`
		TapoPlugIPS               []string `json:"TapoPlugIps"`
		TapoUsername              string   `json:"TapoUsername"`
		TapoPassword              string   `json:"TapoPassword"`
		LogLevel                  int      `json:"LogLevel"`
		LogToFileLevel            int      `json:"LogToFileLevel"`
		ModuleMaxRestartPerMinute int      `json:"ModuleMaxRestartPerMinute"`
		Modified                  int      `json:"Modified"`
	}

	Service struct {
		Name      string
		Err       chan error
		Out       chan string
		Restarts  []time.Time
		IsRunning *bool
		Logger    *logger.Logger
		Meta      map[string]any
		Start     func(chan string, chan error, func(), *logger.Logger, map[string]any)
		Stop      func()
	}

	Services []Service
)

var (
	StopServer = false
	HasStarted = false

	RootDir = func() string {
		filePath, err := os.Executable()
		if err != nil {
			panic(err)
		}
		filePathSplit := strings.Split(filePath, "/")
		return strings.Join(filePathSplit[:len(filePathSplit)-1], "/")
	}()

	files = Files{
		TopDir:      RootDir + "/server",
		UserDir:     RootDir + "/server/users",
		SSLDir:      RootDir + "/server/ssl",
		DBDir:       RootDir + "/server/db",
		TapoDir:     RootDir + "/server/tapo",
		LogDir:      RootDir + "/server/logs",
		SrvLogDir:   RootDir + "/server/logs/server",
		CLILogDir:   RootDir + "/server/logs/cli",
		HTTPSLogDir: RootDir + "/server/logs/https",
		TapoLogDir:  RootDir + "/server/logs/tapo",
		ComLogDir:   RootDir + "/server/logs/com",
		AuthLogDir:  RootDir + "/server/logs/auth",
	}

	lgr = logger.New(files.SrvLogDir)

	config = Config{
		LogLevel:                  1,
		LogToFileLevel:            3,
		ModuleMaxRestartPerMinute: 3,
		IP:                        "127.0.0.1",
		Port:                      17500,
		Domain:                    "HandyGold75.com",
		SubDomainHTTPS:            "https",
		SonosIPS:                  []string{},
		TapoPlugIPS:               []string{},
		TapoUsername:              "",
		TapoPassword:              "",
	}

	services = Services{}

	ServerComs = func() Com.Commands {
		coms := Com.Commands{}
		maps.Copy(coms, Com.ServerComs)
		maps.Copy(coms, CLIComs)

		return coms
	}()

	originalTrm = func() *term.State {
		oldState, err := term.MakeRaw(0)
		if err != nil {
			panic(err)
		}
		return oldState
	}()

	CLIComs = Com.Commands{
		"exit": Com.Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Stop the server.",
			DetailedDescription: "Informs all routines to stop and then quit, the process exits when all routines have stopped.",
			ExampleDescription:  "",
			AutoComplete:        []string{},
			ArgsLen:             [2]int{0, 0},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				StopServer = true
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
		"restart": Com.Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Restart the server.",
			DetailedDescription: "Informs all routines to stop, the routines will be started again when all routines have stopped.",
			ExampleDescription:  "",
			AutoComplete:        []string{},
			ArgsLen:             [2]int{0, 0},
			Function: func(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
				HasStarted = false
				StopServer = true
				return []byte{}, "", http.StatusAccepted, nil
			},
		},
		"debug": Com.Command{
			RequiredAuthLevel:   Auth.AuthMap["admin"],
			RequiredRoles:       []string{"CLI"},
			Description:         "Enable/ disable debugging or print debug values.",
			DetailedDescription: "Enabled or disabled debugging or print debug values. Usage: debug [0|1|server|auth|https]\r\n  Restarting the server will reset the debug state to the orginial value.",
			ExampleDescription:  "1",
			AutoComplete:        []string{"0", "1", "server", "auth", "https"},
			ArgsLen:             [2]int{1, 1},
			Function:            setDebug,
		},
	}
)

func prepareFolders() error {
	allDirs := []string{
		files.TopDir,
		files.UserDir,
		files.SSLDir,
		files.DBDir,
		files.TapoDir,
		files.LogDir,
		files.SrvLogDir,
		files.CLILogDir,
		files.HTTPSLogDir,
		files.TapoLogDir,
		files.ComLogDir,
		files.AuthLogDir,
	}

	for _, dir := range allDirs {
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			if err := os.Mkdir(dir, 0740); err != nil {
				return err
			}
		}
	}

	return nil
}

func filterTimes(timeSlice []time.Time, maxAge time.Duration) []time.Time {
	return slices.DeleteFunc(timeSlice, func(t time.Time) bool {
		return -time.Until(t) > maxAge
	})
}

func setDebug(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) != 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("debug requires 1 argument")
	}

	switch args[0] {
	case "0":
		lgr.VerboseToCLI = config.LogLevel
		for i := 0; i < len(services); i++ {
			services[i].Logger.VerboseToCLI = config.LogLevel
		}

		return []byte{}, "", http.StatusAccepted, nil

	case "1":
		lgr.VerboseToCLI = 0
		for i := 0; i < len(services); i++ {
			services[i].Logger.VerboseToCLI = 0
		}

		return []byte{}, "", http.StatusAccepted, nil

	case "server":
		jsonBytes, err := json.MarshalIndent(Debug(), "\r", "\t")
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "auth":
		jsonBytes, err := json.MarshalIndent(Auth.Debug(), "\r", "\t")
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "https":
		jsonBytes, err := json.MarshalIndent(HTTPS.Debug(), "\r", "\t")
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("debug operation should be 0, 1, server, auth or https")
}

func updateLgr(log *logger.Logger) {
	log.Verbosities = logger.Verbosities{"warning": 5, "error": 5, "info": 4, "high": 3, "medium": 2, "low": 1, "debug": 0}
	log.VerboseToCLI = config.LogLevel
	log.VerboseToFile = config.LogToFileLevel
	log.CharCountPerMsg = 16
	log.PrepentCLI = "\r"
	log.DynamicFileName = func() string { return time.Now().Format("2006-01") + ".log" }
	log.MessageCLIHook = func(msg string) { fmt.Fprint(CLI.Terminal, "\r") }
}

func handleServiceOut(service *Service, out string) {
	defer WeMightBeFucked()

	if service == (&Service{}) {
		return
	}

	outSplitted := strings.Split(out, " ")
	com, args := outSplitted[0], outSplitted[1:]

	user := Auth.User{
		Username:  "Owner",
		Password:  "",
		AuthLevel: Auth.AuthMap["owner"],
		Roles:     []string{"CLI", "Home"},
	}

	var (
		comOut      []byte
		contentType string
		errCode     int
		err         error
	)

	if _, ok := CLIComs[com]; ok {
		if CLIComs[com].RequiredAuthLevel >= 2 {
			lgr.Log("high", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
		} else if CLIComs[com].RequiredAuthLevel >= 1 {
			lgr.Log("medium", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
		} else {
			lgr.Log("low", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
		}

		comOut, contentType, errCode, err = CLIComs[com].Function(user, args...)

	} else {
		comOut, contentType, errCode, err = HTTPS.ProssesCom(user, com, args...)
	}

	if err != nil || errCode < 200 || errCode >= 300 {
		lgr.Log("warning", service.Name, "Failed", err)
	}
	if strings.HasPrefix(contentType, "text/") {
		fmt.Printf("\r%v\r\n", string(comOut))
		if lgr.MessageCLIHook != nil {
			lgr.MessageCLIHook("")
		}
	}
	if strings.HasPrefix(contentType, "application/json") {
		fmt.Printf("\r%+v\r\n", string(comOut))
		if lgr.MessageCLIHook != nil {
			lgr.MessageCLIHook("")
		}
	}
}

func handleServiceErr(service *Service, err error) {
	if err != nil {
		lgr.Log("error", service.Name, "Failed", err)
	}

	service.Restarts = filterTimes(service.Restarts, time.Minute*time.Duration(1))
	service.Restarts = append(service.Restarts, time.Now())
	if len(service.Restarts) > config.ModuleMaxRestartPerMinute {
		lgr.Log("info", service.Name, "Abort Restart", "Restarted "+strconv.Itoa(config.ModuleMaxRestartPerMinute)+" time within a minute!")
		return
	}

	lgr.Log("warning", service.Name, "Restarting", "Attempt "+strconv.Itoa(len(service.Restarts)))

	if *service.IsRunning {
		service.Stop()
	}

	updateLgr(service.Logger)

	go service.Start(service.Out, service.Err, WeMightBeFucked, service.Logger, service.Meta)
}

func startService(service *Service) {
	updateLgr(service.Logger)

	go service.Start(service.Out, service.Err, WeMightBeFucked, service.Logger, service.Meta)
}

func stopService(service *Service) {
	service.Stop()

	close(service.Out)
	close(service.Err)

	service = &Service{}
}

func WeMightBeFucked() {
	if rec := recover(); rec != nil {
		term.Restore(0, originalTrm)

		fmt.Printf("\nPANIC STOPPING SERVER, SERVICES AND MODULES!\n")

		for i := 0; i < len(services); i++ {
			services[i].Stop()
		}

		closeModules()

		panic(rec)
	}
}

func watchDog() {
	CLIService := Service{
		Name:      "CLI",
		Err:       make(chan error),
		Out:       make(chan string),
		Restarts:  []time.Time{},
		IsRunning: &CLI.IsRunning,
		Logger:    logger.New(files.CLILogDir),
		Meta:      map[string]any{},
		Start:     CLI.Start,
		Stop:      CLI.Stop,
	}

	HTTPSService := Service{
		Name:      "HTTPS",
		Err:       make(chan error),
		Out:       make(chan string),
		Restarts:  []time.Time{},
		IsRunning: &HTTPS.IsRunning,
		Logger:    logger.New(files.HTTPSLogDir),
		Meta: map[string]any{
			"TopDir": files.TopDir,
			"SSLDir": files.SSLDir,
			"config": &HTTPS.Config{
				IP:             config.IP,
				Port:           config.Port,
				Domain:         config.Domain,
				SubDomainHTTPS: config.SubDomainHTTPS,
			}},
		Start: HTTPS.Start,
		Stop:  HTTPS.Stop,
	}

	TapoService := Service{
		Name:      "Tapo",
		Err:       make(chan error),
		Out:       make(chan string),
		Restarts:  []time.Time{},
		IsRunning: &Tapo.IsRunning,
		Logger:    logger.New(files.TapoLogDir),
		Meta: map[string]any{
			"TopDir":      files.TopDir,
			"TapoDir":     files.TapoDir,
			"TapoClients": &Com.TapoClients,
		},
		Start: Tapo.Start,
		Stop:  Tapo.Stop,
	}

	services = Services{CLIService, HTTPSService, TapoService}
	for i := 0; i < len(services); i++ {
		startService(&services[i])
		defer stopService(&services[i])
	}

	HasStarted = true
	for !StopServer {
		select {
		case out := <-CLIService.Out:
			go handleServiceOut(&CLIService, out)
		case err := <-CLIService.Err:
			handleServiceErr(&CLIService, err)

		case out := <-HTTPSService.Out:
			go handleServiceOut(&HTTPSService, out)
		case err := <-HTTPSService.Err:
			handleServiceErr(&HTTPSService, err)

		case out := <-TapoService.Out:
			go handleServiceOut(&TapoService, out)
		case err := <-TapoService.Err:
			handleServiceErr(&TapoService, err)

		case <-time.After(time.Second + time.Duration(1)):
			lgr.Log("debug", "Server", "Checking", "Server stop request")
			if StopServer {
				break
			}

			if !*CLIService.IsRunning && len(CLIService.Restarts) < config.ModuleMaxRestartPerMinute+1 {
				handleServiceErr(&CLIService, nil)
			}
			if !*HTTPSService.IsRunning && len(HTTPSService.Restarts) < config.ModuleMaxRestartPerMinute+1 {
				handleServiceErr(&HTTPSService, nil)
			}
			if !*TapoService.IsRunning && len(TapoService.Restarts) < config.ModuleMaxRestartPerMinute+1 {
				handleServiceErr(&TapoService, nil)
			}
		}
	}
}

func Debug() Config {
	return config
}

func closeModules() {
	Com.Close()
	Auth.Close()
}

func initModules() {
	comLogger := logger.New(files.ComLogDir)
	updateLgr(comLogger)

	Com.Init(
		Com.Files{
			LogDir:  files.LogDir,
			DBDir:   files.DBDir,
			TapoDir: files.TapoDir,
		},
		comLogger,
		Com.Config{
			SonosIPS:     config.SonosIPS,
			TapoPlugIPS:  config.TapoPlugIPS,
			TapoUsername: config.TapoUsername,
			TapoPassword: config.TapoPassword,
		},
	)

	authLogger := logger.New(files.AuthLogDir)
	updateLgr(authLogger)

	Auth.Init(
		Auth.Files{
			UserDir: files.UserDir,
		},
		authLogger,
	)
}

func loadHotConfig() {
	if err := prepareFolders(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	cfg.FileName = strings.Replace(files.TopDir, RootDir, "", 1) + "/config.json"
	if err := cfg.Load(&config); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	updateLgr(lgr)
}

func main() {
	defer WeMightBeFucked()

	for !HasStarted {
		loadHotConfig()
		initModules()

		lgr.Log("info", "Server", "Starting", "")

		watchDog()
		lgr.Log("info", "Server", "Stopping", "")

		closeModules()
		StopServer = false
		lgr.Log("debug", "Server", "Stopped", "")
	}

	fmt.Printf("\r")

	term.Restore(0, originalTrm)
}
