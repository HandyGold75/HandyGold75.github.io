package auth

import (
	"crypto/sha1"
	"crypto/sha512"
	"encoding/hex"
	"errors"
	"fmt"
	"maps"
	"math/rand/v2"
	"os"
	"slices"
	"strings"
	"time"
	"unicode"

	"github.com/HandyGold75/GOLib/cfg"
)

type (
	AuthLevel uint8

	User struct {
		UID, Username, Password string
		AuthLevel               AuthLevel
		Roles                   []string
		Enabled                 bool
	}

	token struct {
		Hash    string
		User    User
		Expires time.Time
	}

	Config struct {
		TokenExpiresAfterDays int
	}
	Auth struct {
		cfg    Config
		tokens map[string]token
	}
)

const (
	AuthLevelGuest AuthLevel = iota
	AuthLevelUser
	AuthLevelAdmin
	AuthLevelOwner
)

var (
	Errors = struct {
		InvalidHash, InvalidToken, InvalidAuthLevel, InvalidUsername,
		UserExists, UserNotExists,
		PasswordToShort, PasswordToSimple, UsernameToShort,
		PasswordAlreadyHashed,
		AuthFailed,
		PathNotFound error
	}{
		InvalidHash: errors.New("invalid hash"), InvalidToken: errors.New("invalid token"), InvalidAuthLevel: errors.New("invalid auth level"), InvalidUsername: errors.New("invalid username"),
		UserExists: errors.New("user exists"), UserNotExists: errors.New("user not exists"),
		PasswordToShort: errors.New("password to short"), PasswordToSimple: errors.New("password to simple"), UsernameToShort: errors.New("username to short"),
		PasswordAlreadyHashed: errors.New("password is already hashed"),
		AuthFailed:            errors.New("authentication failed"),
		PathNotFound:          errors.New("path not found"),
	}

	AuthMap = map[string]AuthLevel{"guest": AuthLevelGuest, "user": AuthLevelUser, "admin": AuthLevelAdmin, "owner": AuthLevelOwner}
)

func validateHash(hash string) bool {
	if len(hash) != 128 && len(hash) != 64 && len(hash) != 40 {
		return false
	}
	_, err := hex.DecodeString(hash)
	return err == nil
}

func hashUser(user User) (User, string, error) {
	switch {
	case validateHash(user.Password):
	case len(user.Password) < 12:
		return User{}, "", Errors.PasswordToShort
	case !strings.ContainsFunc(user.Password, unicode.IsLower):
		return User{}, "", Errors.PasswordToSimple
	case !strings.ContainsFunc(user.Password, unicode.IsUpper):
		return User{}, "", Errors.PasswordToSimple
	case !strings.ContainsFunc(user.Password, unicode.IsNumber):
		return User{}, "", Errors.PasswordToSimple
	case !strings.ContainsFunc(user.Password, unicode.IsPunct):
		return User{}, "", Errors.PasswordToSimple
	default:
		hash := sha512.Sum512([]byte(user.Password))
		user.Password = hex.EncodeToString(hash[:])
	}

	pass, err := hex.DecodeString(user.Password)
	if err != nil {
		return User{}, "", err
	}
	hash := sha1.Sum(append([]byte(user.Username), pass...))
	hashStr := hex.EncodeToString(hash[:])
	if !validateHash(hashStr) {
		return User{}, "", Errors.InvalidHash
	}
	return user, hashStr, nil
}

func NewAuth(conf Config) Auth {
	toks := map[string]token{}
	_ = cfg.LoadRel("data/cache/tokens", &toks)
	return Auth{cfg: conf, tokens: toks}
}

