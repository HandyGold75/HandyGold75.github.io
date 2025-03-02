package Com

import (
	"HG75/modules/Auth"
	"bufio"
	"errors"
	"io"
	"net/http"
	"slices"
	"strings"
	"unicode"

	"github.com/kkdai/youtube/v2"
)

var YTDLComs = Commands{
	"ytdl": Command{
		RequiredAuthLevel: Auth.AuthMap["user"],
		RequiredRoles:     []string{},
		Description:       "YouTube downloader.",
		DetailedDescription: "Download a video from YouTube. Usage: ytdl [download] [args?]...\r\n" +
			"  download [url] [mp4?] [audio?] [low?]\r\n    Can force mp4 format, audio only and low quality.",
		ExampleDescription: "",
		AutoComplete:       []string{},
		ArgsLen:            [2]int{2, 5},
		Function:           download,
	},
}

func sanatize(title string) string {
	title = strings.Map(func(r rune) rune {
		if unicode.IsLetter(r) || unicode.IsSpace(r) || unicode.IsNumber(r) {
			return r
		}
		return -1
	}, title)

	return strings.ReplaceAll(title, "  ", " ")
}

func DownloadVideo(URL string, AudioOnly bool, LowQuality bool, ForceType string) ([]byte, string, error) {
	client := &youtube.Client{}

	vid := &youtube.Video{}
	for i := 0; i < 10; i++ {
		v, err := client.GetVideo(URL)
		if err == nil {
			vid = v
			break
		}
		if i == 9 {
			return []byte{}, "", err
		}
	}

	formats := vid.Formats.WithAudioChannels()
	if AudioOnly {
		formats = formats.Select(func(f youtube.Format) bool {
			return f.FPS == 0
		})
	} else {
		formats = formats.Select(func(f youtube.Format) bool {
			return f.FPS > 0
		})
	}
	if ForceType != "" {
		formats = formats.Select(func(f youtube.Format) bool {
			return strings.Contains(f.MimeType, ForceType)
		})
	}
	if len(formats) == 0 {
		return []byte{}, "", errors.New("no format was found satisfying filters")
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
	defer stream.Close()

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

func download(user Auth.User, args ...string) (out []byte, contentType string, errCode int, err error) {
	if len(args) < 1 {
		return []byte{}, "", http.StatusBadRequest, errors.New("ytdl requires at least 1 arguments")
	}

	switch args[0] {
	case "download":
		if len(args) < 2 {
			return []byte{}, "", http.StatusBadRequest, errors.New("ytdl download requires 1, 2, 3 or 4 arguments")
		}

		forcedTyp := ""
		if slices.Contains(args, "mp4") {
			forcedTyp = "video/mp4"
		}

		fileBytes, fileName, err := DownloadVideo(args[1], slices.Contains(args, "audio"), slices.Contains(args, "low"), forcedTyp)
		if err != nil {
			return []byte{}, "", http.StatusBadRequest, err
		}
		return fileBytes, "video/" + fileName, http.StatusOK, nil

	default:
	}

	return []byte{}, "", http.StatusBadRequest, errors.New("ytdl operation should be download")
}
