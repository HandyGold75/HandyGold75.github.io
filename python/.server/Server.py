from datetime import datetime, timedelta
from json import JSONDecodeError, dump, load
from multiprocessing import Process
from os import makedirs, path as osPath, remove
from signal import SIGINT, SIGTERM, signal
from sys import exit, modules
from threading import Thread
from time import sleep
from traceback import format_exc

from rsa import PrivateKey, PublicKey, encrypt, newkeys

_default_modules = list(modules)

from lib import clientHandler, fileServer, logger, tapoMonitor, timedInput

_local_modules = []
for mod in list(modules):
    if not mod in _default_modules:
        _local_modules.append(mod)


class server:
    requiredFiles = {
        "/config.json": {
            "IP": "127.0.0.1",
            "PORT": 17510,
            "Domain": "HandyGold75.com",
            "SonosSubnet": [],
            "TapoPlugIps": [],
            "TapoUsername": "",
            "TapoPassword": "",
            "LogLevel": 3,
            "Debug": False,
            "Modified": 0,
        },
        "/ssl/pub.pem": PublicKey,
        "/ssl/pvk.pem": PrivateKey,
    }

    def __init__(self):
        self.stop = False
        self.workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/")}/server'
        self.runAtBoot = (clientHandler, fileServer, tapoMonitor)

        self.si = Thread(target=self.serverInput)
        self.subpros = {}
        self.restartedSubpros = {}
        self.failedSubpros = []
        self.lastServerCommand = ""

        self.log = logger(("server",), "server", "Server").log

        self.commands = {
            "help": self.help,
            "restart": self.restart,
            "exit": self.quit,
        }

        self.validateFiles()

        signal(SIGINT, self.quit)
        signal(SIGTERM, self.quit)

    def validateFiles(self):
        for file in self.requiredFiles:
            if self.requiredFiles[file].__class__ in (PrivateKey.__class__, PublicKey.__class__) and not osPath.exists(f"{self.workFolder}{file}"):
                for warning in (
                    "pub.pem or pvk.pem was not found! Valid location:",
                    f"    {self.workFolder}/ssl",
                    f"Keys will be automaticly generated, passwords of default accounts and tapo monitor account will be reset, old encrypted data will cause crashes!",
                ):
                    self.log(criticality="error", msg=warning)

                if not osPath.exists(f"{self.workFolder}/ssl"):
                    makedirs(f"{self.workFolder}/ssl")
                if str(input("Continue (y/n)? ")).lower() != "y":
                    exit()

                self.log(criticality="info", msg=f"Generating keys, this will take some time.")
                pub, pvk = newkeys(16384, poolsize=8)
                with open(f"{self.workFolder}/ssl/pub.pem", "w", encoding="UTF-8") as fileW:
                    fileW.write(pub.save_pkcs1().decode())
                with open(f"{self.workFolder}/ssl/pvk.pem", "w", encoding="UTF-8") as fileW:
                    fileW.write(pvk.save_pkcs1().decode())

                with open(f"{self.workFolder}/config.json", "r", encoding="UTF-8") as fileR:
                    config = load(fileR)
                config["TapoPassword"] = str(encrypt(input("Tapo monitor password: ").encode(), pub))
                with open(f"{self.workFolder}/config.json", "w", encoding="UTF-8") as fileW:
                    dump(config, fileW, indent=2)

                continue

            if osPath.exists(f"{self.workFolder}{file}"):
                if not type(self.requiredFiles[file]) is dict:
                    continue

                fileValid = True
                with open(f"{self.workFolder}{file}", "r", encoding="UTF-8") as fileR:
                    try:
                        fileData = load(fileR)
                    except JSONDecodeError:
                        self.log(criticality="warning", msg=f'File "{file}" is improparly formatted, resetting file to default!')
                        fileValid = False

                if fileValid:
                    for requirement in self.requiredFiles[file]:
                        if len(requirement) >= 128:
                            continue

                        if not requirement in fileData:
                            self.log(criticality="warning", msg=f'File "{file}" is missing value "{requirement}", resetting file to default!')
                            fileValid = False
                            break
                        if not type(self.requiredFiles[file][requirement]) is type(fileData[requirement]):
                            self.log(criticality="warning", msg=f'File "{file}" has improparly formatted value "{requirement}", resetting file to default!')
                            fileValid = False
                            break

                if not fileValid:
                    with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                        dump(self.requiredFiles[file], fileW, indent=2)

            else:
                if len(file.split("/")) > 2 and not osPath.exists(f'{self.workFolder}{"/".join(file.split("/")[:-1])}'):
                    self.log(criticality="info", msg=f'Creating directory: {self.workFolder}{"/".join(file.split("/")[:-1])}')
                    makedirs(f'{self.workFolder}{"/".join(file.split("/")[:-1])}')

                self.log(criticality="info", msg=f"Creating file: {self.workFolder}{file}")
                if not type(self.requiredFiles[file]) is dict:
                    with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                        fileW.write(self.requiredFiles[file])
                    continue
                else:
                    with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                        dump(self.requiredFiles[file], fileW, indent=2)

            with open(f"{self.workFolder}{file}", "r", encoding="UTF-8") as fileR:
                fileData = load(fileR)

            for requirement in self.requiredFiles[file]:
                if len(requirement) < 128:
                    continue
                if not requirement in fileData or not "Password" in fileData[requirement] or not "User" in fileData[requirement] or len(fileData[requirement]["Password"]) > 256:
                    continue

                with open(f"{self.workFolder}/ssl/pub.pem", "r", encoding="UTF-8") as fileR:
                    svPub = PublicKey.load_pkcs1(fileR.read())
                self.log(criticality="info", msg=f'Encrypting password of user: {fileData[requirement]["User"]}')
                fileData[requirement]["Password"] = str(encrypt(fileData[requirement]["Password"].encode(), svPub))
                with open(f"{self.workFolder}{file}", "w", encoding="UTF-8") as fileW:
                    dump(fileData, fileW, indent=2)

    def watchdog(self):
        while not self.stop:
            try:
                sleep(0.25)
                for restartTime in dict(self.restartedSubpros):
                    if float(restartTime) < (datetime.now() - timedelta(seconds=30)).timestamp():
                        self.restartedSubpros.pop(restartTime)

                for name in self.subpros:
                    if self.subpros[name].is_alive() or name in self.failedSubpros:
                        continue

                    restartCount = 0
                    for restartTime in dict(self.restartedSubpros):
                        if self.restartedSubpros[restartTime] == name:
                            restartCount += 1

                    if restartCount >= 3:
                        self.failedSubpros.append(name)
                        self.log(criticality="error", msg=f"Restarted subproces to quickly to many times: {name}")
                        break

                    self.log(criticality="warning", msg=f"Watchdog: Process {name} died! Exitcode: {self.subpros[name].exitcode}")
                    self.subpros[name].join()

                    for cls in self.runAtBoot:
                        if name != cls.__name__:
                            continue

                        self.log(criticality="info", msg=f"Starting subproces: {cls.__name__}")
                        process = Process(target=cls().main)
                        self.subpros[cls.__name__] = process
                        self.restartedSubpros[str(datetime.now().timestamp())] = cls.__name__
                        process.start()

                if not osPath.exists(f"{self.workFolder}/commandStack.txt"):
                    continue

                with open(f"{self.workFolder}/commandStack.txt", "r", encoding="UTF-8") as fileA:
                    fileData = fileA.readlines()
                remove(f"{self.workFolder}/commandStack.txt")

                for line in fileData:
                    args = line.split(" ")
                    if not args[0] in self.commands:
                        continue

                    self.log(criticality="high", msg=f"Executing: {' '.join(args)}")
                    out = self.commands[args[0]](*args[1:])
                    if not out is None:
                        print(out)

            except Exception as err:
                self.log(criticality="error", msg=format_exc())

        return None

    def serverInput(self):
        inputPrefill = ""
        while not self.stop:
            srvInp, timedOut = timedInput(prompt="> ", prefill=inputPrefill, timeout=3)
            inputPrefill = ""
            if timedOut:
                continue

            if srvInp == "\\":
                inputPrefill = self.lastServerCommand
                continue
            elif srvInp.startswith("[") or srvInp == "":
                continue

            self.lastServerCommand = srvInp
            srvInp = str(srvInp).split(" ")
            if srvInp[0] in self.commands:
                with open(f"{self.workFolder}/commandStack.txt", "a" if osPath.exists(f"{self.workFolder}/commandStack.txt") else "w", encoding="UTF-8") as fileW:
                    fileW.write(f'\n{" ".join(srvInp)}')
            else:
                print(f"\nUnknown command!")

    def help(self):
        return f'Commands: \n    {f"\n    ".join(self.commands)}'

    def restart(self):
        self.quit(doExit=False)

        self.log(criticality="info", msg=f"Reloading server")

        for mod in list(modules):
            if mod in _local_modules or modules[mod] == None:
                del modules[mod]

        from lib import clientHandler, fileServer, logger, tapoMonitor, timedInput

        self.__init__()
        self.start()

    def quit(self, *args, doExit=True):
        if not self.si.is_alive() or self.stop:
            return None

        self.log(criticality="info", msg=f"Stopping thread: serverInput")
        self.stop = True
        self.si.join()

        for name in self.subpros:
            if self.subpros[name].is_alive():
                self.log(criticality="info", msg=f"Terminating subproces: {name}")
                self.subpros[name].terminate()
                self.subpros[name].join(timeout=10)
                if self.subpros[name].exitcode is None:
                    self.log(criticality="info", msg=f"Killing subproces: {name}")
                    self.subpros[name].kill()
                    self.subpros[name].join()

        if doExit:
            exit()

    def start(self):
        self.stop = False
        for cls in self.runAtBoot:
            self.log(criticality="info", msg=f"Starting subproces: {cls.__name__}")
            process = Process(target=cls().main)
            self.subpros[cls.__name__] = process
            process.start()

        self.log(criticality="info", msg=f"Starting thread: serverInput")
        self.si.start()

    def main(self):
        self.start()
        self.watchdog()
        self.quit()


if __name__ == "__main__":
    server().main()
