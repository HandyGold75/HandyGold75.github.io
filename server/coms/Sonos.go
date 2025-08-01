package coms

import (
	"HG75/auth"
	"encoding/base64"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/raitonoberu/ytsearch"
)

type (
	SyncInfo struct {
		Track   TrackInfoMinimal
		Que     QueInfoMinimal
		Playing bool
		Shuffle bool
		Repeat  bool
		Volume  int
	}

	TrackInfoMinimal struct {
		QuePosition int
		Duration    string
		Progress    string
		Title       string
		Creator     string
		Album       string
	}

	QueInfoMinimal struct {
		Count      int
		TotalCount int
	}

	YTInfoMinimal struct {
		ID        string
		Title     string
		Duration  int
		ViewCount int
		Creator   string
	}
)

var sonosCommands = Commands{
	"sonos": Command{
		AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
		Description: "Interact sonos music boxes.",
		Commands: Commands{
			"track": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get current track.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"state": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get state.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"stop": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Stop play state.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"play": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set play state.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"mute": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set mute state.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"volume": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Control media volume.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:100|+X|-X|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"seek": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Control track progress.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:X|+X|-X]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"position": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Control que position.",
				AutoComplete:    []string{},
				ArgsDescription: "[1:X|+X|-X]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"next": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Next que position.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:X|+X|-X]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"previous": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Previous que position.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:X|+X|-X]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"que": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get, set, remove or clear que.",
				AutoComplete:    []string{},
				ArgsDescription: "[get|add|remove|clear] [track|index]?",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"bass": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get, set or change bass.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:10|+X|-X|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"treble": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get, set or change treble.",
				AutoComplete:    []string{},
				ArgsDescription: "[0:10|+X|-X|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"loudness": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set loudness.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"led": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set speaker led.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"playername": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set speaker led.",
				AutoComplete:    []string{},
				ArgsDescription: "[name]?",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"shuffle": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set shuffle.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"repeat": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set repeat.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"repeatone": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get or set repeatone.",
				AutoComplete:    []string{},
				ArgsDescription: "[0|1|get]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"favorites": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get current favorites.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"radioshows": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get current radioshows.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"radiostations": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get current radiostations.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"sync": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get current track (minimal) + que (minimal) + diverce device states.",
				AutoComplete:    []string{},
				ArgsDescription: "",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"yt": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get query from yt.",
				AutoComplete:    []string{},
				ArgsDescription: "[query]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
			"uri": Command{
				AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
				Description:     "Get base64 from album art uri.",
				AutoComplete:    []string{},
				ArgsDescription: "[uri]",
				ArgsLen:         [2]int{0, 0},
				Exec: func(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
					return []byte{}, "", http.StatusInternalServerError, errors.New("unimplemented")
				},
			},
		},
	},
}

