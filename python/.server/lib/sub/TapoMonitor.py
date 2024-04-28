from ast import literal_eval
from datetime import datetime, timedelta
from json import dump, load
from os import listdir, makedirs, path as osPath
from signal import SIGTERM, signal
from sys import exit, platform
from time import sleep
from traceback import format_exc

from psutil import Process as psProcess
from PyP100 import PyP110
from requests.exceptions import ConnectTimeout
from rsa import PrivateKey, decrypt

from ..mod import logger

if platform == "win32":
    from psutil import BELOW_NORMAL_PRIORITY_CLASS, IOPRIO_LOW
else:
    from psutil import IOPRIO_CLASS_IDLE


class tapoMonitor:
    def __init__(self):
        self.stop = False
        self.workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/shared/tapoMonitor")

        self.requiredFiles = {"/tapoMonitor.json": {"model": str, "state": bool, "duration": int, "overheated": bool, "protection": str, "currentPower": int, "todayTime": int, "monthlyTime": int, "todayPower": int, "monthlyPower": int}}
        self.configStyleFiles = ["/config.json"]
        self.sharedServerFiles = ["/config.json"]

        self.monitorWeeksOfMonth = (1, 2, 3, 4, 5)
        self.monitorDays = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
        self.monitorTime = "23:45:00"

        self.log = logger(("tapoMonitor",), "tapoMonitor", "TapoMonitor").log

        if not osPath.exists(self.workFolder):
            makedirs(self.workFolder)

        self.loadFiles()
        signal(SIGTERM, self.quit)

    def loadFiles(self):
        from Server import server as rootServer

        for file in tuple(self.sharedServerFiles):
            shortFile = f'/{file.split("/")[-1]}'
            if not shortFile in self.sharedServerFiles:
                self.sharedServerFiles.append(shortFile)

            if not type(rootServer.requiredFiles[file]) is dict:
                self.requiredFiles[shortFile] = type(rootServer.requiredFiles[file])
                continue

            if file in self.configStyleFiles:
                self.requiredFiles[shortFile] = {}
                for item in rootServer.requiredFiles[file]:
                    self.requiredFiles[shortFile][item] = type(rootServer.requiredFiles[file][item])
                continue

            self.requiredFiles[shortFile] = {}
            for item in rootServer.requiredFiles[file][tuple(rootServer.requiredFiles[file])[-1]]:
                self.requiredFiles[shortFile][item] = type(rootServer.requiredFiles[file][tuple(rootServer.requiredFiles[file])[-1]][item])
            continue

        for file in self.requiredFiles:
            if file in self.sharedServerFiles:
                continue

            if len(file.split("/")) > 2:
                if not osPath.exists(f'{self.workFolder}{"/".join(file.split("/")[:-1])}'):
                    makedirs(f'{self.workFolder}{"/".join(file.split("/")[:-1])}')

            if not osPath.exists(f"{self.workFolder}{file}"):
                with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                    if type(self.requiredFiles[file]) is dict:
                        dump({}, fileW)
                        continue
                    fileW.write("")

    def quit(self, *args):
        self.stop = True

    def verify(self, file: str, obj: dict):
        if not type(self.requiredFiles[file]) is dict:
            if not type(obj) is self.requiredFiles[file]:
                raise SyntaxError(f"Type mismatch for {str(obj)} {str(type(obj))} != {str(self.requiredFiles[file])}")
            return None

        for mainObj in obj:
            for check in self.requiredFiles[file]:
                if not check in obj[mainObj]:
                    raise SyntaxError(f"Missing record {check} ({str(mainObj)})")

                if not self.requiredFiles[file][check] is type(obj[mainObj][check]):
                    raise SyntaxError(f"Type mismatch record for {check} {str(self.requiredFiles[file][check])} != {str(type(obj[mainObj][check]))}")

            for check in obj[mainObj]:
                if not check in self.requiredFiles[file]:
                    raise SyntaxError(f"Additional record {check} ({str(mainObj)})")

    def findFile(self, file):
        if not file in self.requiredFiles:
            raise NameError(f"File {file} not found!")

        serverFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/server")

        if file.split("/")[-1] in listdir(serverFolder):
            return f'{serverFolder}/{file.split("/")[-1]}'
        elif file.split("/")[-1] in listdir(self.workFolder):
            return f'{self.workFolder}/{file.split("/")[-1]}'

        raise NameError(f"File {file} not found!")

    def write(self, file: str, obj: dict):
        if file in self.configStyleFiles:
            self.verify(file, obj)
            with open(self.findFile(file), "w", encoding="UTF-8") as fileW:
                dump(obj, fileW, indent=2)

            return obj

        objSort = {}
        for subObj in obj:
            objSort[subObj] = {}
            for tag in obj[subObj]:
                objSort[subObj][tag] = {}
                for key in self.requiredFiles[file]:
                    if key in obj[subObj][tag]:
                        objSort[subObj][tag][key] = obj[subObj][tag][key]

        try:
            objSort = dict(sorted(objSort.items(), key=lambda x: int(x[0])))
        except ValueError:
            objSort = dict(sorted(objSort.items()))

        for subObjSort in objSort:
            self.verify(file, objSort[subObjSort])
        with open(self.findFile(file), "w", encoding="UTF-8") as fileW:
            dump(objSort, fileW, indent=2)

        return objSort

    def start(self):
        with open(osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "") + "/server/ssl/pvk.pem", "r", encoding="UTF-8") as fileR:
            svPvk = PrivateKey.load_pkcs1(fileR.read())

        with open(self.findFile("/config.json"), "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)

        self.plugsIps = fileData["TapoPlugIps"]
        self.usr = fileData["TapoUsername"]
        self.psw = fileData["TapoPassword"]

        plugs = {}
        for ip in self.plugsIps:
            plug = PyP110.P110(ip, self.usr, decrypt(literal_eval(self.psw), svPvk).decode())
            try:
                plug.handshake()
            except (ConnectTimeout, KeyError):
                self.log(criticality="error", msg=f'Unable to connect to Tapo plug "{ip}"!')
                continue
            try:
                plug.login()
            except Exception:
                raise PermissionError(f'Unable to log into Tapo plug "{ip}"!')

            plugs[plug.getDeviceName()] = plug

        self.log(criticality="info", msg="Started tapo monitor")
        self.plugs = plugs
        return plugs

    def getState(self):
        data = {"Total": {"model": "total", "state": False, "duration": 0, "overheated": False, "protection": "none", "currentPower": 0, "todayTime": 0, "monthlyTime": 0, "todayPower": 0, "monthlyPower": 0}}

        for i in range(0, 5):
            for plug in self.plugs:
                try:
                    if "result" in self.plugs[plug].getDeviceInfo() and "result" in self.plugs[plug].getEnergyUsage():
                        hasResults = True
                        continue
                except KeyError:
                    self.start()
                    hasResults = False
                    break

            if hasResults:
                break

        for plug in self.plugs:
            deviceInfo = self.plugs[plug].getDeviceInfo()
            deviceEnergy = self.plugs[plug].getEnergyUsage()
            data[plug] = {}

            for key in (("model", "model"), ("state", "device_on"), ("duration", "on_time"), ("overheated", "overheated"), ("protection", "power_protection_status")):
                data[plug][key[0]] = deviceInfo["result"][key[1]]

                if type(deviceInfo["result"][key[1]]) is int:
                    data["Total"][key[0]] += deviceInfo["result"][key[1]]
                elif type(deviceInfo["result"][key[1]]) is bool and deviceInfo["result"][key[1]]:
                    data["Total"][key[0]] = deviceInfo["result"][key[1]]

            for key in (("currentPower", "current_power"), ("todayTime", "today_runtime"), ("monthlyTime", "month_runtime"), ("todayPower", "today_energy"), ("monthlyPower", "month_energy")):
                data[plug][key[0]] = deviceEnergy["result"][key[1]]

                if type(deviceEnergy["result"][key[1]]) is int:
                    data["Total"][key[0]] += deviceEnergy["result"][key[1]]
                elif type(deviceEnergy["result"][key[1]]) is bool and deviceEnergy["result"][key[1]]:
                    data["Total"][key[0]] = deviceEnergy["result"][key[1]]

        return data

    def run(self):
        state = self.getState()

        currentState = {}
        for plug in state:
            currentState[plug] = {f"{int(datetime.now().timestamp())}": state[plug]}

        with open(self.findFile("/tapoMonitor.json"), "r", encoding="UTF-8") as fileR:
            oldState = load(fileR)

        for dict in currentState:
            if not dict in oldState:
                oldState[dict] = {}
            oldState[dict] = {**oldState[dict], **currentState[dict]}

        self.write("/tapoMonitor.json", oldState)
        self.log(criticality="info", msg="Executed monitor logging for Tapo plugs.")

    def getNextDate(self):
        if not ":" in self.monitorTime:
            raise Exception("Unable to set the correct time!")

        date = datetime.now().replace(microsecond=0)
        if len(self.monitorTime.split(":")) > 2:
            isSecondCorrect = False
            for i in range(0, 61):
                if date.second == int(self.monitorTime.split(":")[2]):
                    isSecondCorrect = True
                    break
                date += timedelta(seconds=1)
        else:
            date = date.replace(second=0, microsecond=0)
            isSecondCorrect = True

        if not isSecondCorrect:
            raise Exception("Unable to set the correct second!")

        isMinuteCorrect = False
        for i in range(0, 61):
            if date.minute == int(self.monitorTime.split(":")[1]):
                isMinuteCorrect = True
                break
            date += timedelta(minutes=1)

        if not isMinuteCorrect:
            raise Exception("Unable to set the correct minute!")

        isHourCorrect = False
        for i in range(0, 25):
            if date.hour == int(self.monitorTime.split(":")[0]):
                isHourCorrect = True
                break
            date += timedelta(hours=1)

        if not isHourCorrect:
            raise Exception("Unable to set the correct hour!")

        isWeekCorrect = False
        for i in range(0, 32):
            if int(((date.day - 1) / 7) + 1) in self.monitorWeeksOfMonth:
                isWeekCorrect = True
                break
            date += timedelta(days=1)

        if not isWeekCorrect:
            raise Exception("Unable to set the correct week!")

        isWeekdayCorrect = False
        for i in range(0, 8):
            for day in self.monitorDays:
                if date.weekday() == {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}[day.lower()]:
                    isWeekdayCorrect = True
            if isWeekdayCorrect:
                break
            date += timedelta(days=1)

        if not isWeekdayCorrect:
            raise Exception("Unable to set the correct weekday!")

        return date

    def timeout(self):
        nextMonitorDate = self.getNextDate()
        timeDiff = int(nextMonitorDate.timestamp() - datetime.now().replace(microsecond=0).timestamp())

        self.log(criticality="debug", msg=f'Next monitor scheduled for: {nextMonitorDate.strftime("%Y-%b-%d %H:%M:%S")}')

        while timeDiff > 0:
            timeDiff -= 1
            sleep(1)

            if self.stop:
                exit()
            if timeDiff % 60 == 0:
                timeDiff = int(nextMonitorDate.timestamp() - datetime.now().replace(microsecond=0).timestamp())

    def main(self):
        if platform == "win32":
            psProcess().nice(BELOW_NORMAL_PRIORITY_CLASS)
            psProcess().ionice(IOPRIO_LOW)
        else:
            psProcess().nice(20)
            psProcess().ionice(IOPRIO_CLASS_IDLE)

        self.start()

        while True:
            self.timeout()

            try:
                self.run()
                retryRun = False
            except Exception:
                self.log(criticality="error", msg=f"Failed running monitor for Tapo plugs (Retrying).\nError -> {format_exc()}")
                retryRun = True

            if retryRun:
                self.start()
                try:
                    self.run()
                except Exception:
                    self.log(criticality="error", msg=f"Failed retry monitor for Tapo plugs.\nError -> {format_exc()}")

            sleep(330)


if __name__ == "__main__":
    tapoMonitor().main()
