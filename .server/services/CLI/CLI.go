package CLI

import (
	"HG75/modules/Auth"
	"HG75/modules/Com"
	"encoding/json"
	"errors"
	"io"
	"os"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/logger"

	"golang.org/x/term"
)

var (
	StopService = false
	IsRunning   = false
	OnExit      = func() {}

	lgr = &logger.Logger{}

	AutoComplete = []string{}

	Terminal = func() *term.Terminal {
		if !term.IsTerminal(0) || !term.IsTerminal(1) {
			panic(errors.New("stdin/stdout should be term"))
		}

		screen := struct {
			io.Reader
			io.Writer
		}{os.Stdin, os.Stdout}

		terminal := term.NewTerminal(screen, "> ")
		terminal.SetPrompt(string(terminal.Escape.Red) + "> " + string(terminal.Escape.Reset))
		terminal.AutoCompleteCallback = keypressCallback

		return terminal
	}()
)

func keypressCallback(line string, pos int, key rune) (newLine string, newPos int, ok bool) {
	if key != 9 || line == "" {
		return line, pos, false
	}

	for _, com := range AutoComplete {
		if strings.HasPrefix(com, strings.ToLower(line)) {
			return com, len(com), true
		}
	}

	return line, pos, false
}

func loop(out chan string) error {
	inpCh := make(chan string)
	errCh := make(chan error)
	go func() {
		defer OnExit()

		for !StopService {
			line, err := Terminal.ReadLine()
			if err != nil {
				errCh <- err
			} else {
				inpCh <- line
			}
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
			lgr.Log("debug", "CLI", "Checking", "Stop request")
		}
	}

	return nil
}

func Stop() {
	lgr.Log("info", "CLI", "Stopping", "")
	StopService = true

	for i := 0; i < 3; i++ {
		if !IsRunning {
			break
		}
		time.Sleep(time.Second * time.Duration(1))
	}

	lgr.Log("debug", "CLI", "Stopped", "")
}

func Start(mainChOut chan string, mainChErr chan error, onExit func(), log *logger.Logger, meta map[string]any) {
	OnExit = onExit
	defer OnExit()

	log.Log("info", "CLI", "Starting", "")

	IsRunning = true
	StopService = false

	lgr = log

	_, err := term.MakeRaw(0)
	if err != nil {
		panic(err)
	}

	user := Auth.User{
		Username:  "Owner",
		Password:  "",
		AuthLevel: Auth.AuthMap["owner"],
		Roles:     []string{"CLI", "Home"},
	}
	err = json.Unmarshal(Com.AutoComplete(user), &AutoComplete)
	if err != nil {
		mainChErr <- errors.New("unable to get auto completion: " + err.Error())
		panic(err)
	}

	lgr.Log("debug", "CLI", "Started", "")
	for !StopService {
		err := loop(mainChOut)
		if err == io.EOF {
			mainChOut <- "exit"
			break
		}
		if err != nil {
			mainChErr <- err
			break
		}
	}

	IsRunning = false
	lgr.Log("debug", "CLI", "Exited", "")
}
