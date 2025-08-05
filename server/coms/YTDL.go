package coms

import (
	"HG75/coms/auth"
	"bufio"
	"io"
	"net/http"
	"slices"
	"strings"

	"github.com/kkdai/youtube/v2"
)

var ytdlCommands = Commands{
	"ytdl": Command{
		AuthLevel: auth.AuthLevelUser, Roles: []string{},
		Description:     "Download a video from YouTube.",
		AutoComplete:    []string{},
		ArgsDescription: "[url] [mp4]? [audio]? [low]?",
		ArgsLen:         [2]int{1, 4},
		Exec: func(user auth.User, args ...string) (con []byte, typ string, code int, err error) {
			forcedTyp := ""
			if slices.Contains(args, "mp4") {
				forcedTyp = TypeMP4
			}
			fileBytes, fileName, err := DownloadVideo(args[0], slices.Contains(args, "audio"), slices.Contains(args, "low"), forcedTyp)
			if err != nil {
				return []byte{}, "", http.StatusBadRequest, err
			}
			return fileBytes, TypeVideo + fileName, http.StatusOK, nil
		},
	},
}

func DownloadVideo(URL string, AudioOnly bool, LowQuality bool, ForceType string) ([]byte, string, error) {
	client, vid := &youtube.Client{}, &youtube.Video{}
	for i := range 10 {
		v, err := client.GetVideo(URL)
		if err != nil {
			if i == 9 {
				return []byte{}, "", err
			}
			continue
		}
		vid = v
		break
	}
	formats := vid.Formats.WithAudioChannels()
	if AudioOnly {
		formats = formats.Select(func(f youtube.Format) bool { return f.FPS == 0 })
	} else {
		formats = formats.Select(func(f youtube.Format) bool { return f.FPS > 0 })
	}
	if ForceType != "" {
		formats = formats.Select(func(f youtube.Format) bool { return strings.Contains(f.MimeType, ForceType) })
	}
	if len(formats) == 0 {
		return []byte{}, "", Errors.VideoNotFound
	}
	formats.Sort()
	fIndex := 0
	if LowQuality {
		fIndex = len(formats) - 1
	}
	format := formats[fIndex]
	stream, _, err := client.GetStream(vid, &format)
	if err != nil {
		return []byte{}, "", err
	}
	defer func() { _ = stream.Close() }()
	br := bufio.NewReader(stream)
	fileBytes := []byte{}
	for {
		b, err := br.ReadByte()
		if err == io.EOF {
			break
		}
		if err != nil {
			return []byte{}, "", err
		}
		fileBytes = append(fileBytes, b)
	}
	return fileBytes, sanatize(vid.Title) + "." + strings.Split(strings.Split(format.MimeType, ";")[0], "/")[1], nil
}
