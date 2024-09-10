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
	ForcePage               = func(string) {}
	SetLoginSuccessCallback = func(func()) {}
)