func sonosInterface(user auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("sonos requires at least 1 argument")
	}

	switch args[0] {
	case "track":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos track requires 0 argument")
		}

		trackInfo, err := HookSonos.GetTrackInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(trackInfo)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "state":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos state requires 0 argument")
		}

		return state()

	case "stop":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos stop requires 0 argument")
		}

		err := HookSonos.Stop()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return state()

	case "play":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos play requires 1 argument")
		}

		if args[1] == "0" {
			return play(false)
		} else if args[1] == "1" {
			return play(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetPlay()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos play state should be 0, 1 or get")

	case "mute":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos mute requires 1 argument")
		}

		if args[1] == "0" {
			return mute(false)
		} else if args[1] == "1" {
			return mute(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetMute()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos mute state should be 0, 1 or get")

	case "volume":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos volume requires 1 argument")
		}

		if args[1] == "get" {
			curVol, err := HookSonos.GetVolume()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
		}

		return volume(args[1])

	case "seek":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos seek requires 1 argument")
		}

		return seek(args[1])

	case "que":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos que requires 1 argument")
		}

		if args[1] == "get" {
			queInfo, err := HookSonos.GetQue()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			jsonBytes, err := json.Marshal(queInfo)
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return jsonBytes, "application/json", http.StatusOK, nil

		} else if args[1] == "add" {
			if len(args) != 3 {
				return []byte{}, "", http.StatusBadRequest, errors.New("sonos que requires 1 argument")
			}

			return add(args[2])

		} else if args[1] == "remove" {
			if len(args) != 3 {
				return []byte{}, "", http.StatusBadRequest, errors.New("sonos remove requires 1 argument")
			}

			return remove(args[2])

		} else if args[1] == "clear" {
			if len(args) != 1 {
				return []byte{}, "", http.StatusBadRequest, errors.New("sonos clear requires 0 argument")
			}

			return clearq()
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos play state should be get, add, remove or clear")

	case "position":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos position requires 1 argument")
		}

		return position(args[1])

	case "next":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos next requires 0 argument")
		}

		return next()

	case "previous":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos previous requires 0 argument")
		}

		return previous()

	case "bass":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos bass requires 1 argument")
		}

		if args[1] == "get" {
			curVol, err := HookSonos.GetBass()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
		}

		return bass(args[1])

	case "treble":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos treble requires 1 argument")
		}

		if args[1] == "get" {
			curVol, err := HookSonos.GetTreble()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
		}

		return treble(args[1])

	case "loudness":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos loudness requires 1 argument")
		}

		if args[1] == "0" {
			return loudness(false)
		} else if args[1] == "1" {
			return loudness(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetLoudness()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos loudness state should be 0, 1 or get")

	case "led":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos led requires 1 argument")
		}

		if args[1] == "0" {
			return led(false)
		} else if args[1] == "1" {
			return led(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetLED()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos led state should be 0, 1 or get")

	case "playername":
		if len(args) == 1 {
			return playername("")
		} else if len(args) == 2 {
			return playername(args[1])
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos playername requires 0 or 1 argument")

	case "shuffle":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos shuffle requires 1 argument")
		}

		if args[1] == "0" {
			return shuffle(false)
		} else if args[1] == "1" {
			return shuffle(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetShuffle()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos shuffle state should be 0, 1 or get")

	case "repeat":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeat requires 1 argument")
		}

		if args[1] == "0" {
			return repeat(false)
		} else if args[1] == "1" {
			return repeat(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetRepeat()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeat state should be 0, 1 or get")

	case "repeatone":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeatone requires 1 argument")
		}

		if args[1] == "0" {
			return repeatone(false)
		} else if args[1] == "1" {
			return repeatone(true)
		} else if args[1] == "get" {
			curState, err := HookSonos.GetRepeatOne()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeatone state should be 0, 1 or get")

	case "favorites":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos favorites requires 0 argument")
		}

		favInfo, err := HookSonos.GetSonosFavorites()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(favInfo)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "radioshows":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos radioshows requires 0 argument")
		}

		radInfo, err := HookSonos.GetRadioShows()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(radInfo)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "radiostations":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos radiostations requires 0 argument")
		}

		radInfo, err := HookSonos.GetRadioStations()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(radInfo)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "sync":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos sync requires 0 argument")
		}

		return sync()

	case "yt":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos yt requires 1 argument")
		}

		return yt(args[1])

	case "uri":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos uri requires 1 argument")
		}

		return uri(args[1])

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("sonos operation should be track, state, stop, play, mute, volume, seek, position, next, previous, que, add, remove, clear, bass, treble, loudness, led, playername, shuffle, repeat, repeatone, favorites, radioshows, radiostations, sync, yt or uri")
}

func state() (out []byte, contentType string, errCode int, err error) {
	curState, err := HookSonos.GetCurrentTransportState()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(curState), "text/plain", http.StatusOK, nil
}

