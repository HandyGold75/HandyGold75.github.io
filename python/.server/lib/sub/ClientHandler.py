from ast import literal_eval
from asyncio import get_event_loop, new_event_loop, set_event_loop, sleep as asyncSleep, wait_for
from asyncio.exceptions import TimeoutError
from datetime import datetime, timedelta
from json import dump, dumps, load
from os import listdir, makedirs, path as osPath
from random import choices
from signal import SIGTERM, signal
from ssl import PROTOCOL_TLS_SERVER, SSLContext
from sys import exit
from time import sleep
from traceback import format_exc

from rsa import DecryptionError, PrivateKey, PublicKey, decrypt, encrypt, newkeys
from websockets import serve
from websockets.exceptions import ConnectionClosed, ConnectionClosedError, ConnectionClosedOK

from .. import srvcoms
from ..mod import fileManager, logger


class clientHandler:
    def __init__(self):
        self.stop = False

        self.workFolder = f'{osPath.split(__file__)[0].replace(chr(92), "/").replace("/lib/sub", "")}'
        self.sslCertPaths = (f"/etc/letsencrypt/live/wss.handygold75.com", f"{self.workFolder}/server/ssl/wss")

        self.requiredFiles = {}
        self.configStyleFiles = ["/config.json"]
        self.sharedServerFiles = ["/config.json"]

        self.log = logger(("clientHandler",), "clientHandler", "ClientHandler").log

        with open(f"{self.workFolder}/server/ssl/pub.pem", "r", encoding="UTF-8") as fileR:
            svPub = PublicKey.load_pkcs1(fileR.read())
        with open(f"{self.workFolder}/server/ssl/pvk.pem", "r", encoding="UTF-8") as fileR:
            svPvk = PrivateKey.load_pkcs1(fileR.read())

        self.defaultTokens = {
            "0": {
                "User": "admin",
                "Token": "111hypikGqYXff3W6J8lFRIFZVgv2nikUcRGwnIS2EwAnXze6bCVP9lAgGmUG0aHeXUTu8NvPd8wvLOBgn1hxxTaQq3ZEJMowpCbs1z4x8bldcEkqZjKWVhCPP7YnbLX",
                "Password": str(encrypt("!Admin69".encode(), svPub)),
                "Auth": 1,
                "Roles": ["Admin"],
                "Expires": 0.0,
                "Modified": 0.0,
                "Active": True,
                "TapoUser": "",
                "TapoPassword": "",
                "Notes": "Is Admin",
            },
            "1": {
                "User": "user",
                "Token": "222k80sfTO7W4fufUsctZyeyPXWSln5cM4pI6Fh3SJZjSwL5xUVk5WUnsM8aVDEmPk9e6a3ICj4XshhNlP3yobdE8YEngBNfDGgTWqAaHF0gYpQSta2kuKmeI1VuRWPE",
                "Password": str(encrypt("!User69".encode(), svPub)),
                "Auth": 2,
                "Roles": [],
                "Expires": 0.0,
                "Modified": 0.0,
                "Active": True,
                "TapoUser": "",
                "TapoPassword": "",
                "Notes": "Is User",
            },
            "2": {
                "User": "guest",
                "Token": "333zTMU8lgHon3id7EXWl2RLVJcxyRWGShNntII18MRhZMGpg6Zt3tKDNNe81H13dcThPNXAgRcSD65jieLsysdhVxWhnDBaeVonb4No8xYMtrGvc5ShwYqM8Rdedz81",
                "Password": str(encrypt("!Guest69".encode(), svPub)),
                "Auth": 3,
                "Roles": [],
                "Expires": 0.0,
                "Modified": 0.0,
                "Active": True,
                "TapoUser": "",
                "TapoPassword": "",
                "Notes": "Is Guest",
            },
        }

        self.tokenManager = fileManager(
            workFolder=osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/server"),
            sheets={
                "tokens": (("User", str), ("Token", str), ("Password", bytes), ("Auth", int), ("Roles", list), ("Expires", float), ("Modified", float), ("Active", bool), ("TapoUser", str), ("TapoPassword", bytes), ("Notes", str)),
            },
            modifiedKey="Modified",
            decryptPvk=svPvk,
        )

        if self.tokenManager.count("tokens", True) <= 0:
            for dataIndex in self.defaultTokens:
                self.tokenManager.add("tokens", "-1", "1", [self.defaultTokens[dataIndex][key] for key in self.defaultTokens[dataIndex]])

        self.loadFiles()
        signal(SIGTERM, self.quit)

        self.sesions = {}

        with open(self.findFile("/config.json"), "r", encoding="UTF-8") as fileR:
            fileData = load(fileR)
            self.ip = fileData["IP"]
            self.port = fileData["PORT"]

        self.sslCert = None
        for path in self.sslCertPaths:
            if osPath.exists(f"{path}/fullchain.pem") and osPath.exists(f"{path}/privkey.pem"):
                self.sslCert = SSLContext(PROTOCOL_TLS_SERVER)
                self.sslCert.load_cert_chain(certfile=f"{path}/fullchain.pem", keyfile=f"{path}/privkey.pem")
                break
        if self.sslCert is None:
            self.log(criticality="warning", msg=f'Missing wss certificates! Valid locations: \n    {chr(10) + "    ".join(self.sslCertPaths)}')

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

    def findFile(self, file):
        if not file in self.requiredFiles:
            raise NameError(f"File {file} not found!")

        serverFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "/server")

        if file.split("/")[-1] in listdir(serverFolder):
            return f'{serverFolder}/{file.split("/")[-1]}'
        elif file.split("/")[-1] in listdir(self.workFolder):
            return f'{self.workFolder}/{file.split("/")[-1]}'

        raise NameError(f"File {file} not found!")

    async def getMsg(self, ws, raw: bool = False):
        msg = str(await ws.recv())

        with open(self.findFile("/config.json"), "r", encoding="UTF-8") as fileR:
            if load(fileR)["Debug"]:
                if raw:
                    self.log(criticality="debug", msg=msg)
                else:
                    self.log(criticality="debug", msg=msg.replace("%20", " "))

        if raw:
            return msg

        spliter = " "
        if msg.startswith("<RAW>"):
            msg = msg.replace("<RAW>", "", 1)
            spliter = "<SPLIT>"

        msg, args = (msg.split(spliter), [])
        if len(msg) > 1:
            for arg in msg[1:]:
                args.append(arg.replace("%20", " "))
        msg = msg[0].replace("%20", " ")

        return msg, args

    async def login(self, ws, sId):
        clPuk, clPvk = newkeys(1024)
        await ws.send(f"<LOGIN> {clPuk.save_pkcs1().decode()}")

        triedToken, madeLogin, loginTries = (False, False, 0)
        for i in range(0, 6):
            msg = await self.getMsg(ws, raw=True)

            sleep(int("".join(choices("0123456789", k=2))) / 100)

            if msg.startswith("<LOGIN_TOKEN> ") and not triedToken:
                triedToken = True
                userDataHeader = [pair[0] for pair in self.tokenManager.template()["template"]["sheets"]["tokens"]]
                for dataIndex in range(0, self.tokenManager.count("tokens", True)):
                    userData = self.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
                    if not msg.split("<LOGIN_TOKEN> ")[1] == userData[userDataHeader.index("Token")]:
                        continue
                    break
                else:
                    self.log(criticality="info", msg=f"Token login attempt failed from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                    await ws.send(f"<LOGIN_TOKEN_FAIL>")

                if userData[userDataHeader.index("Expires")] > datetime.now().timestamp() and userData[userDataHeader.index("Active")]:
                    self.log(criticality="info", msg=f'Token login by {userData[userDataHeader.index("User")]} ({userData[userDataHeader.index("Token")][:8]}...)', status="success")
                    return ({**{"sId": sId, "pvk": clPvk}, **{userDataHeader[dataIndex]: value for dataIndex, value in enumerate(userData)}}, f"<LOGIN_TOKEN_SUCCESS>")

                self.log(criticality="info", msg=f"Token login attempt from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                await ws.send(f"<LOGIN_TOKEN_FAIL>")
                continue

            elif msg.startswith("<LOGIN> "):
                loginTries += 1
                if loginTries > 3:
                    self.log(criticality="info", msg=f"Login attempt for {ws.remote_address[0]}:{ws.remote_address[1]}", status="cancelled")
                    await ws.send("<LOGIN_CANCEL>")
                    await ws.close()
                    return (None, None)

                try:
                    password = decrypt(literal_eval(msg.split("<LOGIN> ")[1]), clPvk).decode()
                    user, password = password.split("<SPLIT>")

                    with open(f"{self.workFolder}/server/ssl/pvk.pem", "r", encoding="UTF-8") as fileR:
                        svPvk = PrivateKey.load_pkcs1(fileR.read())

                    userDataHeader = [pair[0] for pair in self.tokenManager.template()["template"]["sheets"]["tokens"]]
                    for dataIndex in range(0, self.tokenManager.count("tokens", True)):
                        userData = self.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
                        if user != userData[userDataHeader.index("User")]:
                            continue
                        if password != decrypt(literal_eval(userData[userDataHeader.index("Password")]), svPvk).decode():
                            continue

                        if not userData[userDataHeader.index("Active")]:
                            self.log(criticality="info", msg=f'User login by {userData[userDataHeader.index("User")]} ({userData[userDataHeader.index("Token")][:8]}...)', status="failed")
                            await ws.send("<LOGIN_FAIL>")
                            break

                        userData[userDataHeader.index("Expires")] = (datetime.now() + timedelta(days=14)).timestamp()
                        self.tokenManager.mod("tokens", dataIndex, "Expires", userData[userDataHeader.index("Expires")])

                        self.log(criticality="info", msg=f'User login by {userData[userDataHeader.index("User")]} ({userData[userDataHeader.index("Token")][:8]}...)', status="success")
                        return ({**{"sId": sId, "pvk": clPvk}, **{userDataHeader[dataIndex]: value for dataIndex, value in enumerate(userData)}}, f'<LOGIN_SUCCESS> {userData[userDataHeader.index("Token")]}')
                    else:
                        self.log(criticality="info", msg=f"Login attempt from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                        await ws.send("<LOGIN_FAIL>")
                        continue

                    continue
                except DecryptionError:
                    pass

                self.log(criticality="info", msg=f"Login attempt from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                await ws.send("<LOGIN_FAIL>")
                continue

            elif msg.startswith("<LOGIN_NEW>") and not madeLogin:
                madeLogin = True
                if not all(item in msg for item in ("<User>", "</User>", "<Password>", "</Password>")):
                    self.log(criticality="info", msg=f"Login creation from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                    await ws.send(f"<LOGIN_NEW_FAIL>")
                    continue

                userDataHeader = [pair[0] for pair in self.tokenManager.template()["template"]["sheets"]["tokens"]]
                user = msg.split("<User>")[1].split("</User>")[0]
                skipAttemt = False
                for dataIndex in range(0, self.tokenManager.count("tokens", True)):
                    userData = self.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
                    if user != userData[userDataHeader.index("User")]:
                        continue

                    self.log(criticality="info", msg=f'Login creation by {userData[userDataHeader.index("User")]} ({userData[userDataHeader.index("Token")][:8]}...)', status="failed")
                    await ws.send(f"<LOGIN_NEW_FAIL>")
                    skipAttemt = True
                    break

                if skipAttemt:
                    continue

                with open(f"{self.workFolder}/server/ssl/pub.pem", "r", encoding="UTF-8") as fileR:
                    svPub = PublicKey.load_pkcs1(fileR.read())

                try:
                    password = decrypt(literal_eval(msg.split("<Password>")[1].split("</Password>")[0]), clPvk).decode()
                    password = encrypt(password.encode(), svPub)
                except SyntaxError:
                    self.log(criticality="info", msg=f"Login creation from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                    await ws.send("<LOGIN_FAIL>")
                    continue

                token = "".join(choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=128))
                allUserData = self.tokenManager.read("tokens")["tokens"]
                while token in tuple(allUserData[dataIndex][userDataHeader.index("Token")] for dataIndex in allUserData):
                    token = "".join(choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=128))

                userData = (str(user), str(token), str(password), 3, [], int((datetime.now() + timedelta(days=14)).timestamp()), int(datetime.now().timestamp()), True, "", "", f"Is {user}")

                self.tokenManager.add("tokens", "-1", "1", userData)

                self.log(criticality="info", msg=f'User created by {userData[userDataHeader.index("User")]} ({userData[userDataHeader.index("Token")][:8]}...)', status="sucess")
                return ({**{"sId": sId, "pvk": clPvk}, **{userDataHeader[dataIndex]: value for dataIndex, value in enumerate(userData)}}, f'<LOGIN_NEW_SUCCES> {userData[userDataHeader.index("Token")]}')

            if i < 5:
                self.log(criticality="info", msg=f"Login attempt from {ws.remote_address[0]}:{ws.remote_address[1]}", status="failed")
                await ws.send("<LOGIN_FAIL>")

        self.log(criticality="info", msg=f"Login attempt from {ws.remote_address[0]}:{ws.remote_address[1]}", status="cancelled")
        await ws.send("<LOGIN_CANCEL>")
        await ws.close()
        return (None, None)

    async def processCom(self, clT, com, args):
        if not com in clT.allCommands:
            clT.log(criticality="low", msg=f'{com} {" ".join(args)}', status="unknown")
            return "unknown"
        criticality = ["high", "high", "medium", "low"][clT.allCommands[com][0]]
        if not com in clT.commands:
            clT.log(criticality=criticality, msg=f'{com} {" ".join(args)}', status="unknown")
            return "unknown"

        if callable(clT.commands[com]):
            clT.log(criticality=criticality, msg=f'{com} {" ".join(args)}', status="executed")
            try:
                return await clT.commands[com](clT, *args[1:])
            except Exception as err:
                clT.log(criticality="error", msg=format_exc())
                return str(err)

        if len(args) < 1:
            clT.log(criticality=criticality, msg=f"{com}", status="missing")
            return "no argument"
        if not args[0].lower() in clT.commands[com]:
            clT.log(criticality=criticality, msg=f'{com} {" ".join(args)}', status="unknown")
            return "unknown argument"

        clT.log(criticality=criticality, msg=f'{com} {" ".join(args)}', status="executed")
        try:
            resp = await clT.commands[com][args[0].lower()](clT, *args[1:])
            if type(resp) is dict:
                return {com.lower(): resp}
            return resp
        except Exception as err:
            clT.log(criticality="error", msg=format_exc())
            return str(err)

    async def serve(self, ws):
        clientIP = ws.remote_address[0]
        clientPort = ws.remote_address[1]
        self.log(criticality="info", msg=f"Client connected from {clientIP}:{clientPort}")
        clT = None

        sId = "".join(choices("0123456789", k=8))
        while sId in self.sesions:
            sId = "".join(choices("0123456789", k=8))
        self.sesions[sId] = None

        try:
            userData, resp = await self.login(ws, sId)
            if userData is None or resp is None:
                return None

            clT = clThread(ws, userData, self)
            self.sesions[sId] = clT
            await ws.send(resp)

            while not self.stop:
                com = None
                while com is None and not self.stop:
                    try:
                        com, args = await wait_for(self.getMsg(ws), timeout=1)
                    except TimeoutError:
                        com = None
                if self.stop:
                    break

                if clT.created < (datetime.now() - timedelta(minutes=15)).timestamp():
                    for dataIndex in range(0, self.tokenManager.count("tokens", True)):
                        userDataHeader = [pair[0] for pair in self.tokenManager.template()["template"]["sheets"]["tokens"]]
                        newUserData = self.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
                        if clT.token == newUserData[userDataHeader.index("Token")]:
                            userData = {**{"sId": clT.sId, "pvk": clT.pvk}, **{userDataHeader[dataIndex]: value for dataIndex, value in enumerate(newUserData)}}
                            break
                    else:
                        clT.log(criticality="error", msg=f"Client authenitcation refresh failed")
                        break

                    clT = clThread(ws, userData, self)
                    self.sesions[sId] = clT

                resp = await self.processCom(clT, com, args)
                if resp is None:
                    continue
                elif type(resp) is dict:
                    resp = dumps(resp)
                else:
                    resp = str(resp)
                    if resp == "<CLOSE>":
                        clT.log(criticality="info", msg=f"User disconnected")
                        break

                await ws.send(resp)

            clT.log(criticality="info", msg=f"Disconnecting")
            await self.sesions[sId].ws.send("<CLOSE>")
            await asyncSleep(3)
            clT.log(criticality="info", msg=f"Closing")
            await self.sesions[sId].ws.close()

        except (ConnectionClosedOK, ConnectionClosedError, ConnectionClosed, ConnectionResetError, ConnectionError) as err:
            if not clT is None:
                clT.log(criticality="info", msg=f"User disconnected")
            else:
                self.log(criticality="info", msg=f"Client disconnected from {clientIP}:{clientPort}")

        self.sesions.pop(sId)

        if self.stop and self.sesions == {}:
            get_event_loop().stop()
            exit()

    def quit(self, *args):
        self.stop = True

    def start(self):
        set_event_loop(new_event_loop())
        get_event_loop().run_until_complete(serve(self.serve, self.ip, self.port, ssl=self.sslCert))
        self.log(criticality="info", msg=f'Started {(lambda: "WS" if self.sslCert is None else "WSS")()} service on {self.ip}:{self.port}')
        get_event_loop().run_forever()
        self.log(criticality="info", msg=f'Stopped {(lambda: "WS" if self.sslCert is None else "WSS")()} service on {self.ip}:{self.port}')

    def main(self):
        try:
            self.start()
        except Exception as err:
            self.log(criticality="error", msg=format_exc())

        self.quit()


class clThread:
    def __init__(self, ws, userData, server):
        self.ws = ws
        self.server = server
        self.token = userData["Token"]
        self.pvk = userData["pvk"]
        self.sId = userData["sId"]
        self.ip = ws.remote_address[0]
        self.port = ws.remote_address[1]
        self.userData = userData
        self.created = datetime.now().timestamp()

        self.log = logger(("clientHandler",), "clientHandler", userData["User"]).log

        coms = srvcoms.get(userData)
        for name in coms:
            setattr(self, name, coms[name])

        self.allCommands = {
            "logout": [3, self.logout],
            "access": [3, self.access],
            "reload": [3, self.reload],
            "restart": [1, self.restart],
            "shutdown": [1, self.shutdown],
            "monitor": [1, self.monitor],
            "admin": [1, self.admin.commands],
            "sonos": [2, self.sonos.commands],
            "tapo": [2, self.tapo.commands],
            "yt": [2, self.ytdl.commands],
            "am": [2, self.asset.commands],
            "lm": [2, self.license.commands],
            "qr": [3, self.query.commands],
        }

        self.commands = {}
        for com in self.allCommands:
            if self.allCommands[com][0] < userData["Auth"]:
                continue
            if callable(self.allCommands[com][1]):
                self.commands[com] = self.allCommands[com][1]
                continue

            for subcom in self.allCommands[com][1]:
                if not self.allCommands[com][1][subcom][0] in userData["Roles"] and not self.allCommands[com][1][subcom][0] is None:
                    continue

                if not com in self.commands:
                    self.commands[com] = {}
                self.commands[com][subcom] = self.allCommands[com][1][subcom][1]

    async def logout(self, args=None):
        await self.ws.send("<CLOSE>")
        sleep(3)
        await self.ws.close()
        return "<CLOSE>"

    async def access(self, args=None):
        access = {}
        for com in self.commands:
            if callable(self.commands[com]):
                access[com] = True
                continue

            access[com] = []
            for subcom in self.commands[com]:
                access[com].append(subcom)

        return {"access": access}

    async def reload(self, args=None):
        for dataIndex in range(0, self.server.tokenManager.count("tokens", True)):
            userDataHeader = [pair[0] for pair in self.server.tokenManager.template()["template"]["sheets"]["tokens"]]
            newUserData = self.server.tokenManager.read("tokens", dataIndex)["tokens"][str(dataIndex)]
            if self.token == newUserData[userDataHeader.index("Token")]:
                userData = {**{"sId": self.sId, "pvk": self.pvk}, **{userDataHeader[dataIndex]: value for dataIndex, value in enumerate(newUserData)}}
                break
        else:
            return f'Client authenitcation refresh failed for {self.userData["User"]}'

        self.token = userData["Token"]
        self.pvk = userData["pvk"]
        self.sId = userData["sId"]
        self.ip = self.ws.remote_address[0]
        self.port = self.ws.remote_address[1]
        self.userData = userData
        self.created = datetime.now().timestamp()

        if not args is None and args[0].lower() == "full":
            coms = srvcoms.get(userData)
            for name in coms:
                setattr(self, name, coms[name])

        self.allCommands = {
            "logout": [3, self.logout],
            "access": [3, self.access],
            "reload": [3, self.reload],
            "restart": [1, self.restart],
            "shutdown": [1, self.shutdown],
            "monitor": [1, self.monitor],
            "admin": [1, self.admin.commands],
            "sonos": [2, self.sonos.commands],
            "tapo": [2, self.tapo.commands],
            "yt": [2, self.ytdl.commands],
            "am": [2, self.asset.commands],
            "lm": [2, self.license.commands],
            "qr": [3, self.query.commands],
        }

        self.commands = {}
        for com in self.allCommands:
            if self.allCommands[com][0] < self.userData["Auth"]:
                continue
            if callable(self.allCommands[com][1]):
                self.commands[com] = self.allCommands[com][1]
                continue

            for subcom in self.allCommands[com][1]:
                if not self.allCommands[com][1][subcom][0] in self.userData["Roles"] and not self.allCommands[com][1][subcom][0] is None:
                    continue

                if not com in self.commands:
                    self.commands[com] = {}
                self.commands[com][subcom] = self.allCommands[com][1][subcom][1]

        return await self.access(self)

    async def restart(self, args=None):
        workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "")
        with open(f"{workFolder}/server/commandStack.txt", "a" if osPath.exists(f"{workFolder}/server/commandStack.txt") else "w", encoding="UTF-8") as fileA:
            fileA.write("\nrestart")

    async def shutdown(self, args=None):
        workFolder = osPath.split(__file__)[0].replace("\\", "/").replace("/lib/sub", "")
        with open(f"{workFolder}/server/commandStack.txt", "a" if osPath.exists(f"{workFolder}/server/commandStack.txt") else "w", encoding="UTF-8") as fileA:
            fileA.write("\nexit")

    async def monitor(self, args=None):
        def sanetize(obj):
            if isinstance(obj, dict):
                return {k: sanetize(v) for k, v in obj.items() if k not in {"Password", "TapoPassword", "sId", "pvk"}}

            if isinstance(obj, list):
                return [sanetize(v) for v in obj]

            return obj

        allUserData = {}
        for sId in self.server.sesions:
            if self.server.sesions[sId] is None:
                allUserData[sId] = None
                continue
            allUserData[sId] = sanetize(self.server.sesions[sId].userData)

        return {"monitor": {"Current": {self.sId: sanetize(self.userData)}, "All": allUserData}}


if __name__ == "__main__":
    clientHandler().start()
