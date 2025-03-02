package Com

import (
	"HG75/modules/Auth"
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

var SonosComs = Commands{
	"sonos": Command{
		RequiredAuthLevel: Auth.AuthMap["user"],
		RequiredRoles:     []string{"Home"},
		Description:       "Sonos interface.",
		DetailedDescription: "Interact sonos music boxes. Usage: sonos [track|state|stop|play|mute|volume|seek|position|next|previous|que|add|remove|clear|bass|treble|loudness|led|playername|shuffle|repeat|repeatone|favorites|radioshows|radiostations|sync|yt|uri] [args?]...\r\n" +
			"  track\r\n    Get current track.\r\n" +
			"  state\r\n    Get state.\r\n" +
			"  stop\r\n    Stop play state.\r\n" +
			"  play [0|1|get]\r\n    Get or set play state.\r\n" +
			"  mute [0|1|get]\r\n    Get or set mute state.\r\n" +
			"  volume [0:100|+X|-X|get]\r\n    Control media volume.\r\n" +
			"  seek [0:X|+X|-X]\r\n    Control track progress.\r\n" +
			"  position [1:X|+X|-X]\r\n    Control que position.\r\n" +
			"  next [0:X|+X|-X]\r\n    Next que position.\r\n" +
			"  previous [0:X|+X|-X]\r\n    Previous que position.\r\n" +
			"  que [get|add|remove|clear] [track|index]?\r\n    Get, set, remove or clear que.\r\n" +
			"  bass [0:10|+X|-X|get]\r\n    Get, set or change bass.\r\n" +
			"  treble [0:10|+X|-X|get]\r\n    Get, set or change treble.\r\n" +
			"  loudness [0|1|get]\r\n    Get or set loudness.\r\n" +
			"  led [0|1|get]\r\n    Get or set speaker led.\r\n" +
			"  playername [name]?\r\n    Get or set speaker led.\r\n" +
			"  shuffle [0|1|get]\r\n    Get or set shuffle.\r\n" +
			"  repeat [0|1|get]\r\n    Get or set repeat.\r\n" +
			"  repeatone [0|1|get]\r\n    Get or set repeatone.\r\n" +
			"  favorites\r\n    Get current favorites.\r\n" +
			"  radioshows\r\n    Get current radioshows.\r\n" +
			"  radiostations\r\n    Get current radiostations.\r\n" +
			"  sync\r\n    Get current track (minimal) + que (minimal) + diverce device states.\r\n" +
			"  yt [query]\r\n    Get query from yt.\r\n" +
			"  uri [uri]\r\n    Get base64 from album art uri.\r\n",
		ExampleDescription: "play",
		AutoComplete:       []string{"track", "state", "stop", "play", "mute", "volume", "seek", "position", "next", "previous", "que", "add", "remove", "clear", "bass", "treble", "loudness", "led", "playername", "shuffle", "repeat", "repeatone", "favorites", "radioshows", "radiostations", "sync", "yt", "uri"},
		ArgsLen:            [2]int{1, 5},
		Function:           SonosInterface,
	},
}

func SonosInterface(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("sonos requires at least 1 argument")
	}

	switch args[0] {
	case "track":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos track requires 0 argument")
		}

		trackInfo, err := zp.GetTrackInfo()
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

		err := zp.Stop()
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
			curState, err := zp.GetPlay()
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
			curState, err := zp.GetMute()
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
			curVol, err := zp.GetVolume()
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
			queInfo, err := zp.GetQue()
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
			curVol, err := zp.GetBass()
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
			curVol, err := zp.GetTreble()
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
			curState, err := zp.GetLoudness()
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
			curState, err := zp.GetLED()
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
			curState, err := zp.GetShuffle()
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
			curState, err := zp.GetRepeat()
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
			curState, err := zp.GetRepeatOne()
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

		favInfo, err := zp.GetSonosFavorites()
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

		radInfo, err := zp.GetRadioShows()
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

		radInfo, err := zp.GetRadioStations()
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
	curState, err := zp.GetCurrentTransportState()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(curState), "text/plain", http.StatusOK, nil
}

func play(state bool) (out []byte, contentType string, errCode int, err error) {
	if state {
		if err := zp.Play(); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	} else {
		if err := zp.Pause(); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	for i := 0; i < 10; i++ {
		curState, err := zp.GetTransitioning()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		if curState {
			time.Sleep(time.Millisecond * time.Duration(max(50, 600-(i*200))))
			continue
		}

		curState, err = zp.GetPlay()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
	}

	return []byte("false"), "text/plain", http.StatusOK, nil
}

func mute(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetMute(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetMute()
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
		oldVol, err := zp.GetVolume()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := zp.SetVolume(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := zp.SetVolume(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := zp.GetVolume()
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
		if err := zp.SeekTimeDelta(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	} else {
		if err := zp.SeekTime(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	trackInfo, err := zp.GetTrackInfo()
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
		trackInfo, err := zp.GetTrackInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		if err := zp.SeekTrack(trackInfo.QuePosition + newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := zp.SeekTrack(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	trackInfo, err := zp.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(trackInfo.QuePosition)), "text/plain", http.StatusOK, nil
}

func next() (out []byte, contentType string, errCode int, err error) {
	if err := zp.Next(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	trackInfo, err := zp.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(trackInfo.QuePosition)), "text/plain", http.StatusOK, nil
}

func previous() (out []byte, contentType string, errCode int, err error) {
	if err := zp.Previous(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	trackInfo, err := zp.GetTrackInfo()
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

	trackInfo, err := zp.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if err := zp.QueAdd(uri, trackInfo.QuePosition, true); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQue()
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

	if err := zp.QueRemove(newIndex); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQue()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(queInfo.TotalCount)), "text/plain", http.StatusOK, nil
}

func clearq() (out []byte, contentType string, errCode int, err error) {
	if err := zp.QueClear(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQue()
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
		oldVol, err := zp.GetBass()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := zp.SetBass(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := zp.SetBass(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := zp.GetBass()
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
		oldVol, err := zp.GetTreble()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := zp.SetTreble(oldVol + newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := zp.SetTreble(newVol); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	curVol, err := zp.GetTreble()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.Itoa(curVol)), "text/plain", http.StatusOK, nil
}

func loudness(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetLoudness(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetLoudness()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func led(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetLED(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetLED()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func playername(name string) (out []byte, contentType string, errCode int, err error) {
	if name != "" {
		if err := zp.SetZoneName(name); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}
	curName, err := zp.GetZoneName()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(curName), "text/plain", http.StatusOK, nil
}

func shuffle(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetShuffle(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetShuffle()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func repeat(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetRepeat(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetRepeat()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func repeatone(state bool) (out []byte, contentType string, errCode int, err error) {
	if err := zp.SetRepeatOne(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetRepeatOne()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func sync() (out []byte, contentType string, errCode int, err error) {
	trackInfo, err := zp.GetTrackInfo()
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

	queInfo, err := zp.GetQue()
	if err != nil { // Assume no que; for cases when 3th party apps have control of que
		queInfo.Count, queInfo.TotalCount = 0, 0
	}
	queInfoMinimal := QueInfoMinimal{
		Count:      queInfo.Count,
		TotalCount: queInfo.TotalCount,
	}

	playing, err := zp.GetPlay()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	shuffle, repeat, _, err := zp.GetPlayMode()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curVol, err := zp.GetVolume()
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
