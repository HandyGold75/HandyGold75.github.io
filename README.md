# HandyGold75

## Setup

### Frontend

The frontend files can be found in `./`.
The frontend is accessible via [HandyGold75.com](https://HandyGold75.com)

### Backend

The backend files can be found in `./.server/`.
The backend is accessible via [https.HandyGold75.com:17500](https://https.HandyGold75.com:17500)

You can also host you're own backend, this can either be done by building the server or using the release files.
To build the server you can use `cd ./.server && ./build.sh`.
Alternatively if you don't want to automatically update the go version and dependencies `cd ./.server && go build .` can be used.

After running the server for the first time `./server/` will be generated relative to the executable location.
In here this directory the file `config.json` can be used to configure the server.

```jsonc
{
  "IP": "127.0.0.1", // Local IP to bind the server to.
  "Port": 17500, // Local Port to bind the server to.
  "Domain": "HandyGold75.com", // Domain the server is accessible from.
  "SubDomainHTTPS": "https", // Sub domain the server is accessible from.
  "SonosIP": "", // CIDR ip network where a Sonos speaker may reside for intergartion with Sonos.
  "TapoPlugIps": [], // List of ips where tapo power plugs reside for intergartion with Tapo.
  "TapoUsername": "", // Tapo login username.
  "TapoPassword": "", // Tapo login password.
  "LogLevel": 1, // Minimal (inclusive) log level to CLI; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "LogToFileLevel": 3, // Minimal log level to log file; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "ModuleMaxRestartPerMinute": 3, // Maximum number of restarts a module may get in a minute before the watchdog gives up..
}
```

The server expects SSL certificates (`fullchain.pem` and `privkey.pem`) to be present in either `./server/ssl` or `/etc/letsencrypt/live/{sub}.{domain}`

### Frontend (Python Legacy)

The frontend files can be found in `./.python/`.
The frontend is accessible via [HandyGold75.com/.python](https://HandyGold75.com/.python)

### Backend (Python Legacy)

The backend files can be found in `./.python/.server/`.
The backend is accessible via [wss.HandyGold75.com:17510](WSS://wss.HandyGold75.com:17510)

You can also host you're own backend, this can be done running `python3 Server.py`.

After running the server for the first time `./server/` will be generated relative to the executable location.
In here this directory the file `config.json` can be used to configure the server.

```jsonc
{
  "IP": "127.0.0.1", //  Local IP to bind the server to.
  "PORT": 17510, //  Local Port to bind the server to.
  "Domain": "HandyGold75.com", // Domain the server is accessible from.
  "SonosSubnet": [], // List of ips where Sonos speakers reside for intergartion with Sonos..
  "TapoPlugIps": [], // List of ips where tapo power plugs reside for intergartion with Tapo.
  "TapoUsername": "", // Tapo login username.
  "TapoPassword": "", // Tapo login password; Encrypted during first time setup, do not manualy modify.
  "LogLevel": 3, // Maximum (inclusive) log level to log; `warning: 0`, `error: 0`, `info: 1`, `high: 2`, `medium: 3`, `low: 4`, `debug: 5`.
  "Debug": false, // Print debug statements (requires `LogLevel >= 5`).
  "Modified": 0, // Last modified.
}
```

The server expects SSL certificates (`fullchain.pem` and `privkey.pem`) to be present in either `./server/ssl` or `/etc/letsencrypt/live/wss.{domain}`
