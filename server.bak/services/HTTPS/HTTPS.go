package HTTPS

import (
	"HG75/modules/Auth"
	"HG75/modules/Com"
	"context"
	"errors"
	"net/http"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"
	"unicode"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	Files struct {
		TopDir string
		SSLDir string
	}

	Cert struct {
		Cert string
		Key  string
	}

	Config struct {
		IP        string `json:"IP"`
		Port      uint16 `json:"Port"`
		Domain    string `json:"Domain"`
		SubDomain string `json:"SubDomain"`
	}
)

var (
	StopService = false
	IsRunning   = false
	OnExit      = func() {}

	recentComRequests  = map[string][]time.Time{}
	recentAuthRequests = map[string][]time.Time{}

	RootDir = func() string {
		filePath, err := os.Executable()
		if err != nil {
			panic(err)
		}
		filePathSplit := strings.Split(filePath, "/")
		return strings.Join(filePathSplit[:len(filePathSplit)-1], "/")
	}()

	files = Files{}

	lgr    = &logger.Logger{}
	config = &Config{}

	HTTPServer = &http.Server{}
)

func prepareFolders() error {
	allDirs := []string{
		files.TopDir,
		files.SSLDir,
	}

	for _, dir := range allDirs {
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			if err := os.Mkdir(dir, 0740); err != nil {
				return err
			}
		}
	}

	return nil
}

func filterTimes(timeSlice []time.Time, maxAge time.Duration) []time.Time {
	return slices.DeleteFunc(timeSlice, func(t time.Time) bool {
		return -time.Until(t) > maxAge
	})
}

func getSSLCert(dir string) (Cert, error) {
	if f, err := os.Stat(dir + "/fullchain.pem"); os.IsNotExist(err) || f.IsDir() {
		return Cert{}, errors.New(dir + "/fullchain.pem was not found or is a directory")
	}

	if f, err := os.Stat(dir + "/privkey.pem"); os.IsNotExist(err) || f.IsDir() {
		return Cert{}, errors.New(dir + "/privkey.pem was not found or is a directory")
	}

	return Cert{Cert: dir + "/fullchain.pem", Key: dir + "/privkey.pem"}, nil
}

