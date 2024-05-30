//go:build js && wasm

package WS

import (
	"HandyGold75/WebKit"
	"HandyGold75/WebKit/JS"
	"bufio"
	"crypto/sha1"
	"crypto/sha512"
	"crypto/tls"
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

	transportSkipVerify = func() *http.Transport {
		customTransport := http.DefaultTransport.(*http.Transport).Clone()
		customTransport.TLSClientConfig = &tls.Config{ServerName: "wss.handygold75.com", InsecureSkipVerify: true}
		return customTransport
	}()
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

func isAuthenticated(callback func(error)) {
	token := JS.CacheGet("token")
	if token == "" {
		callback(WebKit.ErrWebKit.WSUnauthorized)
		return
	}
	server := JS.CacheGet("server")
	if server == "" {
		callback(WebKit.ErrWebKit.WSUnauthorized)
		return
	}

	res, err := (&http.Client{Transport: transportSkipVerify}).PostForm("https://"+server+"/auth", url.Values{
		"token": []string{token},
	})
	if err != nil {
		callback(err)
		return
	}
	if res.StatusCode == http.StatusTooManyRequests {
		callback(errors.New(strconv.Itoa(http.StatusTooManyRequests) + " StatusTooManyRequest retry-after:" + res.Header.Get("retry-after")))
		return
	}
	if res.StatusCode != 200 {
		callback(WebKit.ErrWebKit.WSUnauthorized)
		return
	}

	callback(nil)
	return
}

func IsAuthenticated(callback func(error)) {
	go isAuthenticated(callback)
}

func authenticate(callback func(error), username string, password string) {
	server := JS.CacheGet("server")
	if server == "" {
		callback(WebKit.ErrWebKit.WSNoServerSpecified)
		return
	}

	res, err := (&http.Client{Transport: transportSkipVerify}).PostForm("https://"+server+"/auth", url.Values{
		"usrHash": []string{Sha1(username + Sha512(password))},
		"pswHash": []string{Sha512(Sha512(password) + time.Now().Format(time.DateTime))},
	})
	if err != nil {
		callback(err)
		return
	}
	if res.StatusCode == http.StatusTooManyRequests {
		callback(errors.New(strconv.Itoa(http.StatusTooManyRequests) + " StatusTooManyRequest retry-after:" + res.Header.Get("retry-after")))
		return
	}
	if res.StatusCode != 200 {
		callback(WebKit.ErrWebKit.WSUnauthorized)
		return
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		callback(err)
		return
	}
	// JS.CacheSet("token", string(body))

	bodyType := res.Header.Get("Content-Type") // WHY ME NOT GET HEAD!?!!!?
	if strings.HasPrefix(bodyType, "text/") {
		JS.CacheSet("token", string(body))
		callback(nil)
		return
	}

	callback(WebKit.ErrWebKit.WSUnexpectedResponse)
}

func Authenticate(callback func(error), username string, password string) {
	go authenticate(callback, username, password)
}

func send(callback func(string, error), com string, args ...string) {
	token := JS.CacheGet("token")
	if token == "" {
		UnauthorizedCallback()
		callback("", WebKit.ErrWebKit.WSUnauthorized)
		return
	}
	server := JS.CacheGet("server")
	if server == "" {
		UnauthorizedCallback()
		callback("", WebKit.ErrWebKit.WSNoServerSpecified)
		return
	}

	req, err := http.NewRequest("POST", "https://"+server+"/com", strings.NewReader(url.Values{
		"com":  []string{com},
		"args": []string{strings.Join(args, " ")},
	}.Encode()))
	if err != nil {
		callback("", err)
		return
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Authorization", token)

	res, err := (&http.Client{Transport: transportSkipVerify}).Do(req)
	if err != nil {
		callback("", err)
		return
	}

	if res.StatusCode < 200 || res.StatusCode >= 300 {
		if res.StatusCode == http.StatusUnauthorized {
			UnauthorizedCallback()
		}
		callback("", errors.New(strconv.Itoa(res.StatusCode)+": "+res.Header.Get("x-error")))
		return
	}

	body, err := io.ReadAll(res.Body)
	if err != nil {
		callback("", err)
		return
	}

	bodyType := res.Header.Get("Content-Type")
	if strings.HasPrefix(bodyType, "text/") {
		callback(string(body), nil)
		return

	} else if strings.HasPrefix(bodyType, "video/") {
		if err := downloadToFile(strings.Replace(bodyType, "video/", "", 1), &body); err != nil {
			callback("", err)
			return
		}

		callback("downloaded: "+strings.Replace(bodyType, "video/", "", 1), nil)
		return

	}

	callback("", WebKit.ErrWebKit.WSUnexpectedResponse)
	return
}

func Send(callback func(string, error), com string, args ...string) {
	go send(callback, com, args...)
}
