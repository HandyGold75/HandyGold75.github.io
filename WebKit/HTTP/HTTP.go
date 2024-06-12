//go:build js && wasm

package HTTP

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/JS"
	"bufio"
	"crypto/sha1"
	"crypto/sha512"
	"crypto/tls"
	"encoding/json"
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

type config struct {
	Server         string
	RememberSignIn bool
	Token          string
}

var (
	UnauthorizedCallback = func() {}

	transportRules = func() *http.Transport {
		transport := http.DefaultTransport.(*http.Transport).Clone()
		transport.TLSClientConfig = &tls.Config{ServerName: "wss.handygold75.com"}
		return transport
	}()

	defaultConfig = config{
		Server:         "https.HandyGold75.com:17500",
		RememberSignIn: true,
		Token:          "",
	}

	Config = defaultConfig
)

func (cfg *config) Load() {
	if JS.CacheGet("HTTP") == "" {
		cfgBytes, _ := json.Marshal(&defaultConfig)
		JS.CacheSet("HTTP", string(cfgBytes))
	}

	err := json.Unmarshal([]byte(JS.CacheGet("HTTP")), &Config)
	if err != nil {
		Config = defaultConfig
	}
}

func (cfg *config) Set(key string, value string) error {
	switch strings.ToLower(key) {
	case "server":
		Config.Server = value
	case "remembersignin":
		Config.RememberSignIn = strings.ToLower(value) == "true"
	case "token":
		Config.Token = value
	}

	cfgBytes, err := json.Marshal(&Config)
	if err != nil {
		return err
	}
	JS.CacheSet("HTTP", string(cfgBytes))

	return nil
}

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

func isAuthenticated(callback func(error)) {
	if Config.Token == "" {
		callback(WebKit.ErrWebKit.HTTPUnauthorized)
		return
	}
	if Config.Server == "" {
		callback(WebKit.ErrWebKit.HTTPUnauthorized)
		return
	}

	res, err := (&http.Client{Transport: transportRules}).PostForm("https://"+Config.Server+"/auth", url.Values{
		"token": []string{Config.Token},
	})
	if err != nil {
		callback(err)
		return
	}
	defer res.Body.Close()

	if res.StatusCode == http.StatusTooManyRequests {
		callback(errors.New(strconv.Itoa(http.StatusTooManyRequests) + " StatusTooManyRequest retry-after:" + res.Header.Get("retry-after")))
		return
	}
	if res.StatusCode != 200 {
		callback(WebKit.ErrWebKit.HTTPUnauthorized)
		return
	}

	callback(nil)
	return
}

func IsAuthenticated(callback func(error)) {
	go isAuthenticated(callback)
}

func IsMaybeAuthenticated() bool {
	if Config.Token == "" {
		return false
	}
	if Config.Server == "" {
		return false
	}
	return true
}

func authenticate(callback func(error), username string, password string) {
	if Config.Server == "" {
		callback(WebKit.ErrWebKit.HTTPNoServerSpecified)
		return
	}

	res, err := (&http.Client{Transport: transportRules}).PostForm("https://"+Config.Server+"/auth", url.Values{
		"usrHash": []string{Sha1(username + Sha512(password))},
		"pswHash": []string{Sha512(Sha512(password) + time.Now().Format(time.DateTime))},
	})
	if err != nil {
		callback(err)
		return
	}
	defer res.Body.Close()

	if res.StatusCode == http.StatusTooManyRequests {
		callback(errors.New(strconv.Itoa(http.StatusTooManyRequests) + " StatusTooManyRequest retry-after:" + res.Header.Get("retry-after")))
		return
	}
	if res.StatusCode != 200 {
		callback(WebKit.ErrWebKit.HTTPUnauthorized)
		return
	}
	token := res.Header.Get("token")
	if token != "" {
		Config.Set("token", token)
		callback(nil)
		return
	}

	callback(WebKit.ErrWebKit.HTTPUnexpectedResponse)
}

func Authenticate(callback func(error), username string, password string) {
	go authenticate(callback, username, password)
}

// Returns string in case response is type text/*
// Returns []byte in case response is type application/json
func send(callback func(string, []byte, error), com string, args ...string) {
	if Config.Token == "" {
		callback("", []byte{}, WebKit.ErrWebKit.HTTPUnauthorized)
		UnauthorizedCallback()
		return
	}
	if Config.Server == "" {
		Config.Set("token", "")
		callback("", []byte{}, WebKit.ErrWebKit.HTTPNoServerSpecified)
		UnauthorizedCallback()
		return
	}

	req, err := http.NewRequest("POST", "https://"+Config.Server+"/com", strings.NewReader(url.Values{
		"com":  []string{com},
		"args": []string{strings.Join(args, "%20")},
	}.Encode()))
	if err != nil {
		callback("", []byte{}, err)
		return
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("token", Config.Token)

	res, err := (&http.Client{Transport: transportRules}).Do(req)
	if err != nil {
		callback("", []byte{}, err)
		return
	}
	defer res.Body.Close()

	if res.StatusCode < 200 || res.StatusCode >= 300 {
		callback("", []byte{}, errors.New(strconv.Itoa(res.StatusCode)+": "+res.Header.Get("x-error")))

		if res.StatusCode == http.StatusUnauthorized {
			Config.Set("token", "")
			UnauthorizedCallback()
		}
		return
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		callback("", []byte{}, err)
		return
	}

	bodyType := res.Header.Get("Content-Type")
	if strings.HasPrefix(bodyType, "text/") {
		callback(string(body), []byte{}, nil)
		return

	} else if strings.HasPrefix(bodyType, "application/json") {
		callback("", body, nil)
		return

	} else if strings.HasPrefix(bodyType, "video/") {
		if err := downloadToFile(strings.Replace(bodyType, "video/", "", 1), &body); err != nil {
			callback("", []byte{}, err)
			return
		}

		callback("downloaded: "+strings.Replace(bodyType, "video/", "", 1), []byte{}, nil)
		return

	}

	callback("", []byte{}, WebKit.ErrWebKit.HTTPUnexpectedResponse)
	return
}

func Send(callback func(string, []byte, error), com string, args ...string) {
	go send(callback, com, args...)
}