func ProssesCom(user Auth.User, com string, args ...string) (out []byte, contentType string, errCode int, err error) {
	if Com.ServerComs[com].RequiredAuthLevel >= 2 {
		lgr.Log("high", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
	} else if Com.ServerComs[com].RequiredAuthLevel >= 1 {
		lgr.Log("medium", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
	} else {
		lgr.Log("low", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
	}

	if com == "help" {
		return []byte(Com.HelpMenu(user, args...)), "text/plain", http.StatusOK, nil
	} else if com == "autocomplete" {
		return Com.AutoComplete(user, args...), "application/json", http.StatusOK, nil
	}

	if _, ok := Com.ServerComs[com]; !ok {
		return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
	}

	srvCom := Com.ServerComs[com]
	if srvCom.RequiredAuthLevel > user.AuthLevel {
		return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
	}

	for _, role := range srvCom.RequiredRoles {
		if !slices.Contains(user.Roles, role) {
			return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
		}
	}

	return Com.ServerComs[com].Function(user, args...)
}

func sanatize(s string) string {
	s = strings.Map(func(r rune) rune {
		if unicode.IsPrint(r) {
			return r
		}
		return -1
	}, s)

	s = strings.ReplaceAll(s, lgr.RecordSepperator, "<rs>")
	s = strings.ReplaceAll(s, lgr.EORSepperator, "<es>")

	return s
}

func handleComHTTP(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Allow-Headers", "Content-Type,token")
	w.Header().Add("Access-Control-Expose-Headers", "Content-Type,x-error,retry-after")
	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

	if req.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	} else if req.Method != "POST" {
		lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "400 BadRequest: Not a POST request")
		w.Header().Set("x-error", "invalid method "+req.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	recentComRequests[req.RemoteAddr] = filterTimes(recentComRequests[req.RemoteAddr], time.Minute*time.Duration(1))
	if len(recentComRequests[req.RemoteAddr]) >= 180 {
		lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "429 TooManyRequests")
		w.Header().Set("retry-after", strconv.Itoa(60))
		w.WriteHeader(http.StatusTooManyRequests)
		return
	}
	recentComRequests[req.RemoteAddr] = append(recentComRequests[req.RemoteAddr], time.Now())

	token := req.Header.Get("token")
	if token == "" {
		lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "400 BadRequest: Missing token")
		w.Header().Set("x-error", "missing header token")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	user, err := Auth.IsAuthenticated(token)
	if err != nil {
		lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "401 Unauthorized: Failed Authentication")
		w.Header().Set("x-error", "failed auth bad token")
		w.WriteHeader(http.StatusUnauthorized)
		return
	}

	com := sanatize(req.PostFormValue("com"))
	if com == "" {
		lgr.Log("low", user.Username, "Com Request", "400 BadRequest: Missing com")
		w.Header().Set("x-error", "missing field com")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	args := strings.Split(sanatize(req.PostFormValue("args")), "%20")
	if len(args) == 1 && args[0] == "" {
		args = []string{}
	}

	out, contentType, errCode, err := ProssesCom(user, com, args...)

	if err != nil || errCode < 200 || errCode >= 300 {
		lgr.Log("debug", user.Username, "Com Request", strconv.Itoa(errCode)+": "+err.Error())
		w.Header().Set("x-error", err.Error())
		w.WriteHeader(errCode)
		return
	}

	lgr.Log("debug", user.Username, "Com Request", strconv.Itoa(errCode)+": "+sanatize(string(out)))
	if len(out) != 0 && contentType != "" {
		w.Header().Set("Content-Type", contentType)
		w.WriteHeader(errCode)
		w.Write(out)
		return
	}

	w.WriteHeader(errCode)
}

func handleAuthHTTP(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Expose-Headers", "token,x-error,retry-after")
	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

	if req.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	} else if req.Method != "POST" {
		lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Not a POST request")
		w.Header().Set("x-error", req.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	recentAuthRequests[req.RemoteAddr] = filterTimes(recentAuthRequests[req.RemoteAddr], time.Minute*time.Duration(10))
	if len(recentAuthRequests[req.RemoteAddr]) >= 10 {
		lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "429 TooManyRequests")
		w.Header().Set("retry-after", strconv.Itoa(60*10))
		w.WriteHeader(http.StatusTooManyRequests)
		return
	}
	recentAuthRequests[req.RemoteAddr] = append(recentAuthRequests[req.RemoteAddr], time.Now())

	tokenCheck := req.PostFormValue("token")
	if tokenCheck != "" {
		user, err := Auth.IsAuthenticated(tokenCheck)
		if err != nil {
			lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusUnauthorized)+": Token check failed for"+tokenCheck)
			w.WriteHeader(http.StatusUnauthorized)
			return
		}

		lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusOK)+": Token check succeeded for "+user.Username)
		w.WriteHeader(http.StatusOK)
	}

	usrHash := req.PostFormValue("usrHash")
	if usrHash == "" {
		lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Missing usrHash")
		w.Header().Set("x-error", "missing field usrHash")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	pswHash := req.PostFormValue("pswHash")
	if pswHash == "" {
		lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Missing pswHash")
		w.Header().Set("x-error", "missing field pswHash")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	token, err := Auth.Authenticate(usrHash, pswHash)
	if err != nil {
		lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "401 Unauthorized: Failed Authentication")
		w.Header().Set("x-error", "failed auth bad credentials")
		w.WriteHeader(http.StatusUnauthorized)
		return
	}

	user, err := Auth.IsAuthenticated(token)
	if err != nil {
		lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusInternalServerError)+": Failed Resloving Token")
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	lgr.Log("high", user.Username, "Auth Request", strconv.Itoa(http.StatusOK)+": Authenticated "+user.Username)
	w.Header().Set("token", token)
	w.WriteHeader(http.StatusOK)
}

