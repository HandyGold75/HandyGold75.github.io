package srvs

import (
	"HG75/auth"
	"HG75/coms"
	"context"
	"encoding/base64"
	"fmt"
	"net/http"
	"os"
	"slices"
	"strconv"
	"strings"
	"time"
	"unicode"

	"github.com/HandyGold75/GOLib/cfg"
	"github.com/HandyGold75/GOLib/gapo"
	"github.com/HandyGold75/GOLib/logger"
	"github.com/HandyGold75/Gonos"
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
		tapoCfg                       TapoConfig
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

func NewSite(conf SiteConfig, tapoConf TapoConfig, confAuth auth.Config) *Site {
	lgr, _ := logger.NewRel("data/logs/site")
	path := cfg.CheckDirRel("")
	if path == "" {
		path = "./"
	}
	cert, key, err := getSSLCert(path + "ssl")
	if err != nil {
		cert, key, err = getSSLCert("/etc/letsencrypt/live/" + strings.ToLower(conf.SubDomain) + "." + strings.ToLower(conf.Domain))
		if err != nil {
			lgr.Log("error", "site", "missing", "certificates not found in: \""+path+"ssl\", \""+"/etc/letsencrypt/live/"+strings.ToLower(conf.SubDomain)+"."+strings.ToLower(conf.Domain)+"\"")
		}
	}

	zonePlayer := &Gonos.ZonePlayer{}
	if conf.SonosIP != "" {
		if zp, err := Gonos.NewZonePlayer(conf.SonosIP); err == nil {
			zonePlayer = zp
			lgr.Log("low", "site", "connected", "sonos speaker: "+zonePlayer.URL)
		} else if zps, err := Gonos.DiscoverZonePlayer(1); err == nil {
			zonePlayer = zps[0]
			lgr.Log("low", "site", "connected", "sonos speaker: "+zonePlayer.URL)
		} else if zps, err := Gonos.ScanZonePlayer(conf.SonosIP, 1); err == nil {
			zonePlayer = zps[0]
			lgr.Log("low", "site", "connected", "sonos speaker: "+zonePlayer.URL)
		} else {
			lgr.Log("error", "site", "failed", "connecting to sonos speaker: "+conf.SonosIP)
		}
	}
	tapoPlugs := map[string]*gapo.Tapo{}
	for _, ip := range tapoConf.PlugIPS {
		var e error
		for i := range 11 {
			if i == 10 {
				lgr.Log("error", "site", "failed", "connecting to tapo plug: "+ip+"; error: "+e.Error())
				break
			}
			tc, err := gapo.NewTapoHash(ip, tapoConf.AuthHash)
			if err != nil {
				e = err
				continue
			}
			tcInfo, err := tc.GetDeviceInfo()
			if err != nil {
				e = err
				continue
			}
			nickname, err := base64.StdEncoding.DecodeString(tcInfo.Nickname)
			if err != nil {
				e = err
				continue
			}
			tapoPlugs[string(nickname[:])] = tc
			lgr.Log("low", "site", "connected", "tapo plug: "+ip)
			break
		}
	}

	s := &Site{
		cfg: conf, tapoCfg: tapoConf, Pipe: make(chan string), lgr: lgr,
		cert: cert, key: key,
		server:        http.Server{},
		recentReqsCom: []reqStamp{}, recentReqsAuth: []reqStamp{},
		auth: auth.NewAuth(confAuth),
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/com", s.handleComHTTP)
	mux.HandleFunc("/auth", s.handleAuthHTTP)
	s.server = http.Server{Addr: conf.IP + ":" + strconv.Itoa(int(conf.Port)), Handler: mux}

	coms.Hook(&s.auth, s.Pipe, zonePlayer, &tapoPlugs)
	return s
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
	s.lgr.Log("low", "site", "started")
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

	for name, db := range coms.OpenDataBases {
		s.lgr.Log("debug", "site", "dumping", name)
		for _, err := range db.Dump() {
			s.lgr.Log("error", "site", name, err)
		}
		s.lgr.Log("low", "site", "dumped", name)
		delete(coms.OpenDataBases, name)
	}

	coms.Unhook()

	s.lgr.Log("low", "site", "stopped")
}

func (s *Site) loop() {
	for !s.exit {
		if s.cert == "" || s.key == "" {
			s.lgr.Log("warning", "site", "downgrading", "falling back to http")
			s.lgr.Log("medium", "site", "listening", "http://"+s.cfg.IP+":"+strconv.Itoa(int(s.cfg.Port)))
			if err := s.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
				s.lgr.Log("error", "site", "failed", err)
				break
			}
		} else {
			s.lgr.Log("medium", "site", "listening", "https://"+s.cfg.IP+":"+strconv.Itoa(int(s.cfg.Port)))
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

func (s *Site) ProssesCommand(user auth.User, inp ...string) (out []byte, contentType string, errCode int, err error) {
	if len(inp) < 1 {
		return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
	}
	command, ok := coms.AllCommands[inp[0]]
	if !ok {
		return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
	}
	args := inp[1:]
	if command.AuthLevel > user.AuthLevel {
		return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
	} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
		return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
	}

	for i, p := range inp[1:] {
		com, ok := command.Commands[p]
		if !ok {
			break
		}
		command, args = com, inp[i+2:]
		if command.AuthLevel > user.AuthLevel {
			return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
		} else if slices.ContainsFunc(command.Roles, func(r string) bool { return !slices.Contains(user.Roles, r) }) {
			return []byte{}, "", http.StatusNotFound, coms.Errors.CommandNotFound
		}
	}

	if len(command.Commands) > 0 || len(args) < command.ArgsLen[0] {
		return []byte{}, "", http.StatusBadRequest, Errors.MissingArgs
	} else if len(args) > command.ArgsLen[1] {
		fmt.Println(args)
		return []byte{}, "", http.StatusBadRequest, Errors.AdditionalArgs
	}

	if command.AuthLevel < auth.AuthLevelUser {
		s.lgr.Log("low", user.Username, "Executing", strings.Join(inp, " "))
	} else if command.AuthLevel == auth.AuthLevelUser {
		s.lgr.Log("medium", user.Username, "Executing", strings.Join(inp, " "))
	} else {
		s.lgr.Log("high", user.Username, "Executing", strings.Join(inp, " "))
	}

	return command.Exec(user, args...)
}

func (s *Site) handleComHTTP(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Allow-Headers", "Content-Type,token")
	w.Header().Add("Access-Control-Expose-Headers", "Content-Type,x-error,retry-after")
	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

	if req.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	} else if req.Method != "POST" {
		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "ComReq", "400: Not a POST request")
		w.Header().Set("x-error", "invalid method "+req.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	s.recentReqsCom = slices.DeleteFunc(s.recentReqsCom, func(rs reqStamp) bool {
		return -time.Until(rs.date) > time.Minute*time.Duration(s.cfg.RequestsLimitTimoutCom)
	})
	c := 0
	for _, stamp := range s.recentReqsCom {
		if stamp.addr == req.RemoteAddr {
			c += 1
		}
		if c >= s.cfg.RequestsLimitCom {
			s.lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "ComReq", "429: Too many requests")
			w.Header().Set("retry-after", strconv.Itoa(60))
			w.WriteHeader(http.StatusTooManyRequests)
			return
		}
	}
	s.recentReqsCom = append(s.recentReqsCom, reqStamp{addr: req.RemoteAddr, date: time.Now()})

	tok := req.Header.Get("token")
	if tok == "" {
		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "ComReq", "400: Missing token")
		w.Header().Set("x-error", "missing header token")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	user, ok := s.auth.IsAuthenticated(tok)
	if !ok {
		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "ComReq", "401: Failed Authentication")
		w.Header().Set("x-error", "failed auth bad token")
		w.WriteHeader(http.StatusUnauthorized)
		return
	}

	inp := strings.Split(s.sanatize(req.PostFormValue("com")), "%20")
	if len(inp) <= 1 && inp[0] == "" {
		s.lgr.Log("low", user.Username, "ComReq", "400: Missing com")
		w.Header().Set("x-error", "missing field com")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	out, contentType, errCode, err := s.ProssesCommand(user, inp...)
	if err != nil || errCode < 200 || errCode >= 300 {
		s.lgr.Log("debug", user.Username, "ComReq", strconv.Itoa(errCode)+": "+err.Error())
		w.Header().Set("x-error", err.Error())
		w.WriteHeader(errCode)
		return
	}

	s.lgr.Log("debug", user.Username, "ComReq", strconv.Itoa(errCode)+": "+string(out))
	if len(out) != 0 && contentType != "" {
		w.Header().Set("Content-Type", contentType)
		w.WriteHeader(errCode)
		_, _ = w.Write(out)
		return
	}
	w.WriteHeader(errCode)
}

func (s *Site) handleAuthHTTP(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Expose-Headers", "x-error,retry-after")
	w.Header().Set("Access-Control-Allow-Methods", "OPTIONS,POST")

	if req.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	} else if req.Method != "POST" {
		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "400: Not a POST request")
		w.Header().Set("x-error", req.Method)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	s.recentReqsAuth = slices.DeleteFunc(s.recentReqsAuth, func(rs reqStamp) bool {
		return -time.Until(rs.date) > time.Minute*time.Duration(s.cfg.RequestsLimitTimoutAuth)
	})
	c := 0
	for _, stamp := range s.recentReqsAuth {
		if stamp.addr == req.RemoteAddr {
			c += 1
		}
		if c >= s.cfg.RequestsLimitAuth {
			s.lgr.Log("medium", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "429: Too many requests")
			w.Header().Set("retry-after", strconv.Itoa(60*10))
			w.WriteHeader(http.StatusTooManyRequests)
			return
		}
	}
	s.recentReqsAuth = append(s.recentReqsAuth, reqStamp{addr: req.RemoteAddr, date: time.Now()})

	tokCheck := s.sanatize(req.PostFormValue("token"))
	if tokCheck != "" {
		user, err := s.auth.Reauthenticate(tokCheck)
		if err != nil {
			s.lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "401: Token check failed for "+tokCheck)
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "200: Token check succeeded for "+user.Username)
		w.Header().Set("Content-Type", coms.TypeTXT)
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(tokCheck))
		return
	}

	userHash := s.sanatize(req.PostFormValue("userHash"))
	if userHash == "" {
		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "400: Missing userHash")
		w.Header().Set("x-error", "missing field userHash")
		w.WriteHeader(http.StatusBadRequest)
		return
	}
	authHash := s.sanatize(req.PostFormValue("authHash"))
	if authHash == "" {
		s.lgr.Log("low", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "400: Missing authHash")
		w.Header().Set("x-error", "missing field authHash")
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	tok, err := s.auth.Authenticate(userHash, authHash)
	if err != nil {
		s.lgr.Log("high", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "401: Failed Authentication")
		w.Header().Set("x-error", "failed auth bad credentials")
		w.WriteHeader(http.StatusUnauthorized)
		return
	}
	user, ok := s.auth.IsAuthenticated(tok)
	if !ok {
		s.lgr.Log("error", strings.Split(req.RemoteAddr, ":")[0], "AuthReq", "500: Failed Resloving Token")
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	s.lgr.Log("high", user.Username, "AuthReq", "200: Authenticated "+user.Username)
	w.Header().Set("Content-Type", coms.TypeTXT)
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(tok))
}
