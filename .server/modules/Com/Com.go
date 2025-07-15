package Com

import (
	"HG75/modules/Auth"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"maps"
	"slices"
	"strings"
	"time"

	"github.com/HandyGold75/GOLib/logger"
	"github.com/HandyGold75/Gonos"
	"github.com/achetronic/tapogo/pkg/tapogo"
)

type (
	Files struct {
		LogDir  string
		DBDir   string
		TapoDir string
	}

	Command struct {
		RequiredAuthLevel   int
		RequiredRoles       []string
		Description         string
		DetailedDescription string
		ExampleDescription  string
		AutoComplete        []string
		ArgsLen             [2]int
		Function            func(Auth.User, ...string) (out []byte, typ string, errCode int, err error)
	}

	Commands map[string]Command

	Config struct {
		SonosIP      string
		TapoPlugIPS  []string
		TapoUsername string
		TapoPassword string
	}
)

var (
	OutCh = make(chan string)

	ServerComs = func() Commands {
		coms := Commands{}
		maps.Copy(coms, YTDLComs)
		maps.Copy(coms, TapoComs)
		maps.Copy(coms, SonosComs)
		maps.Copy(coms, DateBasesComs)
		maps.Copy(coms, AdminComs)

		return coms
	}()

	files       = Files{}
	lgr         = &logger.Logger{}
	config      = Config{}
	zp          = &Gonos.ZonePlayer{}
	TapoClients = map[string]*tapogo.Tapo{}
)

func HelpMenu(user Auth.User, args ...string) string {
	msgReturn := ""
	if len(args) == 1 {
		if _, ok := ServerComs[args[0]]; !ok {
			return HelpMenu(user)
		}
		srvCom := ServerComs[args[0]]

		if srvCom.RequiredAuthLevel > user.AuthLevel {
			return HelpMenu(user)
		}

		for _, role := range srvCom.RequiredRoles {
			if !slices.Contains(user.Roles, role) {
				return HelpMenu(user)
			}
		}

		msg := "Usage: " + args[0] + strings.Repeat(" [arg]", srvCom.ArgsLen[0]) + strings.Repeat(" [arg?]", srvCom.ArgsLen[1]-srvCom.ArgsLen[0]) + "\r\n"
		msg += srvCom.Description + "\r\n"
		if srvCom.ExampleDescription != "" {
			msg += "Example: " + args[0] + " " + srvCom.ExampleDescription + "\r\n"
		}
		msg += "\n" + srvCom.DetailedDescription + "\r\n"

		msgReturn += fmt.Sprintf("\r%v\n", msg)

		return msgReturn
	}

	msg := "Usage: <command> [args]...\r\n"
	msg += "Execute server commands.\r\n"
	msg += "Example: help exit\r\n\n"
	msg += "Available:\r\n"

	msg += fmt.Sprintf("  %-10v %v\r\n", "help", "Show this help menu.")
	msg += fmt.Sprintf("  %-10v %v\r\n", "autocomplete", "Get autocomplete information.")
	for v, srvCom := range ServerComs {
		if srvCom.RequiredAuthLevel > user.AuthLevel {
			continue
		}

		rolesPassed := true
		for _, role := range srvCom.RequiredRoles {
			if !slices.Contains(user.Roles, role) {
				rolesPassed = false
				break
			}
		}
		if !rolesPassed {
			continue
		}

		msg += fmt.Sprintf("  %-10v %v\r\n", v, srvCom.Description)
	}

	return fmt.Sprintf("\r%v\n", msg)
}

func AutoComplete(user Auth.User, args ...string) []byte {
	coms := []string{"help", "autocomplete"}
	for v, srvCom := range ServerComs {
		if srvCom.RequiredAuthLevel > user.AuthLevel {
			continue
		}

		rolesPassed := true
		for _, role := range srvCom.RequiredRoles {
			if !slices.Contains(user.Roles, role) {
				rolesPassed = false
				break
			}
		}
		if !rolesPassed {
			continue
		}

		coms = append(coms, "help "+v)
		coms = append(coms, v)
		for _, ac := range srvCom.AutoComplete {
			coms = append(coms, v+" "+ac)
		}
	}

	jsonBytes, err := json.Marshal(coms)
	if err != nil {
		return []byte("[" + strings.Join(coms, ",") + "]")
	}

	return jsonBytes
}

func Close() {
	lgr.Log("debug", "Com", "Closing", "")

	close(OutCh)

	for name := range openDataBases {
		lgr.Log("info", "Com", "Dumping", name)

		for _, err := range openDataBases[name].Dump() {
			lgr.Log("error", "Com", name, err)
		}

		lgr.Log("debug", "Com", "Clearing", name)
		delete(openDataBases, name)
	}

	lgr.Log("debug", "Com", "Closed", "")
}

func Init(f Files, log *logger.Logger, cfg Config) {
	log.Log("debug", "Com", "Initializing", "")

	files = f
	lgr = log
	config = cfg

	if config.SonosIP != "" {
		if zpTmp, err := Gonos.NewZonePlayer(config.SonosIP); err == nil {
			zp = zpTmp
		} else if zpTmp, err := Gonos.DiscoverZonePlayer(1); err == nil {
			zp = zpTmp[0]
		} else if zpsTmp, err := Gonos.ScanZonePlayer(config.SonosIP, 1); err == nil {
			zp = zpsTmp[0]
		} else {
			lgr.Log("error", "Com", "Failed", fmt.Sprintf("Connecting to Sonos speaker: %v", config.SonosIP))
		}
	}

	OutCh = make(chan string)

	if len(config.TapoPlugIPS) > 0 && (config.TapoUsername == "" || config.TapoPassword == "") {
		lgr.Log("error", "Com", "Failed", "Invalid username or Password for tapo!")
		lgr.Log("debug", "Com", "Initialized", "")
		return
	}

	TapoClients = map[string]*tapogo.Tapo{}
	for _, ip := range config.TapoPlugIPS {
		if ip == "" {
			lgr.Log("error", "Com", "Failed", fmt.Sprintf("Connecting to tapo plug: %v", ip))
			continue
		}

		for i := range 10 {
			tc, err := tapogo.NewTapo(ip, config.TapoUsername, config.TapoPassword, &tapogo.TapoOptions{HandshakeDelayDuration: time.Millisecond * time.Duration(100)})
			if err != nil {
				if i == 9 {
					lgr.Log("error", "Com", "Failed", fmt.Sprintf("Connecting to tapo plug: %v > Info: %v", ip, err))
				}
				continue
			}

			tcInfo, err := tc.DeviceInfo()
			if err != nil {
				if i == 9 {
					lgr.Log("error", "Com", "Failed", fmt.Sprintf("Connecting to tapo plug: %v > Info: %v", ip, err))
				}
				continue
			}

			nickname, err := base64.StdEncoding.DecodeString(tcInfo.Result.Nickname)
			if err != nil {
				if i == 9 {
					lgr.Log("error", "Com", "Failed", fmt.Sprintf("Connecting to tapo plug: %v > Info: %v", ip, err))
				}
				continue
			}

			TapoClients[string(nickname[:])] = tc
			break
		}
	}

	lgr.Log("debug", "Com", "Initialized", "")
}
