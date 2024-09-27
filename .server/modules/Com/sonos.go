package Com

import (
	"HG75/lib/Gonos"
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
		QuePosition string
		Duration    string
		Progress    string
		Title       string
		Creator     string
		Album       string
	}

	QueInfoMinimal struct {
		Count      string
		TotalCount string
	}

	YTInfoMinimal struct {
		ID        string
		Title     string
		Duration  int
		ViewCount int
		Creator   string
	}
)

var (
	SonosComs = Commands{
		"sonos": Command{
			RequiredAuthLevel: Auth.AuthMap["user"],
			RequiredRoles:     []string{"Home"},
			Description:       "Sonos interface.",
			DetailedDescription: "Interact sonos music boxes. Usage: sonos [track|play|mute|volume|seek|position|que|add|remove|clear|bass|treble|loudness|led|playername|shuffle|repeat|repeatone|favorites|radioshows|radiostations|sync|yt|uri] [args?]...\r\n" +
				"  track\r\n    Get current track.\r\n" +
				"  play [0|1]\r\n    Play or pause track.\r\n" +
				"  mute [0|1]\r\n    Mute or unmute media.\r\n" +
				"  volume [0:100|+X|-X|get]\r\n    Control media volume.\r\n" +
				"  seek [0:X|+X|-X]\r\n    Control track progress.\r\n" +
				"  position [0:X|+X|-X]\r\n    Control que position.\r\n" +
				"  que\r\n    Get current que.\r\n" +
				"  add [track]\r\n    Add track to que.\r\n" + // TODO: Broken
				"  remove [index]\r\n    Remove track from que.\r\n" +
				"  clear\r\n    Clear que.\r\n" +
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
			AutoComplete:       []string{"track", "play", "mute", "volume", "seek", "position", "que", "add", "remove", "clear", "bass", "treble", "loudness", "led", "playername", "shuffle", "repeat", "repeatone", "favorites", "radioshows", "radiostations", "sync", "yt", "uri"},
			ArgsLen:            [2]int{1, 5},
			Function:           SonosInterface,
		},
	}
)

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

	case "play":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos play requires 1 argument")
		}

		if args[1] == "0" {
			return play(false)
		} else if args[1] == "1" {
			return play(true)
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos play state should be 0 or 1")

	case "mute":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos mute requires 1 argument")
		}

		if args[1] == "0" {
			return mute(false)
		} else if args[1] == "1" {
			return mute(true)
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos mute state should be 0 or 1")

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
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos que requires 0 argument")
		}

		queInfo, err := zp.GetQueInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		jsonBytes, err := json.Marshal(queInfo)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		return jsonBytes, "application/json", http.StatusOK, nil

	case "position":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos position requires 1 argument")
		}

		return position(args[1])

	case "add":
		return []byte{}, "", http.StatusInternalServerError, errors.New("sonos add is broken")

		// if len(args) != 2 {
		// 	return []byte{}, "", http.StatusBadRequest, errors.New("sonos remove requires 1 argument")
		// }

		// return add(args[1])

	case "remove":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos remove requires 1 argument")
		}

		return remove(args[1])

	case "clear":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos clear requires 0 argument")
		}

		return clear()

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

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos loudness state should be 0 or 1")

	case "led":
		if len(args) != 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos led requires 1 argument")
		}

		if args[1] == "0" {
			return led(false)
		} else if args[1] == "1" {
			return led(true)
		} else if args[1] == "get" {
			curState, err := zp.GetLedState()
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}

			return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
		}

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos led state should be 0 or 1")

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

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos shuffle state should be 0 or 1")

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

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeat state should be 0 or 1")

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

		return []byte{}, "", http.StatusBadRequest, errors.New("sonos repeatone state should be 0 or 1")

	case "favorites":
		if len(args) != 1 {
			return []byte{}, "", http.StatusBadRequest, errors.New("sonos favorites requires 0 argument")
		}

		favInfo, err := zp.GetFavoritesInfo()
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

		radInfo, err := zp.GetFavoritesRadioShowsInfo()
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

		radInfo, err := zp.GetFavoritesRadioStationsInfo()
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

	return []byte{}, "", http.StatusBadRequest, errors.New("sonos operation should be track, play, mute, volume, seek, position, que, add, remove, clear, bass, treble, loudness, led, playername, shuffle, repeat, repeatone, favorites, radioshows, radiostations, sync, yt or uri")
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

	curState := false
	for i := 0; i < 10; i++ {
		curState, err = zp.GetState()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		if curState {
			break
		}

		time.Sleep(time.Millisecond * time.Duration(100))
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
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
		trackInfo, err := zp.GetTrackInfo()
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		oldTime, err := time.Parse(time.TimeOnly, trackInfo.Progress)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		oldTime = oldTime.Add(time.Second * time.Duration(newIndex))

		if err := zp.Seek(oldTime.Clock()); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		newTime, err := time.Parse(time.TimeOnly, "00:00:00")
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		newTime = newTime.Add(time.Second * time.Duration(newIndex))

		if err := zp.Seek(newTime.Clock()); err != nil {
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

		oldIndex, err := strconv.Atoi(trackInfo.QuePosition)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

		if err := zp.PlayFromQue(oldIndex + newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}

	} else {
		if err := zp.PlayFromQue(newIndex); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}

	trackInfo, err := zp.GetTrackInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(trackInfo.QuePosition), "text/plain", http.StatusOK, nil
}

