package auth

import (
	"crypto/sha512"
	"errors"
	"fmt"
	"maps"
	"math/rand/v2"
	"os"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/cfg"
)

type (
	User struct {
		Username, Password string
		AuthLevel          int
		Roles              []string
		Enabled            bool
	}

	Token struct {
		UserHash string
		UserData User
		Expires  time.Time
	}

	Auth struct{ Tokens map[string]Token }
)

var (
	AuthMap         = map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}
	AuthMapReversed = map[int]string{0: "guest", 1: "user", 2: "admin", 3: "owner"}

	Errors = struct {
		InvalidHash, InvalidAuthLevel,
		UserExists, UserNotExists,
		PasswordToShort, UsernameToShort,
		AuthFailed error
	}{
		InvalidHash:      errors.New("invalid hash"),
		InvalidAuthLevel: errors.New("invalid auth level"),
		UserExists:       errors.New("user exists"),
		UserNotExists:    errors.New("user not exists"),
		PasswordToShort:  errors.New("password to short"),
		UsernameToShort:  errors.New("username to short"),
		AuthFailed:       errors.New("authentication failed"),
	}
)

func genToken() string {
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	token := make([]byte, 128)
	for i := range token {
		token[i] = charset[rand.IntN(len(charset))]
	}
	return string(token)
}

func validateHash(hash string) bool {
	if len(hash) != 128 {
		return false
	}
	charset := "abcdef0123456789"
	for _, char := range hash {
		if !strings.ContainsRune(charset, char) {
			return false
		}
	}
	return true
}

func sha(s string) string {
	hasher := sha512.New()
	hasher.Write([]byte(s))
	return fmt.Sprintf("%x", hasher.Sum(nil))
}

func NewAuth() Auth {
	return Auth{Tokens: map[string]Token{}}
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

func (a Auth) CreateUser(user User) (string, error) {
	if len(user.Username) < 3 {
		return "", Errors.UsernameToShort
	} else if len(user.Password) < 12 {
		return "", Errors.PasswordToShort
	} else if user.AuthLevel < 0 || user.AuthLevel > 3 {
		return "", Errors.InvalidAuthLevel
	}

	hash := sha(user.Username + user.Password)
	if !validateHash(hash) {
		return "", Errors.InvalidHash
	} else if cfg.CheckRel("data/users/"+hash) != "" {
		return "", Errors.UserExists
	}

	if err := cfg.DumpRel("data/users/"+hash, user); err != nil {
		return "", err
	}
	return hash, nil
}

func (a Auth) ModifyUser(hash string, newUser User) (string, error) {
	if len(newUser.Username) < 3 {
		return "", Errors.UsernameToShort
	} else if len(newUser.Password) < 12 {
		return "", Errors.PasswordToShort
	} else if newUser.AuthLevel < 0 || newUser.AuthLevel > 3 {
		return "", Errors.InvalidAuthLevel
	}

	if !validateHash(hash) {
		return "", Errors.InvalidHash
	}
	path := cfg.CheckRel("data/users/" + hash)
	if path == "" {
		return "", Errors.UserNotExists
	}

	newHash := sha(newUser.Username + newUser.Password)
	if hash != newHash {
		if !validateHash(newHash) {
			return "", Errors.InvalidHash
		} else if cfg.CheckRel("data/users/"+newHash) != "" {
			return "", Errors.UserExists
		}
	}

	if err := cfg.DumpRel("data/users/"+newHash, newUser); err != nil {
		return "", err
	}
	if hash != newHash {
		if err := os.Remove(path); err != nil {
			return "", err
		}
	}
	return newHash, nil
}

func (a Auth) DeleleteUser(hash string) error {
	if !validateHash(hash) {
		return Errors.InvalidHash
	}
	path := cfg.CheckRel("data/users/" + hash)
	if path == "" {
		return Errors.UserNotExists
	}

	if err := os.Remove(path); err != nil {
		return err
	}
	return nil
}

func (a Auth) Authenticate(hash string, password string) (string, error) {
	user, err := a.GetUser(hash)
	if err != nil {
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}
	if !user.Enabled {
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}
	switch password {
	case sha(user.Password + time.Now().Format("2006-01-02 15:04")):
	case sha(user.Password + time.Now().Add(-time.Minute).Format("2006-01-02 15:04")):
	case sha(user.Password + time.Now().Add(time.Minute).Format("2006-01-02 15:04")):
	default:
		time.Sleep(time.Millisecond * time.Duration(rand.IntN(250)))
		return "", Errors.AuthFailed
	}

	token := genToken()
	for {
		if _, ok := a.Tokens[token]; !ok {
			break
		}
		token = genToken()
	}
	a.Tokens[token] = Token{
		UserHash: hash,
		UserData: user,
		Expires:  time.Now().Add(time.Hour * 24 * 7),
	}
	time.AfterFunc(time.Until(a.Tokens[token].Expires), func() { a.DeauthenticateToken(token) })
	return token, nil
}

func (a Auth) Deauthenticate(hash string) {
	maps.DeleteFunc(a.Tokens, func(k string, v Token) bool { return v.UserHash == hash })
}

func (a Auth) DeauthenticateToken(token string) {
	delete(a.Tokens, token)
}