func (a Auth) ListUsers() ([]string, error) {
	path := cfg.CheckDirRel("data/users")
	if path == "" {
		return []string{}, Errors.PathNotFound
	}
	items, err := os.ReadDir(path)
	if err != nil {
		return []string{}, err
	}
	hashes := []string{}
	for _, item := range items {
		if item.IsDir() || !validateHash(strings.TrimSuffix(item.Name(), ".json")) {
			continue
		}
		hashes = append(hashes, strings.TrimSuffix(item.Name(), ".json"))
	}
	return hashes, nil
}

func (a Auth) GetUser(hash string) (User, error) {
	if !validateHash(hash) {
		return User{}, Errors.InvalidHash
	} else if cfg.CheckRel("data/users/"+hash) == "" {
		return User{}, Errors.UserNotExists
	}

	user := User{}
	if err := cfg.LoadRel("data/users/"+hash, &user); err != nil {
		return User{}, err
	}
	return user, nil
}

func (a Auth) ListTokens() []string {
	toks := []string{}
	for tok := range a.tokens {
		toks = append(toks, tok)
	}
	return toks
}

func (a Auth) GetToken(tok string) (token, error) {
	t, ok := a.tokens[tok]
	if !ok {
		return token{}, Errors.InvalidToken
	}
	return t, nil
}

func (a Auth) CreateUser(user User) (string, error) {
	if len(user.Username) < 3 {
		return "", Errors.UsernameToShort
	} else if user.AuthLevel < AuthLevelGuest || user.AuthLevel > AuthLevelOwner {
		return "", Errors.InvalidAuthLevel
	}

	for _, name := range []string{"server", "cli", "site", "tapo", "auth", "com", "owner", "admin", "user", "guest"} {
		if strings.Contains(strings.ToLower(user.Username), name) {
			return "", Errors.InvalidUsername
		}
	}

	user, hash, err := hashUser(user)
	if err != nil {
		return "", err
	}
	if cfg.CheckRel("data/users/"+hash) != "" {
		return "", Errors.UserExists
	}

	users, err := a.ListUsers()
	if err != nil && err != Errors.PathNotFound {
		return "", err
	}
	for _, uh := range users {
		u, err := a.GetUser(uh)
		if err != nil {
			continue
		}
		if user.Username == u.Username {
			return "", Errors.UserExists
		}
	}

	user.UID = a.genUID()

	if err := cfg.DumpRel("data/users/"+hash, user); err != nil {
		return "", err
	}
	return hash, nil
}

func (a Auth) ModifyUser(hash string, newUser User) (string, error) {
	if len(newUser.Username) < 3 {
		return "", Errors.UsernameToShort
	} else if newUser.AuthLevel < AuthLevelGuest || newUser.AuthLevel > AuthLevelOwner {
		return "", Errors.InvalidAuthLevel
	}

	if !validateHash(hash) {
		return "", Errors.InvalidHash
	}
	path := cfg.CheckRel("data/users/" + hash)
	if path == "" {
		return "", Errors.UserNotExists
	}

	for _, name := range []string{"server", "cli", "site", "tapo", "auth", "com", "owner", "admin", "user", "guest"} {
		if strings.Contains(strings.ToLower(newUser.Username), name) {
			return "", Errors.InvalidUsername
		}
	}

	newUser, newHash, err := hashUser(newUser)
	if err != nil {
		return "", err
	}
	if hash != newHash && cfg.CheckRel("data/users/"+newHash) != "" {
		return "", Errors.UserExists
	}

	if err := cfg.DumpRel("data/users/"+newHash, newUser); err != nil {
		return "", err
	}
	if hash != newHash {
		a.Deauthenticate(hash)
		if err := os.Remove(path); err != nil {
			return "", err
		}
	} else {
		// a.Deauthenticate(hash) => do reauthenticate if hash is the same
	}
	return newHash, nil
}

func (a Auth) DeleteUser(hash string) error {
	if !validateHash(hash) {
		return Errors.InvalidHash
	}
	path := cfg.CheckRel("data/users/" + hash)
	if path == "" {
		return Errors.UserNotExists
	}
	a.Deauthenticate(hash)
	if err := os.Remove(path); err != nil {
		return err
	}
	return nil
}