func add(uri string) (out []byte, contentType string, errCode int, err error) {
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

	if err := zp.AddToQue(uri, trackInfo.QuePosition, true); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQueInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(queInfo.TotalCount), "text/plain", http.StatusOK, nil
}

func remove(index string) (out []byte, contentType string, errCode int, err error) {
	newIndex, err := strconv.Atoi(index)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	if err := zp.RemoveFromQue(newIndex); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQueInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(queInfo.TotalCount), "text/plain", http.StatusOK, nil
}

func clear() (out []byte, contentType string, errCode int, err error) {
	if err := zp.ClearQue(); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	queInfo, err := zp.GetQueInfo()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(queInfo.TotalCount), "text/plain", http.StatusOK, nil
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
	if err := zp.SetLedState(state); err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	curState, err := zp.GetLedState()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	return []byte(strconv.FormatBool(curState)), "text/plain", http.StatusOK, nil
}

func playername(name string) (out []byte, contentType string, errCode int, err error) {
	if name != "" {
		if err := zp.SetPlayerName(name); err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
	}
	curName, err := zp.GetPlayerName()
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
	trackInfoRaw, err := zp.GetTrackInfoRaw()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	trackMetaDataItem, err := trackInfoRaw.ParseMetaData()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	quePos, err := strconv.Atoi(trackInfoRaw.Track)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	trackInfo := TrackInfoMinimal{
		QuePosition: strconv.Itoa(quePos - 1),
		Duration:    trackInfoRaw.TrackDuration,
		Progress:    trackInfoRaw.RelTime,
		Title:       trackMetaDataItem.Title,
		Creator:     trackMetaDataItem.Creator,
		Album:       trackMetaDataItem.Album,
	}

	queInfoRaw, err := zp.GetQueInfoRaw(0, 0)
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	queInfo := QueInfoMinimal{
		Count:      queInfoRaw.NumberReturned,
		TotalCount: queInfoRaw.TotalMatches,
	}

	playing, err := zp.GetState()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	mode, err := zp.GetPlayMode()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}
	modeBools, ok := Gonos.PLAYMODES[mode]
	if !ok {
		return []byte{}, "", http.StatusBadRequest, Gonos.ErrSonos.ErrUnexpectedResponse
	}

	curVol, err := zp.GetVolume()
	if err != nil {
		return []byte{}, "", http.StatusBadRequest, err
	}

	jsonBytes, err := json.Marshal(SyncInfo{
		Track:   trackInfo,
		Que:     queInfo,
		Playing: playing,
		Shuffle: modeBools[0],
		Repeat:  modeBools[1],
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
