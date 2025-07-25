package srvs

import (
	"HG75/auth"
	"context"
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
	reqStamp struct {
		addr string
		date time.Time
	}

	SiteConfig struct {
		IP                                         string
		Port                                       uint16
		SubDomain, Domain                          string
		SonosIP                                    string
		RequestsLimitCom, RequestsLimitTimoutCom   int
		RequestsLimitAuth, RequestsLimitTimoutAuth int
	}

	Site struct {
		lgr                           *logger.Logger
		Pipe                          chan string
		cfg                           SiteConfig
		exit                          bool
		cert, key                     string
		server                        http.Server
		recentReqsCom, recentReqsAuth []reqStamp
		auth                          auth.Auth
	}
)

func getSSLCert(dir string) (string, string, error) {
	if f, err := os.Stat(dir + "/fullchain.pem"); os.IsNotExist(err) || f.IsDir() {
		return "", "", Errors.FullchainNotFound
	}
	if f, err := os.Stat(dir + "/privkey.pem"); os.IsNotExist(err) || f.IsDir() {
		return "", "", Errors.PrivkeyNotFound
	}
	return dir + "/fullchain.pem", dir + "/privkey.pem", nil
}

func NewSite(conf SiteConfig) *Site {
	lgr, _ := logger.NewRel("data/logs/site")

	path, err := os.Executable()
	if err != nil {
		path = "./"
	}
	pathSplit := strings.Split(strings.ReplaceAll(path, "\\", "/"), "/")
	path = strings.Join(pathSplit[:len(pathSplit)-1], "/") + "/data/ssl"
	cert, key, err := getSSLCert(path)
	if err != nil {
		cert, key, err = getSSLCert("/etc/letsencrypt/live/" + strings.ToLower(conf.SubDomain) + "." + strings.ToLower(conf.Domain))
		if err != nil {
			lgr.Log("error", "site", "missing", "certificates not found in: \""+path+"\", \""+"/etc/letsencrypt/live/"+strings.ToLower(conf.SubDomain)+"."+strings.ToLower(conf.Domain)+"\"")
		}
	}

	mux := http.NewServeMux()
	// mux.HandleFunc("/com", handleComHTTP)
	// mux.HandleFunc("/auth", handleAuthHTTP)

	return &Site{
		cfg: conf, Pipe: make(chan string), lgr: lgr,
		cert: cert, key: key,
		server:        http.Server{Addr: conf.IP + ":" + strconv.Itoa(int(conf.Port)), Handler: mux},
		recentReqsCom: []reqStamp{}, recentReqsAuth: []reqStamp{},
	}
}

func (s *Site) Run() {
	s.lgr.Log("debug", "site", "starting")
	go func() {
		defer func() {
			if rec := recover(); rec != nil {
				s.lgr.Log("error", "site", "panic", rec)
			}
			s.exit = true
			close(s.Pipe)
		}()
		s.loop()
	}()
	s.lgr.Log("medium", "site", "started")
}

func (s *Site) Stop() {
	s.lgr.Log("debug", "site", "stopping")
	s.exit = true

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*10)
	defer cancel()
	if err := s.server.Shutdown(ctx); err != nil {
		s.lgr.Log("error", "site", "Stopping", err)
	}

	for range s.Pipe {
	}
	s.lgr.Log("medium", "site", "stopped")
}

func (s *Site) loop() {
	for !s.exit {
		if s.cert == "" || s.key == "" {
			s.lgr.Log("warning", "site", "downgrading", "falling back to http")
			s.lgr.Log("medium", "site", "listening", "https://"+s.cfg.IP+":"+strconv.Itoa(int(s.cfg.Port)))
			if err := s.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
				s.lgr.Log("error", "site", "failed", err)
				break
			}
		} else {
			s.lgr.Log("medium", "site", "listening", "http://"+s.cfg.IP+":"+strconv.Itoa(int(s.cfg.Port)))
			if err := s.server.ListenAndServeTLS(s.cert, s.key); err != nil && err != http.ErrServerClosed {
				s.lgr.Log("error", "site", "failed", err)
				break
			}
		}
	}
}

