from ast import literal_eval
from json import load
from os import path as osPath
from random import choices
from string import digits
from threading import Thread
from time import sleep

from PyP100 import PyP110
from requests.exceptions import ConnectTimeout
from rsa import PrivateKey, PublicKey, decrypt, encrypt


class tapo:
    def __init__(self, userData, return_var=None):
        workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "")
        self.tapoLoginAttemts = 0
        self.plugs = {}
        self.commands = {"login": ["Home", tapo.login, None]}

        with open(f"{workFolder}/server/config.json", "r", encoding="UTF-8") as fileR:
            plugsIps = load(fileR)["TapoPlugIps"]

        if not return_var is None:
            return_var[0] = self

        if userData["TapoUser"] == "" or userData["TapoPassword"] == "":
            return None

        with open(f"{workFolder}/server/ssl/pvk.pem", "r", encoding="UTF-8") as fileR:
            svPvk = PrivateKey.load_pkcs1(fileR.read())

        def loadPlug(ip: str, return_var):
            plug = PyP110.P110(ip, userData["TapoUser"], decrypt(literal_eval(userData["TapoPassword"]), svPvk).decode())
            try:
                plug.handshake()
            except (ConnectTimeout, KeyError):
                return None

            try:
                plug.login()
            except Exception:
                return_var[0] = None
                return False

            self.plugs[plug.getDeviceName()] = plug
            return_var[0] = plug

        threads = []
        threadsReturns = {}
        for ip in plugsIps:
            threadsReturns[ip] = [None]
            trd = Thread(target=loadPlug, kwargs={"ip": ip, "return_var": threadsReturns[ip]})
            trd.start()
            threads.append((trd, ip))
        for trd, name in threads:
            trd.join()
            if threadsReturns[name][0] is None:
                continue
            elif threadsReturns[name][0] is False:
                self.plugs = {}
                if not return_var is None:
                    return_var[0] = self
                return None
            self.plugs[threadsReturns[name][0].getDeviceName()] = threadsReturns[name][0]

        if self.plugs is {}:
            if not return_var is None:
                return_var[0] = self
            return None

        self.commands = {
            "login": ["Home", tapo.login],
            "state": ["Home", tapo.getState],
            "history": ["Home", tapo.getHistory],
            "on": ["Home", tapo.on],
            "off": ["Home", tapo.off],
        }

        if not return_var is None:
            return_var[0] = self

    async def login(clT, usr: str, psw: str):
        if clT.tapo.tapoLoginAttemts >= 3:
            print("To many tapo login attempts!")
            raise PermissionError("To many tapo login attempts!")
        sleep(int("".join(choices(digits, k=3))) / 250)
        clT.tapo.tapoLoginAttemts += 1
        clT.tapo.plugs = {}
        clT.tapo.commands = {"login": ["Home", tapo.login, None]}

        if usr == "" or psw == "":
            raise AttributeError("WARNING: No tapo user was registered, tapo commands will be unavailable!")

        workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "")
        with open(f"{workFolder}/server/config.json", "r", encoding="UTF-8") as fileR:
            plugsIps = load(fileR)["TapoPlugIps"]

        with open(f"{workFolder}/server/ssl/pub.pem", "r", encoding="UTF-8") as fileR:
            svPub = PublicKey.load_pkcs1(fileR.read())
        with open(f"{workFolder}/server/ssl/pvk.pem", "r", encoding="UTF-8") as fileR:
            svPvk = PrivateKey.load_pkcs1(fileR.read())

        psw = encrypt(decrypt(literal_eval(psw), clT.pvk).decode().encode(), svPub)
        clT.userData["TapoUser"] = str(usr)
        clT.userData["TapoPassword"] = str(psw)

        for ip in plugsIps:
            plug = PyP110.P110(ip, clT.userData["TapoUser"], decrypt(literal_eval(clT.userData["TapoPassword"]), svPvk).decode())
            try:
                plug.handshake()
            except ConnectTimeout:
                continue

            try:
                plug.login()
            except Exception:
                clT.tapo.plugs = {}
                raise PermissionError("WARNING: Failed tapo login, tapo commands will be unavailable!")

            clT.tapo.plugs[plug.getDeviceName()] = plug

        if clT.tapo.plugs is {}:
            raise FileNotFoundError("WARNING: No tapo device was discovered, tapo commands will be unavailable!")

        clT.tapo.commands = {
            "login": ["Home", tapo.login],
            "state": ["Home", tapo.getState],
            "history": ["Home", tapo.getHistory],
            "on": ["Home", tapo.on],
            "off": ["Home", tapo.off],
        }

        for dataIndex in range(0, clT.server.tokenManager.count("tokens", True)):
            userDataHeader = [pair[0] for pair in clT.server.tokenManager.template()["template"]["sheets"]["tokens"]]
            userData = clT.server.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
            if clT.token == userData[userDataHeader.index("Token")]:
                userData[userDataHeader.index("TapoUser")] = clT.userData["TapoUser"]
                userData[userDataHeader.index("TapoPassword")] = clT.userData["TapoPassword"]

                clT.server.tokenManager.mod("tokens", dataIndex, "*", userData)
                break

        await clT.commands["reload"](clT)
        return await tapo.getState(clT)

    async def getState(clT):
        data = {"Total": {"model": "total", "state": False, "duration": 0, "overheated": False, "protection": "none", "currentPower": 0, "todayTime": 0, "monthlyTime": 0, "todayPower": 0, "monthlyPower": 0}}

        for plug in clT.tapo.plugs:
            deviceInfo = clT.tapo.plugs[plug].getDeviceInfo()
            deviceEnergy = clT.tapo.plugs[plug].getEnergyUsage()

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

        return {"current": data}

    async def getHistory(clT=None):
        workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/srvcoms", "")
        with open(f"{workFolder}/shared/tapoMonitor/tapoMonitor.json", "r", encoding="UTF-8") as fileR:
            data = load(fileR)

        return {"history": data}

    async def on(clT, plug):
        if plug in clT.tapo.plugs:
            clT.tapo.plugs[plug].turnOn()

        return await tapo.getState(clT)

    async def off(clT, plug):
        if plug in clT.tapo.plugs:
            clT.tapo.plugs[plug].turnOff()

        return await tapo.getState(clT)
