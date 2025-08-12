//go:build js && wasm

package Admin

import "time"

type (
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
)

var (
	authMap         = map[string]int{"guest": 0, "user": 1, "admin": 2, "owner": 3}
	authMapReversed = map[int]string{0: "guest", 1: "user", 2: "admin", 3: "owner"}

	allRoles = []string{"CLI", "Home"}
)