func Debug() map[string]map[string][]time.Time {
	return map[string]map[string][]time.Time{"recentAuthRequests": recentAuthRequests, "recentComRequests": recentComRequests}
}

func loop(out chan string) error {
	doSSL := true
	cert, err := getSSLCert(files.SSLDir)
	if err != nil {
		cert, err = getSSLCert("/etc/letsencrypt/live/" + strings.ToLower(config.SubDomain) + "." + strings.ToLower(config.Domain))
		if err != nil {
			doSSL = false
			lgr.Log("error", "HTTPS", "Missing SSL Certificates", "Valid locations: \""+files.SSLDir+"\", \""+"/etc/letsencrypt/live/"+strings.ToLower(config.SubDomain)+"."+strings.ToLower(config.Domain)+"\"")
			lgr.Log("warning", "HTTPS", "Downgrading", "Falling back to http!")
		}
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/com", handleComHTTP)
	mux.HandleFunc("/auth", handleAuthHTTP)
	HTTPServer = &http.Server{Addr: config.IP + ":" + strconv.Itoa(int(config.Port)), Handler: mux}

	errCh := make(chan error)
	go func() {
		defer OnExit()

		if doSSL {
			lgr.Log("info", "HTTPS", "Listening", "https://"+config.IP+":"+strconv.Itoa(int(config.Port)))
			errCh <- HTTPServer.ListenAndServeTLS(cert.Cert, cert.Key)
		} else {
			lgr.Log("info", "HTTPS", "Listening", "http://"+config.IP+":"+strconv.Itoa(int(config.Port)))
			errCh <- HTTPServer.ListenAndServe()
		}

		close(errCh)
	}()

	for !StopService {
		select {
		case line := <-Com.OutCh:
			if line == "" {
				continue
			}
			out <- line

		case err := <-errCh:
			return err

		case <-time.After(time.Second * time.Duration(1)):
			lgr.Log("debug", "HTTPS", "Checking", "Stop request")
		}
	}

	return nil
}

func Stop() {
	lgr.Log("info", "HTTPS", "Stopping", "")
	StopService = true

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*time.Duration(10))
	defer cancel()
	if err := HTTPServer.Shutdown(ctx); err != nil {
		lgr.Log("error", "HTTPS", "Stopping", err)
	}

	for range 3 {
		if !IsRunning {
			break
		}
		time.Sleep(time.Second * time.Duration(1))
	}

	lgr.Log("debug", "HTTPS", "Stopped", "")
}

// meta expects minimally: map[string]any{"TopDir": string, "SSLDir": string, "config": *Config}
func Start(mainChOut chan string, mainChErr chan error, onExit func(), log *logger.Logger, meta map[string]any) {
	OnExit = onExit
	defer OnExit()

	log.Log("info", "HTTPS", "Starting", "")

	IsRunning = true
	StopService = false

	lgr = log

	topDir, ok := meta["TopDir"].(string)
	if !ok {
		mainChErr <- errors.New("missing TopDir meta")
		StopService = true
	}
	sslDir, ok := meta["SSLDir"].(string)
	if !ok {
		mainChErr <- errors.New("missing SSLDir meta")
		StopService = true
	}
	files = Files{
		TopDir: topDir,
		SSLDir: sslDir,
	}

	cfg, ok := meta["config"].(*Config)
	if !ok {
		mainChErr <- errors.New("missing config meta")
		StopService = true
	}
	config = cfg

	err := prepareFolders()
	if err != nil {
		mainChErr <- errors.New("unable to prepare folders")
		StopService = true
	}

	lgr.Log("debug", "HTTPS", "Started", "")
	for !StopService {
		err := loop(mainChOut)
		if err == http.ErrServerClosed && StopService {
			break
		}
		if err != nil {
			mainChErr <- err
			break
		}
	}

	IsRunning = false
	lgr.Log("debug", "HTTPS", "Exited", "")
}