func play(state bool) (out []byte, contentType string, errCode int, err error) {
	if state {
		if err := HookSonos.Play(); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	} else {
		if err := HookSonos.Pause(); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	for i := range 10 {
		curState, err := HookSonos.GetTransitioning()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		if curState {
			time.Sleep(time.Millisecond * time.Duration(max(50, 600-(i*200))))
			continue
		}

		curState, err = HookSonos.GetPlay()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
	}

	return []byte("false"), "text/plain", http.StatusOK, nil
}

func mute(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetMute(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetMute()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func volume(volume string) (out []byte, contentType string, errCode int, err error) {
	newVol, err := strconv.Atoi(volume)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if strings.HasPrefix(volume, "+") || strings.HasPrefix(volume, "-") {
		oldVol, err := HookSonos.GetVolume()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := HookSonos.SetVolume(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := HookSonos.SetVolume(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := HookSonos.GetVolume()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
}

func seek(index string) (out []byte, contentType string, errCode int, err error) {
	newIndex, err := strconv.Atoi(index)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if strings.HasPrefix(index, "+") || strings.HasPrefix(index, "-") {
		if err := HookSonos.SeekTimeDelta(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	} else {
		if err := HookSonos.SeekTime(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(trackInfo.Progress), "text/plain", http.StatusOK, nil
}

func position(index string) (out []byte, contentType string, errCode int, err error) {
	newIndex, err := strconv.Atoi(index)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if strings.HasPrefix(index, "+") || strings.HasPrefix(index, "-") {
		trackInfo, err := HookSonos.GetTrackInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		if err := HookSonos.SeekTrack(trackInfo.QuePosition + newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := HookSonos.SeekTrack(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(trackInfo.QuePosition)), "text/plain", http.StatusOK, nil
}

func next() (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.Next(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(trackInfo.QuePosition)), "text/plain", http.StatusOK, nil
}

func previous() (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.Previous(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(trackInfo.QuePosition)), "text/plain", http.StatusOK, nil
}

func add(uri string) (out []byte, contentType string, errCode int, err error) {
	return []byte{}, "", http.StatusInternalServerError, errors.New("sonos add is broken")

	if strings.HasPrefix(uri, "https://open.spotify.com/") {
		uri_args := strings.Replace(uri, "https://open.spotify.com/", "", 1)
		id_type := strings.Split(uri_args, "/")[0]
		id := strings.Split(strings.Replace(uri_args, id_type+"/", "", 1), "?")[0]
		uri = "spotify%3a" + id_type + "%3a" + id
		// uri = "x-sonos-spotify:" + "spotify%3a" + id_type + "%3a" + id + "?sid=9\u0026flags=8232\u0026sn=3"
	}

	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if err := HookSonos.QueAdd(uri, trackInfo.QuePosition, true); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := HookSonos.GetQue()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(queInfo.TotalCount)), "text/plain", http.StatusOK, nil
}

func remove(index string) (out []byte, contentType string, errCode int, err error) {
	newIndex, err := strconv.Atoi(index)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if err := HookSonos.QueRemove(newIndex); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := HookSonos.GetQue()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(queInfo.TotalCount)), "text/plain", http.StatusOK, nil
}

func clearq() (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.QueClear(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := HookSonos.GetQue()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(queInfo.TotalCount)), "text/plain", http.StatusOK, nil
}

func bass(volume string) (out []byte, contentType string, errCode int, err error) {
	newVol, err := strconv.Atoi(volume)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if strings.HasPrefix(volume, "+") || strings.HasPrefix(volume, "-") {
		oldVol, err := HookSonos.GetBass()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := HookSonos.SetBass(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := HookSonos.SetBass(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := HookSonos.GetBass()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
}

func treble(volume string) (out []byte, contentType string, errCode int, err error) {
	newVol, err := strconv.Atoi(volume)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if strings.HasPrefix(volume, "+") || strings.HasPrefix(volume, "-") {
		oldVol, err := HookSonos.GetTreble()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := HookSonos.SetTreble(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := HookSonos.SetTreble(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := HookSonos.GetTreble()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
}

func loudness(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetLoudness(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetLoudness()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func led(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetLED(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetLED()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func playername(name string) (out []byte, contentType string, errCode int, err error) {
	if name != "" {
		if err := HookSonos.SetZoneName(name); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}
	curName, err := HookSonos.GetZoneName()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(curName), "text/plain", http.StatusOK, nil
}

func shuffle(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetShuffle(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetShuffle()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func repeat(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetRepeat(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetRepeat()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func repeatone(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := HookSonos.SetRepeatOne(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := HookSonos.GetRepeatOne()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func sync() (out []byte, contentType string, errCode int, err error) {
	trackInfo, err := HookSonos.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	trackInfoMinimal := TrackInfoMinimal{
		QuePosition: trackInfo.QuePosition,
		Duration:    trackInfo.Duration,
		Progress:    trackInfo.Progress,
		Title:       trackInfo.Title,
		Creator:     trackInfo.Creator,
		Album:       trackInfo.Album,
	}

	queInfo, err := HookSonos.GetQue()
	if err != nil { // Assume no que; for cases when 3th party apps have control of que
		queInfo.Count, queInfo.TotalCount = 0, 0
	}
	queInfoMinimal := QueInfoMinimal{
		Count:      queInfo.Count,
		TotalCount: queInfo.TotalCount,
	}

	playing, err := HookSonos.GetPlay()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	shuffle, repeat, _, err := HookSonos.GetPlayMode()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curVol, err := HookSonos.GetVolume()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	jsonBytes, err := json.Marshal(SyncInfo{
		Track:   trackInfoMinimal,
		Que:     queInfoMinimal,
		Playing: playing,
		Shuffle: shuffle,
		Repeat:  repeat,
		Volume:  curVol,
	})
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return jsonBytes, "application/json", http.StatusOK, nil
}

func yt(query string) (out []byte, contentType string, errCode int, err error) {
	search := ytsearch.VideoSearch(query)
	results, err := search.Next()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	resultsMinimal := []YTInfoMinimal{}
	for _, result := range results.Videos {
		resultsMinimal = append(resultsMinimal, YTInfoMinimal{
			ID:        result.ID,
			Title:     result.Title,
			Duration:  result.Duration,
			ViewCount: result.ViewCount,
			Creator:   result.Channel.Title,
		})
	}

	jsonBytes, err := json.Marshal(resultsMinimal)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return jsonBytes, "application/json", http.StatusOK, nil
}

func uri(uri string) (out []byte, contentType string, errCode int, err error) {
	resp, err := http.Get(uri)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	bodyEncoded := base64.StdEncoding.EncodeToString(body)

	return []byte(bodyEncoded), "text/plain", http.StatusOK, nil
}
