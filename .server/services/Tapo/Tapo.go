package Tapo

import (
	"errors"
	"os"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/logger"
	"github.com/HandyGold75/GOLib/scheduler"

	"github.com/achetronic/tapogo/pkg/tapogo"
)

type (
	Files struct {
		TopDir  string
		TapoDir string
	}
)

var (
	StopService = false
	IsRunning   = false
	OnExit      = func() {}

	RootDir = func() string {
		filePath, err := os.Executable()
		if err != nil {
			panic(err)
		}
		filePathSplit := strings.Split(filePath, "/")
		return strings.Join(filePathSplit[:len(filePathSplit)-1], "/")
	}()

	files = Files{}

	lgr = &logger.Logger{}

	scedule = scheduler.Scedule{
		Months:  []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},
		Weeks:   []int{1, 2, 3, 4, 5},
		Days:    []int{0, 1, 2, 3, 4, 5, 6},
		Hours:   []int{23},
		Minutes: []int{59},
	}

	TapoClients = &map[string]*tapogo.Tapo{}
)

func prepareFolders() error {
	allDirs := []string{
		files.TopDir,
		files.TapoDir,
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

func LogTapoStats() (string, error) {
	for tcName, tc := range *TapoClients {
		tcLgr := logger.New(files.TapoDir + "/" + tcName)
		tcLgr.Verbosities = logger.Verbosities{"error": 2, "info": 1}
		tcLgr.VerboseToCLI = 9
		tcLgr.VerboseToFile = 0
		tcLgr.DynamicFileName = func() string { return time.Now().Format("2006") + ".log" }

		if _, err := os.Stat(files.TapoDir + "/" + tcName); os.IsNotExist(err) {
			if err := os.Mkdir(files.TapoDir+"/"+tcName, 0740); err != nil {
				tcLgr.Log("error", err)
				lgr.Log("error", "Tapo", "Failed", tcName)
				continue
			}
		}

		usage, err := tc.GetEnergyUsage()
		if err != nil {
			tcLgr.Log("error", err)
			lgr.Log("error", "Tapo", "Failed", tcName)
			continue
		}

		tcLgr.Log("info", usage.Result.TodayRuntime, usage.Result.TodayEnergy)
		lgr.Log("high", "Tapo", "Logged", tcName)
	}

	return "", nil
}

func loop(out chan string) error {
	inpCh := make(chan string)
	errCh := make(chan error)
	go func() {
		defer OnExit()

		for !StopService {
			nextLogging := time.Now()
			if err := scheduler.SetNextTime(&nextLogging, &scedule); err != nil {
				errCh <- err
				continue
			}

			if time.Until(nextLogging) > time.Duration(0) {
				lgr.Log("high", "Tapo", "Sceduled", nextLogging.Format(time.DateTime))
				scheduler.SleepFor("", time.Until(nextLogging), time.Second*time.Duration(1))
			}

			line, err := LogTapoStats()
			if err != nil {
				errCh <- err
			} else {
				inpCh <- line
			}

			scheduler.SleepFor("", time.Until(nextLogging)+(time.Minute*time.Duration(1)), time.Second*time.Duration(1))
		}

		close(inpCh)
		close(errCh)
	}()

	for !StopService {
		select {
		case line := <-inpCh:
			if line == "" {
				continue
			}
			out <- line

		case err := <-errCh:
			return err

		case <-time.After(time.Second * time.Duration(1)):
			lgr.Log("debug", "Tapo", "Checking", "Stop request")
		}
	}

	return nil
}

func Stop() {
	lgr.Log("info", "Tapo", "Stopping", "")
	StopService = true

	for i := 0; i < 3; i++ {
		if !IsRunning {
			break
		}
		time.Sleep(time.Second * time.Duration(1))
	}

	lgr.Log("debug", "Tapo", "Stopped", "")
}

// meta expects minimally: map[string]any{"TopDir": string, "TapoDir": string, "TapoClients": *map[string]*tapogo.Tapo}
func Start(mainChOut chan string, mainChErr chan error, onExit func(), log *logger.Logger, meta map[string]any) {
	OnExit = onExit
	defer OnExit()

	log.Log("info", "Tapo", "Starting", "")

	IsRunning = true
	StopService = false

	lgr = log

	topDir, ok := meta["TopDir"].(string)
	if !ok {
		mainChErr <- errors.New("missing TopDir meta")
		StopService = true
	}
	tapoDir, ok := meta["TapoDir"].(string)
	if !ok {
		mainChErr <- errors.New("missing TapoDir meta")
		StopService = true
	}
	files = Files{
		TopDir:  topDir,
		TapoDir: tapoDir,
	}

	tcs, ok := meta["TapoClients"].(*map[string]*tapogo.Tapo)
	if !ok {
		mainChErr <- errors.New("missing TapoClients meta")
		StopService = true
	}
	TapoClients = tcs

	err := prepareFolders()
	if err != nil {
		mainChErr <- errors.New("unable to prepare folders")
		StopService = true
	}

	lgr.Log("debug", "Tapo", "Started", "")
	for !StopService {
		err := loop(mainChOut)
		if err != nil {
			mainChErr <- err
			break
		}
	}

	IsRunning = false
	lgr.Log("debug", "Tapo", "Exited", "")
}