func (s *Site) sanatize(v string) string {
	v = strings.Map(func(r rune) rune {
		if unicode.IsPrint(r) {
			return r
		}
		return -1
	}, v)
	v = strings.ReplaceAll(v, s.lgr.RecordSepperator, "<rs>")
	v = strings.ReplaceAll(v, s.lgr.EORSepperator, "<es>")
	return v
}

func (s *Site) checkReqsCom(addr string) bool {
	s.recentReqsCom = slices.DeleteFunc(s.recentReqsCom, func(rs reqStamp) bool {
		return -time.Until(rs.date) > time.Minute*time.Duration(s.cfg.RequestsLimitTimoutCom)
	})
	c := 0
	for _, stamp := range s.recentReqsCom {
		if stamp.addr == addr {
			c += 1
		}
		if c >= s.cfg.RequestsLimitCom {
			return false
		}
	}
	return true
}

func (s *Site) checkReqsAuth(addr string) bool {
	s.recentReqsAuth = slices.DeleteFunc(s.recentReqsAuth, func(rs reqStamp) bool {
		return -time.Until(rs.date) > time.Minute*time.Duration(s.cfg.RequestsLimitTimoutAuth)
	})
	c := 0
	for _, stamp := range s.recentReqsAuth {
		if stamp.addr == addr {
			c += 1
		}
		if c >= s.cfg.RequestsLimitAuth {
			return false
		}
	}
	return true
}

// func (s *Site) prossesCom(user Auth.User, com string, args ...string) (out []byte, contentType string, errCode int, err error) {
// 	if Com.ServerComs[com].RequiredAuthLevel >= 2 {
// 		lgr.Log("high", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
// 	} else if Com.ServerComs[com].RequiredAuthLevel >= 1 {
// 		lgr.Log("medium", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
// 	} else {
// 		lgr.Log("low", user.Username, "Executing", com+" ["+strings.Join(args, ", ")+"]")
// 	}

// 	if com == "help" {
// 		return []byte(Com.HelpMenu(user, args...)), "text/plain", http.StatusOK, nil
// 	} else if com == "autocomplete" {
// 		return Com.AutoComplete(user, args...), "application/json", http.StatusOK, nil
// 	}

// 	if _, ok := Com.ServerComs[com]; !ok {
// 		return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
// 	}

// 	srvCom := Com.ServerComs[com]
// 	if srvCom.RequiredAuthLevel > user.AuthLevel {
// 		return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
// 	}

// 	for _, role := range srvCom.RequiredRoles {
// 		if !slices.Contains(user.Roles, role) {
// 			return []byte{}, "", http.StatusNotFound, errors.New("unknown command: " + com)
// 		}
// 	}

// 	return Com.ServerComs[com].Function(user, args...)
// }

// func (s *Site) handleComHTTP(w http.ResponseWriter, req *http.Request) {
// 	w.Header().Set("Access-Control-Allow-Origin", "*")
// 	w.Header().Add("Access-Control-Allow-Headers", "Content-Type,token")
// 	w.Header().Add("Access-Control-Expose-Headers", "Content-Type,x-error,retry-after")
// 	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

// 	if req.Method == "OPTIONS" {
// 		w.WriteHeader(http.StatusOK)
// 		return
// 	} else if req.Method != "POST" {
// 		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "400 BadRequest: Not a POST request")
// 		w.Header().Set("x-error", "invalid method "+req.Method)
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	recentComRequests[req.RemoteAddr] = filterTimes(recentComRequests[req.RemoteAddr], time.Minute*time.Duration(1))
// 	if len(recentComRequests[req.RemoteAddr]) >= 180 {
// 		s.lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "429 TooManyRequests")
// 		w.Header().Set("retry-after", strconv.Itoa(60))
// 		w.WriteHeader(http.StatusTooManyRequests)
// 		return
// 	}
// 	recentComRequests[req.RemoteAddr] = append(recentComRequests[req.RemoteAddr], time.Now())

// 	token := req.Header.Get("token")
// 	if token == "" {
// 		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "400 BadRequest: Missing token")
// 		w.Header().Set("x-error", "missing header token")
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	user, err := Auth.IsAuthenticated(token)
// 	if err != nil {
// 		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Com Request", "401 Unauthorized: Failed Authentication")
// 		w.Header().Set("x-error", "failed auth bad token")
// 		w.WriteHeader(http.StatusUnauthorized)
// 		return
// 	}

