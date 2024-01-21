from ast import literal_eval
from datetime import datetime
from json import load
from os import listdir, makedirs, path as osPath


class logger:
    def __init__(
        self,
        logs: tuple | list = (),
        spoofLog: str = None,
        spoofExecutor: str = None,
        return_var: list = [None],
    ):
        self.workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/mod", "/server")
        self.logs = logs
        self.spoofLog = spoofLog
        self.spoofExecutor = spoofExecutor
        self.dataSplitter = "%%"

        if not osPath.exists(self.workFolder):
            makedirs(self.workFolder)
        if not osPath.exists(f"{self.workFolder}/logs"):
            makedirs(f"{self.workFolder}/logs")

        for log in self.logs:
            if not osPath.exists(f"{self.workFolder}/logs/{log}"):
                makedirs(f"{self.workFolder}/logs/{log}")

        self.commands = {
            "template": ["Admin", self.com_template],
            "read": ["Admin", self.com_read],
        }

        if not return_var is None:
            return_var[0] = self

    def _verifyAllowed(self, log):
        if not log in self.logs:
            raise SyntaxError(f"Log is not allowed, use one of {self.logs}")

        if not osPath.exists(f"{self.workFolder}/logs/{log}") or not osPath.isdir(f"{self.workFolder}/logs/{log}"):
            raise SyntaxError(f"Log does not exist, use one of {self.logs}")

    def _verifyCriticality(self, criticality: str):
        validCriticality = {"warning": 0, "error": 0, "info": 1, "high": 2, "medium": 3, "low": 4, "debug": 5}
        if not criticality in validCriticality:
            raise ValueError(f"Invalid criticality: {criticality} -> warning, error, info, high, medium, low, debug")
        return validCriticality[criticality]

    def _verifyStatus(self, status: str):
        if not status in ["", "executed", "missing", "unknown", "failed", "cancelled", "success"]:
            raise ValueError(f"Invalid status: {status} -> executed, missing, unknown", "failed", "cancelled", "success")

    def _checkLogFile(self, filePath: str):
        if not osPath.exists("/".join(filePath.split("/")[:-1])):
            makedirs("/".join(filePath.split("/")[:-1]))
        if not osPath.exists(filePath):
            with open(filePath, "w", encoding="UTF-8") as fileW:
                fileW.write("")
        return filePath

    def _getPrintStr(self, time: str, criticality: str, executor: str = "", msg: str = "", status: str = ""):
        prefix = f"[{time}] {criticality:^7} | "
        prefix += f'{executor[:15] + ("..." if len(executor) > 18 else ""):<18}{status:>9}'

        return f"\r{prefix} -> {msg}"

    def _getLogStr(self, time: str, criticality: str, executor: str = "", msg: str = "", status: str = ""):
        return self.dataSplitter.join((time, criticality, executor, msg, status)) + "<END>\n"

    def _sanatizeData(self, data: dict | list):
        if isinstance(data, dict):
            return {k: "REDACTED" if k in ("Password", "TapoPassword") else self._sanatizeData(v) for k, v in data.items()}
        if isinstance(data, list):
            tmp = []
            for v in data:
                try:
                    if isinstance(literal_eval(v), bytes):
                        tmp.append("REDACTED")
                        continue
                except (ValueError, SyntaxError):
                    pass

                tmp.append(self._sanatizeData(v))

            return tmp

        return data

    def _available(self, log: str):
        self._verifyAllowed(log)
        logs = [file.split(".")[0] for file in listdir(f"{self.workFolder}/logs/{log}") if osPath.isfile(f"{self.workFolder}/logs/{log}/{file}")]
        return sorted(logs, key=lambda log: int(log.replace("-", "")))

    def _read(self, log: str, date: str):
        self._verifyAllowed(log)
        if not osPath.exists(f"{self.workFolder}/logs/{log}/{date}.log"):
            raise FileNotFoundError(f"Log {log} contains no log for {date}!")

        with open(f"{self.workFolder}/logs/{log}/{date}.log", "r", encoding="UTF-8") as fileR:
            fileData = fileR.read().split("<END>\n")

        returnDict = {}
        for i, line in enumerate(reversed(fileData)):
            if line == "":
                continue
            returnDict[str(i)] = line.split("%%")

        return returnDict

    def _log(self, log, criticality: str, executor: str = "", msg: str = "", status: str = ""):
        self._verifyAllowed(log)
        criticalityLevel = self._verifyCriticality(criticality)
        self._verifyStatus(status)
        now = datetime.now()

        with open(f"{self.workFolder}/config.json", "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)
        if criticality == "debug" and not fileData["Debug"]:
            return None

        print(self._getPrintStr(now.strftime("%y-%m-%d %H:%M:%S"), criticality, executor, msg, status))

        if fileData["LogLevel"] < criticalityLevel:
            return None

        with open(self._checkLogFile(f'{self.workFolder}/logs/{log}/{now.strftime("%Y-%m")}.log'), "a", encoding="UTF-8") as fileA:
            fileA.write(self._getLogStr(now.strftime("%y-%m-%d %H:%M:%S"), criticality, executor, msg, status))

    def template(self):
        return {"template": {log: self._available(log) for log in self.logs}}

    async def com_template(self, clT):
        return self._sanatizeData(self.template())

    def read(self, log: str = "", date: str = ""):
        log = log if self.spoofLog is None else self.spoofLog
        if date == "":
            return {log: {dateTmp: self._read(log, dateTmp) for dateTmp in self._available(log)}}
        return {log: {date: self._read(log, date)}}

    async def com_read(self, clT, log: str, date: str = ""):
        return self._sanatizeData(self.read(log, date))

    def log(self, log: str = "", criticality: str = "", executor: str = "", msg: str = "", status: str = ""):
        self._log(log if self.spoofLog is None else self.spoofLog, criticality, executor if self.spoofExecutor is None else self.spoofExecutor, msg, status)
