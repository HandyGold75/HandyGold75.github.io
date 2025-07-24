package coms

type Command struct {
	AuthLevel int
	Roles     []string
	Exec      func()
}
