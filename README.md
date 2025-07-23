# HandyGold75

## Setup

### Frontend

The frontend files can be found in `./`.
The frontend is accessible via [HandyGold75.com](https://HandyGold75.com)

To build the frontend you can use `make && make wasm`.
Alternatively if you don't want to automatically update the go version and dependencies `make wasm` can be used.

### Backend

> [!WARNING]  
> Currently rewriting server files, bak version is currently hosted.

The backend files can be found in `./server/`.
The backend is accessible via [go.HandyGold75.com](https://go.HandyGold75.com)

You can also host you're own backend, this can either be done by building the server or using the release files.
To build the server you can use `make && make build`.
Alternatively if you don't want to automatically update the go version and dependencies `make build` can be used.

After running the server for the first time `config.json` will be generated relative to the executable location.
This file can be used to configure the server.

```jsonc
{
  "IP": "0.0.0.0", // Local IP to bind the server to.
  "Port": 17500, // Local Port to bind the server to.
  "Domain": "HandyGold75.com", // Domain the server is accessible from.
  "SubDomain": "go", // Sub domain the server is accessible from.
  "SonosIP": "", // CIDR ip network where a Sonos speaker may reside for intergartion with Sonos.
  "TapoPlugIps": [], // List of ips where tapo power plugs reside for intergartion with Tapo.
  "TapoUsername": "", // Tapo login username.
  "TapoPassword": "", // Tapo login password.
  "LogLevel": 1, // Minimal (inclusive) log level to CLI; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "LogToFileLevel": 3, // Minimal log level to log file; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "ModuleMaxRestartPerMinute": 3, // Maximum number of restarts a module may get in a minute before the watchdog gives up..
```

### Backend (bak)

The backend files can be found in `./server/`.
The backend is accessible via [go.HandyGold75.com](https://go.HandyGold75.com)

You can also host you're own backend, this can either be done by building the server or using the release files.
To build the server you can use `make && make build`.
Alternatively if you don't want to automatically update the go version and dependencies `make build` can be used.

After running the server for the first time `./server/` will be generated relative to the executable location.
In here this directory the file `config.json` can be used to configure the server.

```jsonc
{
  "IP": "0.0.0.0", // Local IP to bind the server to.
  "Port": 17500, // Local Port to bind the server to.
  "Domain": "HandyGold75.com", // Domain the server is accessible from.
  "SubDomain": "go", // Sub domain the server is accessible from.
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
The server will fall back to an insecure connection in case a certificate is not found or valid.
