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

After running the server for the first time `config.json` and `./data/` will be generated relative to the executable location.
In `config.json` can be used to configure the server. `./data/` contains server generated data such as logs, users and monitoring.

```jsonc
{
  "CLIConfig": {
    "Prefix": "\u001b[31m\u003e\u001b[0m", // CLI promt prefix.
  },
  "SiteConfig": {
    "IP": "0.0.0.0", // Local IP to bind the server to.
    "Port": 17500, // Local Port to bind the server to.
    "SubDomain": "go", // Sub domain the server is accessible from.
    "Domain": "HandyGold75.com", // Domain the server is accessible from.
    "SonosIP": "", // CIDR ip network where a Sonos speaker may reside for intergartion with Sonos.
    "RequestsLimitCom": 180, // Maximum number of com requests from a single IP within timeout limit.
    "RequestsLimitTimoutCom": 1, // Time in minutes com requests timeout from the limit que.
    "RequestsLimitAuth": 10, // Maximum number of auth requests from a single IP within timeout limit.
    "RequestsLimitTimoutAuth": 10, // Time in minutes auth requests timeout from the limit que.
  },
  "TapoConfig": {
    "PlugIPS": [], // List of ips where tapo power plugs reside for intergartion with Tapo.
    "AuthHash": "", // Tapo authentication hash, calculated as base16(sha256(sha1(email)+sha1(password))).
    "Schedule": {
      "Months": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], // Months of the year: `1 - 12`
      "Weeks": [1, 2, 3, 4, 5], // Weeks of the month: `1 - 5`
      "Days": [0, 1, 2, 3, 4, 5, 6], // Days of the week: `0 - 6` (Sunday first day of the week)
      "Hours": [23], // Hours of the day: `0 - 23`
      "Minutes": [59], // Minutes of the hour: `0 - 59`
    },
  },
  "AuthConfig": {
    "TokenExpiresAfterDays": 7, // Maximum number of days a auth token may be valid.
  },
  "ComsConfig": {
    "DataBaseOpenTimeout": 30, // Maxmimum number of minutes a database file will stay open.
  },
  "LogLevel": 1, // Minimal (inclusive) log level to CLI; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "LogToFileLevel": 3, // Minimal log level to log file; `warning: 5`, `error: 5`, `info: 4`, `high: 3`, `medium: 2`, `low: 1`, `debug: 0`.
  "ModuleMaxRestartPerHour": 3, // Maximum number of restarts a services may get in a hour before giving up.
  "Debug": false, // Enables debug logs to CLI.
}
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
