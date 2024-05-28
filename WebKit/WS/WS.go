//go:build js && wasm

package WS

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/JS"
	"bufio"
	"crypto/sha1"
	"crypto/sha512"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

var (
	UnauthorizedCallback = func() {}
)

func Sha1(s string) string {
	hasher := sha1.New()
	hasher.Write([]byte(s))
	return fmt.Sprintf("%x", hasher.Sum(nil))
}

func Sha512(s string) string {
	hasher := sha512.New()
	hasher.Write([]byte(s))
	return fmt.Sprintf("%x", hasher.Sum(nil))
}

func downloadToFile(name string, data *[]byte) error {
	file, err := os.Create(name)
	if err != nil {
		return err
	}
	defer file.Close()

	bw := bufio.NewWriter(file)

	for _, b := range *data {
		bw.WriteByte(b)
	}

	return nil
}

func SetServer(server string) {
	JS.CacheSet("server", server)
}

func Authenticate(username string, password string) error {
	server := JS.CacheGet("server")
	if server == "" {
		return WebKit.ErrWebKit.WSNoServerSpecified
	}

	res, err := (&http.Client{}).PostForm("https://"+server+"/auth", url.Values{
		"usrHash": []string{Sha1(username + Sha512(password))},
		"pswHash": []string{Sha512(Sha512(password) + time.Now().Format(time.DateTime))},
	})
	if err != nil {
		return err
	}
	if res.StatusCode != 200 {
		return WebKit.ErrWebKit.WSUnauthorized
	}

	JS.CacheSet("token", res.Header.Get("Authorization"))

	return nil
}

func IsAuthenticated() bool {
	token := JS.CacheGet("token")
	if token == "" {
		return false
	}
	server := JS.CacheGet("server")
	if server == "" {
		return false
	}

	res, err := (&http.Client{}).PostForm("https://"+server+"/auth", url.Values{
		"token": []string{token},
	})
	if err != nil || res.StatusCode != 200 {
		return false
	}

	return true
}

func Send(com string, args ...string) (string, error) {
	token := JS.CacheGet("token")
	if token == "" {
		UnauthorizedCallback()
		return "", WebKit.ErrWebKit.WSUnauthorized
	}
	server := JS.CacheGet("server")
	if server == "" {
		UnauthorizedCallback()
		return "", WebKit.ErrWebKit.WSNoServerSpecified
	}

	req, err := http.NewRequest("POST", "https://"+server+"/com", strings.NewReader(url.Values{
		"com":  []string{com},
		"args": []string{strings.Join(args, " ")},
	}.Encode()))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Authorization", token)

	res, err := (&http.Client{}).Do(req)
	if err != nil {
		return "", err
	}

	if res.StatusCode < 200 || res.StatusCode >= 300 {
		if res.StatusCode == http.StatusUnauthorized {
			UnauthorizedCallback()
		}
		return "", errors.New(strconv.Itoa(res.StatusCode) + ": " + res.Header.Get("x-error"))
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}

	bodyType := res.Header.Get("Content-Type")
	if strings.HasPrefix(bodyType, "text/") {
		return string(body), nil

	} else if strings.HasPrefix(bodyType, "video/") {
		if err := downloadToFile(strings.Replace(bodyType, "video/", "", 1), &body); err != nil {
			return "", err
		}

		return "downloaded: " + strings.Replace(bodyType, "video/", "", 1), nil

	}

	return "", WebKit.ErrWebKit.WSUnexpectedResponse
}