// 	com := sanatize(req.PostFormValue("com"))
// 	if com == "" {
// 		s.lgr.Log("low", user.Username, "Com Request", "400 BadRequest: Missing com")
// 		w.Header().Set("x-error", "missing field com")
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	args := strings.Split(sanatize(req.PostFormValue("args")), "%20")
// 	if len(args) == 1 && args[0] == "" {
// 		args = []string{}
// 	}

// 	out, contentType, errCode, err := ProssesCom(user, com, args...)

// 	if err != nil || errCode < 200 || errCode >= 300 {
// 		s.lgr.Log("debug", user.Username, "Com Request", strconv.Itoa(errCode)+": "+err.Error())
// 		w.Header().Set("x-error", err.Error())
// 		w.WriteHeader(errCode)
// 		return
// 	}

// 	s.lgr.Log("debug", user.Username, "Com Request", strconv.Itoa(errCode)+": "+sanatize(string(out)))
// 	if len(out) != 0 && contentType != "" {
// 		w.Header().Set("Content-Type", contentType)
// 		w.WriteHeader(errCode)
// 		w.Write(out)
// 		return
// 	}

// 	w.WriteHeader(errCode)
// }

// func (s *Site) handleAuthHTTP(w http.ResponseWriter, req *http.Request) {
// 	w.Header().Set("Access-Control-Allow-Origin", "*")
// 	w.Header().Add("Access-Control-Expose-Headers", "token,x-error,retry-after")
// 	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

// 	if req.Method == "OPTIONS" {
// 		w.WriteHeader(http.StatusOK)
// 		return
// 	} else if req.Method != "POST" {
// 		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Not a POST request")
// 		w.Header().Set("x-error", req.Method)
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	recentAuthRequests[req.RemoteAddr] = filterTimes(recentAuthRequests[req.RemoteAddr], time.Minute*time.Duration(10))
// 	if len(recentAuthRequests[req.RemoteAddr]) >= 10 {
// 		s.lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "429 TooManyRequests")
// 		w.Header().Set("retry-after", strconv.Itoa(60*10))
// 		w.WriteHeader(http.StatusTooManyRequests)
// 		return
// 	}
// 	recentAuthRequests[req.RemoteAddr] = append(recentAuthRequests[req.RemoteAddr], time.Now())

// 	tokenCheck := req.PostFormValue("token")
// 	if tokenCheck != "" {
// 		user, err := Auth.IsAuthenticated(tokenCheck)
// 		if err != nil {
// 			s.lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusUnauthorized)+": Token check failed for"+tokenCheck)
// 			w.WriteHeader(http.StatusUnauthorized)
// 			return
// 		}

// 		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusOK)+": Token check succeeded for "+user.Username)
// 		w.WriteHeader(http.StatusOK)
// 	}

// 	usrHash := req.PostFormValue("usrHash")
// 	if usrHash == "" {
// 		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Missing usrHash")
// 		w.Header().Set("x-error", "missing field usrHash")
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	pswHash := req.PostFormValue("pswHash")
// 	if pswHash == "" {
// 		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "400 BadRequest: Missing pswHash")
// 		w.Header().Set("x-error", "missing field pswHash")
// 		w.WriteHeader(http.StatusBadRequest)
// 		return
// 	}

// 	token, err := Auth.Authenticate(usrHash, pswHash)
// 	if err != nil {
// 		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", "401 Unauthorized: Failed Authentication")
// 		w.Header().Set("x-error", "failed auth bad credentials")
// 		w.WriteHeader(http.StatusUnauthorized)
// 		return
// 	}

// 	user, err := Auth.IsAuthenticated(token)
// 	if err != nil {
// 		s.lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "Auth Request", strconv.Itoa(http.StatusInternalServerError)+": Failed Resloving Token")
// 		w.WriteHeader(http.StatusInternalServerError)
// 		return
// 	}

// 	lgr.Log("high", user.Username, "Auth Request", strconv.Itoa(http.StatusOK)+": Authenticated "+user.Username)
// 	w.Header().Set("token", token)
// 	w.WriteHeader(http.StatusOK)
// }
