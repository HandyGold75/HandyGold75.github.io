package Auth

import (
	"crypto/sha1"
	"crypto/sha512"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"os"
	"time"

	"github.com/HandyGold75/GOLib/logger"
)

type (
	Files struct {
		UserDir string
	}

	User struct {
		Username, Password string
		AuthLevel          int
		Roles              []string
		Enabled            bool
	}

	AuthToken struct {
		UserHash string
		UserData User
		Expires  time.Time
	}

	AuthTokens map[string]AuthToken
)

var (
	authTokens = AuthTokens{}

	AuthMap         = map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}
	AuthMapReversed = map[int]string{0: "guest", 1: "user", 2: "admin", 3: "owner"}

	files = Files{}
	lgr   = &logger.Logger{}
)

func readFile(filePath string) ([]byte, error) {
	file, err := os.Open(filePath)
	if err != nil {
		file, err = os.Create(filePath)
		if err != nil {
			return []byte{}, err
		}
		defer file.Close()

		_, err = file.WriteString("{}")
		if err != nil {
			return []byte{}, err
		}
	} else {
		defer file.Close()
	}

	bytes, err := io.ReadAll(file)
	if err != nil {
		return []byte{}, err
	}

	return bytes, nil
}

func genToken() string {
	charset := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

	token := make([]byte, 128)
	for i := range token {
		token[i] = charset[rand.Intn(len(charset))]
	}

	return string(token)
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

func ListHashes() ([]string, error) {
	if _, err := os.Stat(files.UserDir); os.IsNotExist(err) {
		return []string{}, err
	}

	items, err := os.ReadDir(files.UserDir)
	if err != nil {
		return []string{}, err
	}

	hashes := []string{}
	for _, item := range items {
		if item.IsDir() {
			continue
		}
		hashes = append(hashes, item.Name())
	}

	return hashes, nil
}

func GetUser(userHash string) (User, error) {
	if _, err := os.Stat(files.UserDir + "/" + userHash); os.IsNotExist(err) {
		return User{}, err
	}

	user := User{}

	bytes, err := readFile(files.UserDir + "/" + userHash)
	if err != nil {
		return User{}, err
	}

	err = json.Unmarshal(bytes, &user)
	if err != nil {
		return User{}, err
	}

	return user, nil
}

func CreateUser(user User) (string, error) {
	if len(user.Username) < 3 {
		return "", errors.New("username to short")
	} else if user.AuthLevel < 0 || user.AuthLevel > 3 {
		return "", errors.New("invalid authlevel")
	}

	userHash := Sha1(user.Username + user.Password)
	if _, err := os.Stat(files.UserDir + "/" + userHash); !os.IsNotExist(err) {
		return "", os.ErrExist
	}

	configJson, err := json.MarshalIndent(&user, "", "\t")
	if err != nil {
		return "", err
	}

	err = os.WriteFile(files.UserDir+"/"+userHash, configJson, os.ModePerm)
	if err != nil {
		return "", err
	}

	return userHash, nil
}

func ModifyUser(userHash string, newUserData User) (string, error) {
	if _, err := os.Stat(files.UserDir + "/" + userHash); os.IsNotExist(err) {
		return "", err
	}

	newUserHash := Sha1(newUserData.Username + newUserData.Password)
	if _, err := os.Stat(files.UserDir + "/" + newUserHash); !os.IsNotExist(err) && userHash != newUserHash {
		return "", os.ErrExist
	}

	configJson, err := json.MarshalIndent(&newUserData, "", "\t")
	if err != nil {
		return "", err
	}

	err = os.WriteFile(files.UserDir+"/"+newUserHash, configJson, os.ModePerm)
	if err != nil {
		return "", err
	}

	if userHash != newUserHash {
		if err := os.Remove(files.UserDir + "/" + userHash); err != nil {
			return "", err
		}

		for authToken := range GetAuthTokens(userHash) {
			Deautherize(authToken)
		}

	} else if !newUserData.Enabled {
		for authToken := range GetAuthTokens(userHash) {
			Deautherize(authToken)
		}
	}

	return newUserHash, nil
}

func DelUser(userHash string) error {
	if _, err := os.Stat(files.UserDir + "/" + userHash); os.IsNotExist(err) {
		return err
	}

	if err := os.Remove(files.UserDir + "/" + userHash); err != nil {
		return err
	}

	for authToken := range GetAuthTokens(userHash) {
		Deautherize(authToken)
	}

	return nil
}

func IsAuthenticated(token string) (User, error) {
	if _, ok := authTokens[token]; !ok {
		return User{}, errors.New("token not found")
	}

	if time.Until(authTokens[token].Expires) < 0 {
		Deautherize(token)
		return User{}, errors.New("token expired")
	}

	return authTokens[token].UserData, nil
}

func Authenticate(userHash string, passwordHash string) (string, error) {
	userData, err := GetUser(userHash)
	if err != nil {
		time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))
		return "", errors.New("failed authentication")
	}

	if !userData.Enabled {
		time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))
		return "", errors.New("failed authentication")
	}

	if Sha512(userData.Password+time.Now().Format(time.DateTime)) != passwordHash {
		time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))
		return "", errors.New("failed authentication")
	}

	token := genToken()
	for {
		if _, ok := authTokens[token]; !ok {
			break
		}
		token = genToken()
	}

	authTokens[token] = AuthToken{
		UserHash: userHash,
		UserData: userData,
		Expires:  time.Now().Add(time.Hour * time.Duration(168)),
	}

	time.AfterFunc(time.Until(authTokens[token].Expires), func() { Deautherize(token) })

	return token, nil
}

func Deautherize(token string) {
	delete(authTokens, token)
}

func GetAuthTokens(userHash string) map[string]AuthToken {
	tokens := map[string]AuthToken{}
	for authToken, authTokenData := range authTokens {
		if authTokenData.UserHash == userHash {
			tokens[authToken] = authTokenData
		}
	}

	return tokens
}

func Debug() AuthTokens {
	return authTokens
}

func Close() {
	lgr.Log("debug", "Auth", "Closing", "")
	lgr.Log("debug", "Auth", "Closed", "")
}

func Init(f Files, log *logger.Logger) {
	log.Log("debug", "Auth", "Initializing", "")

	files = f
	lgr = log

	lgr.Log("debug", "Auth", "Initialized", "")
}
