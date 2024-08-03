from copy import deepcopy
from json import JSONDecodeError, dumps, loads
from traceback import format_exc

from js import console, eval, window  # type: ignore
from rsa import PublicKey


class WebSocket:
    __all__ = ["start", "close", "state", "send", "msg", "dict", "onMsg"]

    def __init__(self):
        self.protocol = ""
        self.ip = ""
        self.port = ""

        self.ws = None
        self.pub = None

        self.msgReply = {}
        self.lastMsg = ""
        self.msgDict = {}
        self.raiseOnLoginUpdate = None
        self.raiseOnMsg = None

        self.loggedIn = False
        self.reconnectTries = 0
        self.maxReconnectTries = 3
        self.afterReconnect = []

        self.indexLogout = None

        if window.localStorage.getItem("python/configWS") is None:
            window.localStorage.setItem("python/configWS", dumps({"server": "WSS://wss.HandyGold75.com:17510", "autoSignIn": False, "token": ""}))

        self.config = loads(window.localStorage.getItem("python/configWS"))
        if not self.config["autoSignIn"]:
            self.config["token"] = ""
            window.localStorage.setItem("python/configWS", dumps(self.config))

    def indexLogoutHook(self, function):
        self.indexLogout = function

    def onOpen(self, args=None):
        self.onMsg("<LOGIN>", self.onLogin, oneTime=True)
        self.onMsg("<LOGIN_CANCEL>", lambda: self.close("Login was canceled!"), oneTime=True)
        self.onMsg("<CLOSE>", lambda: self.close("The server closed the connection!"), oneTime=True)

        self.onMsg("<LOGIN_SUCCESS>", self.onLoginSucces, oneTime=True)
        self.onMsg("<LOGIN_FAIL>", self.onLoginFail, oneTime=True)

        if self.config["token"] != "":
            self.onMsg("<LOGIN_TOKEN_SUCCESS>", self.onLoginTokenSucces, oneTime=True)
            self.onMsg("<LOGIN_TOKEN_FAIL>", self.onLoginTokenFail, oneTime=True)

    def onMessage(self, args):
        msg = args.data
        self.lastMsg = msg

        if callable(self.raiseOnMsg):
            self.raiseOnMsg(msg)

        if msg.startswith("{") and msg.endswith("}"):
            try:
                data = loads(msg)
            except JSONDecodeError:
                console.log(f"Error:\n{format_exc()}")
                console.log(f"Message:\n{msg}")

            for dict in data:
                if not dict in self.msgDict:
                    self.msgDict[dict] = {}

                self.msgDict[dict] = {**self.msgDict[dict], **data[dict]}

        if msg.split(" ")[0] in self.msgReply:
            msg = msg.split(" ")[0]
        elif " ".join(msg.split(" ")[:2]) in self.msgReply:
            msg = " ".join(msg.split(" ")[:2])
        else:
            return None

        msgOrFunc, funcArgs, funcKwargs = self.msgReply[msg][1:]
        if self.msgReply[msg][0]:
            self.msgReply.pop(msg)

        if callable(msgOrFunc):
            msgOrFunc(*funcArgs, **funcKwargs)
        else:
            self.ws.send(msgOrFunc)

    def onError(self, args):
        if self.config["token"] == "" or self.reconnectTries >= self.maxReconnectTries:
            from WebKit.Widget import raiseError

            raiseError("Error", f"Connection lost to the server!\nServer is unavailable!\nPlease refresh the page to try again.", ("subPageButton_Portal", "subPageButton_Console"))
            return None

        self.start(self.protocol, self.ip, self.port)

    def onClose(self, args=None, msg: str = "The connection to the server was lost!"):
        if not self.loggedIn:
            return None

        if self.config["token"] == "" or self.reconnectTries >= self.maxReconnectTries:
            from WebKit.Widget import raiseError

            raiseError("Error", f"Connection lost to the server!\n{msg}\nPlease refresh the page to try again.", ("subPageButton_Portal", "subPageButton_Console"))
            return None

        self.afterReconnect.append("access")
        self.start(self.protocol, self.ip, self.port)

    def onLogin(self, args=None):
        if not self.msg().startswith("<LOGIN> "):
            return None

        self.pub = PublicKey.load_pkcs1(self.msg().split("<LOGIN> ")[1])

        if self.config["token"] == "" or self.reconnectTries >= self.maxReconnectTries or not self.config["autoSignIn"]:
            self.raiseOnLoginUpdate("loginTokenNotFound")
            return None

        self.ws.send(f'<LOGIN_TOKEN> {self.config["token"]}')
        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenWasSend")

    def onLoginTokenSucces(self):
        self.loggedIn = True
        self.reconnectTries = 0

        for msg in self.afterReconnect:
            self.ws.send(msg)
        self.afterReconnect = []

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenSucces")
            self.raiseOnLoginUpdate = None

    def onLoginTokenFail(self):
        self.loggedIn = False
        self.config["token"] = ""
        window.localStorage.setItem("python/configWS", dumps(self.config))
        self.reconnectTries = 99
        self.onClose(msg="Unable to connect to the server, token authetication failed!")

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenFail")

    def onLoginSucces(self):
        if self.msg().startswith("<LOGIN_SUCCESS> "):
            self.config["token"] = f'{self.msg().split("<LOGIN_SUCCESS> ")[1]}'
            window.localStorage.setItem("python/configWS", dumps(self.config))

        self.loggedIn = True
        self.reconnectTries = 0

        for msg in self.afterReconnect:
            self.ws.send(msg)
        self.afterReconnect = []

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginSucces")
            self.raiseOnLoginUpdate = None

    def onLoginFail(self):
        self.loggedIn = False
        self.config["token"] = ""
        window.localStorage.setItem("python/configWS", dumps(self.config))

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginFail")

    def start(self, protocol: str, ip: str, port: str, raiseOnLoginUpdate: object = None):
        if not self.ws is None:
            self.close()
            self.ws = None
            self.pub = None
            self.loggedIn = False

        self.raiseOnLoginUpdate = raiseOnLoginUpdate

        self.protocol = str(protocol)[:3]
        self.ip = str(ip[:32])
        self.port = str(port)[:5]

        if self.reconnectTries >= self.maxReconnectTries:
            from WebKit.Widget import raiseError

            raiseError("Error", f"Connection lost to the server!\nServer is unavailable!\nPlease refresh the page to try again.", ("subPageButton_Portal", "subPageButton_Console"))
            return None
        self.reconnectTries += 1
        self.ws = eval(f'new WebSocket("{self.protocol}://{self.ip}:{self.port}")')

        self.ws.onopen = self.onOpen
        self.ws.onmessage = self.onMessage
        self.ws.onerror = self.onError
        self.ws.onclose = self.onClose

    def close(self, msg: str = None):
        self.loggedIn = False
        self.ws.close()

        if not msg is None:
            from WebKit.Widget import raiseError

            raiseError("Error", f"Connection lost to the server!\n{msg}\nPlease renavigate to the page to try again.")

    def logout(self):
        if not window.confirm("Log off?"):
            return None

        if self.ws.readyState == 1:
            self.ws.send("logout")

        self.config["token"] = ""
        window.localStorage.setItem("python/configWS", dumps(self.config))
        self.loggedIn = False
        self.ws.close()

        if self.indexLogout is None:
            window.location.reload()
        self.indexLogout()

    def state(self):
        if self.ws is None:
            return -1

        return self.ws.readyState

    def loginState(self):
        return self.loggedIn

    def send(self, com: str):
        if self.ws.readyState != 1:
            self.afterReconnect.append(com)

            if self.ws.readyState != 0:
                self.close("The connection to the server was closed!")

            return None

        self.ws.send(com)

    def msg(self):
        if not self.ws.readyState in [0, 1]:
            self.close("The connection to the server was closed!")
        return self.lastMsg

    def dict(self):
        if not self.ws.readyState in [0, 1]:
            self.close("The connection to the server was closed!")
        return deepcopy(self.msgDict)

    def onMsg(self, msgRecv: str, msgOrFunc: str, args: tuple = (), kwargs: dict = {}, oneTime: bool = False):
        self.msgReply[msgRecv] = (oneTime, msgOrFunc, args, kwargs)
