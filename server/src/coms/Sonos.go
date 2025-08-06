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
		Track                    TrackInfoMinimal
		Que                      QueInfoMinimal
		Playing, Shuffle, Repeat bool
		Volume                   int
	}

	TrackInfoMinimal struct {
		QuePosition           int
		Duration, Progress    string
		Title, Creator, Album string
	}

	QueInfoMinimal struct {
		Count, TotalCount int
	}

	YTInfoMinimal struct {
		ID             string
		Title, Creator string
		Duration       int
		ViewCount      int
	}
)

var sonosCommands = Commands{"sonos": {
	AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
	Description: "Interact with sonos music boxes.",
	Commands: Commands{
		"track": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get current track.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				jsonBytes, err := json.Marshal(trackInfo)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"state": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get state.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				sts, err := hookSonos.GetCurrentTransportState()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(sts), TypeTXT, http.StatusOK, nil
			},
		},
		"stop": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Stop play state.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				err = hookSonos.Stop()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				sts, err := hookSonos.GetCurrentTransportState()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(sts), TypeTXT, http.StatusOK, nil
			},
		},
		"play": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set play state.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if state {
						if err := hookSonos.Play(); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					} else {
						if err := hookSonos.Pause(); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					}
					for i := range 10 {
						sts, err := hookSonos.GetTransitioning()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						if sts {
							time.Sleep(time.Millisecond * time.Duration(max(50, 600-(i*200))))
							continue
						}
					}
				}
				state, err := hookSonos.GetPlay()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"mute": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set mute state.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetMute(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetMute()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"volume": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Control media volume.",
			AutoComplete:    []string{},
			ArgsDescription: "[0:100|+X|-X]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					volume, err := strconv.Atoi(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if strings.HasPrefix(args[0], "+") || strings.HasPrefix(args[0], "-") {
						volumeOld, err := hookSonos.GetVolume()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						if err := hookSonos.SetVolume(volumeOld + volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					} else {
						if err := hookSonos.SetVolume(volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					}
				}
				volume, err := hookSonos.GetVolume()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(volume)), TypeTXT, http.StatusOK, nil
			},
		},
		"seek": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Control track progress.",
			AutoComplete:    []string{},
			ArgsDescription: "[0:X|+X|-X]",
			ArgsLen:         [2]int{1, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				newIndex, err := strconv.Atoi(args[0])
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				if strings.HasPrefix(args[0], "+") || strings.HasPrefix(args[0], "-") {
					if err := hookSonos.SeekTimeDelta(newIndex); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				} else {
					if err := hookSonos.SeekTime(newIndex); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(trackInfo.Progress), TypeTXT, http.StatusOK, nil
			},
		},
		"position": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Control que position.",
			AutoComplete:    []string{},
			ArgsDescription: "[1:X|+X|-X]",
			ArgsLen:         [2]int{1, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				newIndex, err := strconv.Atoi(args[0])
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				if strings.HasPrefix(args[0], "+") || strings.HasPrefix(args[0], "-") {
					trackInfo, err := hookSonos.GetTrackInfo()
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SeekTrack(trackInfo.QuePosition + newIndex); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				} else {
					if err := hookSonos.SeekTrack(newIndex); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(trackInfo.QuePosition)), TypeTXT, http.StatusOK, nil
			},
		},
		"next": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Next que position.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if err := hookSonos.Next(); err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(trackInfo.QuePosition)), TypeTXT, http.StatusOK, nil
			},
		},
		"previous": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Previous que position.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if err := hookSonos.Previous(); err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(trackInfo.QuePosition)), TypeTXT, http.StatusOK, nil
			},
		},
		"que": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description: "Get, set, remove or clear que.",
			Commands: Commands{
				"get": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
					Description:     "Get que.",
					AutoComplete:    []string{},
					ArgsDescription: "",
					ArgsLen:         [2]int{0, 0},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						if hookSonos == nil {
							return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
						}
						queInfo, err := hookSonos.GetQue()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						jsonBytes, err := json.Marshal(queInfo)
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						return jsonBytes, TypeJSON, http.StatusOK, nil
					},
				},
				"add": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
					Description:     "Set que.",
					AutoComplete:    []string{},
					ArgsDescription: "[track]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						if hookSonos == nil {
							return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
						}
						return []byte{}, "", http.StatusInternalServerError, errors.New("sonos add is broken") // TODO: Fix
						// if strings.HasPrefix(args[0], "https://open.spotify.com/") {
						// 	uri_args := strings.Replace(args[0], "https://open.spotify.com/", "", 1)
						// 	id_type := strings.Split(uri_args, "/")[0]
						// 	id := strings.Split(strings.Replace(uri_args, id_type+"/", "", 1), "?")[0]
						// 	uri := "spotify%3a" + id_type + "%3a" + id
						// 	uri = "x-sonos-spotify:" + "spotify%3a" + id_type + "%3a" + id + "?sid=9\u0026flags=8232\u0026sn=3"
						// }
						// trackInfo, err := hookSonos.GetTrackInfo()
						// if err != nil {
						// 	return []byte{}, "", http.StatusBadRequest, err
						// }
						// if err := hookSonos.QueAdd(args[0], trackInfo.QuePosition, true); err != nil {
						// 	return []byte{}, "", http.StatusBadRequest, err
						// }
						// queInfo, err := hookSonos.GetQue()
						// if err != nil {
						// 	return []byte{}, "", http.StatusBadRequest, err
						// }
						// return []byte(strconv.Itoa(queInfo.TotalCount)), TypeTXT, http.StatusOK, nil
					},
				},
				"remove": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
					Description:     "Remove que.",
					AutoComplete:    []string{},
					ArgsDescription: "[index]",
					ArgsLen:         [2]int{1, 1},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						if hookSonos == nil {
							return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
						}
						newIndex, err := strconv.Atoi(args[0])
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						if err := hookSonos.QueRemove(newIndex); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						queInfo, err := hookSonos.GetQue()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						return []byte(strconv.Itoa(queInfo.TotalCount)), TypeTXT, http.StatusOK, nil
					},
				},
				"clear": {
					AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
					Description:     "Clear que.",
					AutoComplete:    []string{},
					ArgsDescription: "",
					ArgsLen:         [2]int{0, 0},
					Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
						if hookSonos == nil {
							return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
						}
						if err := hookSonos.QueClear(); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						queInfo, err := hookSonos.GetQue()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						return []byte(strconv.Itoa(queInfo.TotalCount)), TypeTXT, http.StatusOK, nil
					},
				},
			},
		},
		"bass": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get, set or change bass.",
			AutoComplete:    []string{},
			ArgsDescription: "[0:10|+X|-X]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					volume, err := strconv.Atoi(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if strings.HasPrefix(args[0], "+") || strings.HasPrefix(args[0], "-") {
						volumeOld, err := hookSonos.GetBass()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						if err := hookSonos.SetBass(volumeOld + volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					} else {
						if err := hookSonos.SetBass(volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					}
				}
				volume, err := hookSonos.GetBass()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(volume)), TypeTXT, http.StatusOK, nil
			},
		},
		"treble": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get, set or change treble.",
			AutoComplete:    []string{},
			ArgsDescription: "[0:10|+X|-X]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					volume, err := strconv.Atoi(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if strings.HasPrefix(args[0], "+") || strings.HasPrefix(args[0], "-") {
						volumeOld, err := hookSonos.GetTreble()
						if err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
						if err := hookSonos.SetTreble(volumeOld + volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					} else {
						if err := hookSonos.SetTreble(volume); err != nil {
							return []byte{}, "", http.StatusBadRequest, err
						}
					}
				}
				volume, err := hookSonos.GetTreble()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.Itoa(volume)), TypeTXT, http.StatusOK, nil
			},
		},
		"loudness": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set loudness.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetLoudness(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetLoudness()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"led": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set speaker led.",
			AutoComplete:    []string{},
			ArgsDescription: "[0|1|get]",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetLED(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetLED()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"playername": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set speaker led.",
			AutoComplete:    []string{},
			ArgsDescription: "[name]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 && args[0] != "" {
					if err := hookSonos.SetZoneName(args[0]); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				curName, err := hookSonos.GetZoneName()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(curName), TypeTXT, http.StatusOK, nil
			},
		},
		"shuffle": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set shuffle.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetShuffle(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetShuffle()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"repeat": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set repeat.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetRepeat(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetRepeat()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"repeatone": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get or set repeatone.",
			AutoComplete:    []string{},
			ArgsDescription: "[true|false]?",
			ArgsLen:         [2]int{0, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				if len(args) > 0 {
					state, err := strconv.ParseBool(args[0])
					if err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
					if err := hookSonos.SetRepeatOne(state); err != nil {
						return []byte{}, "", http.StatusBadRequest, err
					}
				}
				state, err := hookSonos.GetRepeatOne()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(strconv.FormatBool(state)), TypeTXT, http.StatusOK, nil
			},
		},
		"favorites": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get current favorites.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				favInfo, err := hookSonos.GetSonosFavorites()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				jsonBytes, err := json.Marshal(favInfo)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"radioshows": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get current radioshows.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				radInfo, err := hookSonos.GetRadioShows()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				jsonBytes, err := json.Marshal(radInfo)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"radiostations": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get current radiostations.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				radInfo, err := hookSonos.GetRadioStations()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				jsonBytes, err := json.Marshal(radInfo)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"sync": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get current track (minimal) + que (minimal) + diverce device states.",
			AutoComplete:    []string{},
			ArgsDescription: "",
			ArgsLen:         [2]int{0, 0},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				if hookSonos == nil {
					return []byte{}, "", http.StatusInternalServerError, Errors.SonosNotHooked
				}
				trackInfo, err := hookSonos.GetTrackInfo()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				trackInfoMinimal := TrackInfoMinimal{
					QuePosition: trackInfo.QuePosition,
					Duration:    trackInfo.Duration, Progress: trackInfo.Progress,
					Title: trackInfo.Title, Creator: trackInfo.Creator, Album: trackInfo.Album,
				}
				queInfo, err := hookSonos.GetQue()
				if err != nil { // Assume no que; for cases when 3th party apps have control of que
					queInfo.Count, queInfo.TotalCount = 0, 0
				}
				queInfoMinimal := QueInfoMinimal{
					Count: queInfo.Count, TotalCount: queInfo.TotalCount,
				}
				playing, err := hookSonos.GetPlay()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				shuffle, repeat, _, err := hookSonos.GetPlayMode()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				volume, err := hookSonos.GetVolume()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				jsonBytes, err := json.Marshal(SyncInfo{
					Track: trackInfoMinimal, Que: queInfoMinimal,
					Playing: playing, Shuffle: shuffle, Repeat: repeat,
					Volume: volume,
				})
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"yt": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get query from yt.",
			AutoComplete:    []string{},
			ArgsDescription: "[query]",
			ArgsLen:         [2]int{1, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				search := ytsearch.VideoSearch(args[0])
				results, err := search.Next()
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				resultsMinimal := []YTInfoMinimal{}
				for _, result := range results.Videos {
					resultsMinimal = append(resultsMinimal, YTInfoMinimal{
						ID:    result.ID,
						Title: result.Title, Creator: result.Channel.Title,
						Duration:  result.Duration,
						ViewCount: result.ViewCount,
					})
				}
				jsonBytes, err := json.Marshal(resultsMinimal)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return jsonBytes, TypeJSON, http.StatusOK, nil
			},
		},
		"url2base64": {
			AuthLevel: auth.AuthLevelUser, Roles: []string{"Home"},
			Description:     "Get base64 from url.",
			AutoComplete:    []string{},
			ArgsDescription: "[url]",
			ArgsLen:         [2]int{1, 1},
			Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
				resp, err := http.Get(args[0])
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				body, err := io.ReadAll(resp.Body)
				if err != nil {
					return []byte{}, "", http.StatusBadRequest, err
				}
				return []byte(base64.StdEncoding.EncodeToString(body)), TypeTXT, http.StatusOK, nil
			},
		},
	},
}}