func (a Auth) IsAuthenticated(tok string) (User, bool) {
	t, ok := a.tokens[tok]
	if !ok {
		return User{}, false
	}
	if time.Until(a.tokens[tok].Expires) < 0 {
		a.deauthenticateWhenExpired(tok)
		return User{}, false
	}
	return t.User, true
}

// userHash: base16(sha1(username+sha512(password)))
// authHash: base16(sha1(sha512(password)+time.Now().Format("2006-01-02 15:04")))
func (a Auth) Authenticate(userHash string, authHash string) (string, error) {
	user, err := a.GetUser(userHash)
	if err != nil {
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}
	if !user.Enabled {
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}

	pass, err := hex.DecodeString(user.Password)
	if err != nil {
		return "", err
	}
	authSuccess := false
	for i := range []int{0, -1, 1} {
		hash := sha1.Sum(append(pass, []byte(time.Now().Add(time.Minute*time.Duration(i-1)).Format("2006-01-02 15:04"))...))
		fmt.Print("\r\n" + authHash + " == " + hex.EncodeToString(hash[:]) + "\r\n")
		if authHash == hex.EncodeToString(hash[:]) {
			authSuccess = true
			break
		}
	}
	if !authSuccess {
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}

	tok := a.genToken()
	a.tokens[tok] = token{
		Hash:    userHash,
		User:    user,
		Expires: time.Now().Add(time.Hour * 24 * time.Duration(a.cfg.TokenExpiresAfterDays)),
	}
	_ = cfg.DumpRel("data/cache/tokens", &a.tokens)
	a.deauthenticateWhenExpired(tok)
	return tok, nil
}

func (a Auth) Reauthenticate(tok string) (User, error) {
	user, ok := a.IsAuthenticated(tok)
	if !ok {
		return User{}, Errors.AuthFailed
	}

	t := a.tokens[tok]
	t.Expires = time.Now().Add(time.Hour * 24 * time.Duration(a.cfg.TokenExpiresAfterDays))
	u, err := a.GetUser(t.Hash)
	if err != nil {
		user = u
	}
	t.User = user
	a.tokens[tok] = t
	_ = cfg.DumpRel("data/cache/tokens", &a.tokens)
	return user, nil
}

func (a Auth) Deauthenticate(hash string) {
	maps.DeleteFunc(a.tokens, func(k string, v token) bool { return v.Hash == hash })
	_ = cfg.DumpRel("data/cache/tokens", &a.tokens)
}

func (a Auth) DeauthenticateToken(tok string) {
	delete(a.tokens, tok)
	_ = cfg.DumpRel("data/cache/tokens", &a.tokens)
}

func (a Auth) deauthenticateWhenExpired(tok string) {
	t, ok := a.tokens[tok]
	if !ok {
		return
	}
	if time.Until(t.Expires) > 0 {
		time.AfterFunc(time.Until(t.Expires), func() { a.deauthenticateWhenExpired(tok) })
		return
	}
	delete(a.tokens, tok)
	_ = cfg.DumpRel("data/cache/tokens", &a.tokens)
}

func (a Auth) genToken() string {
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	for {
		tok := make([]byte, 32)
		for i := range tok {
			tok[i] = charset[rand.IntN(len(charset))]
		}
		if _, ok := a.tokens[string(tok)]; !ok {
			return string(tok)
		}
	}
}

func (a Auth) genUID() string {
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	for {
		uid := make([]byte, 32)
		for i := range uid {
			uid[i] = charset[rand.IntN(len(charset))]
		}
		users, err := a.ListUsers()
		if err != nil {
			return string(uid)
		}
		if slices.IndexFunc(users, func(user string) bool { u, _ := a.GetUser(user); return u.UID == string(uid) }) < 0 {
			return string(uid)
		}
	}
}
