from js import document, window, eval, console
from rsa import PublicKey
from json import loads, dumps, JSONDecodeError
from copy import deepcopy
from traceback import format_exc


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

        self.loggedIn = False
        self.reconnectTries = 0
        self.afterReconnect = []

        self.indexLogout = None

        if window.localStorage.getItem("configWS") is None:
            window.localStorage.setItem("configWS", dumps({"server": "WSS://wss.HandyGold75.com:17500", "autoSignIn": False, "token": ""}))

        self.config = loads(window.localStorage.getItem("configWS"))
        if not self.config["autoSignIn"]:
            self.config["token"] = ""
            window.localStorage.setItem("configWS", dumps(self.config))

    def indexLogoutHook(self, function):
        self.indexLogout = function

    def onOpen(self, args=None):
        self.onMsg("<LOGIN>", self.onLogin, oneTime=True)
        self.onMsg("<LOGIN_CANCEL>", self.close, oneTime=True)
        self.onMsg("<CLOSE>", self.close, oneTime=True)

        self.onMsg("<LOGIN_SUCCESS>", self.onLoginSucces, oneTime=True)
        self.onMsg("<LOGIN_FAIL>", self.onLoginFail, oneTime=True)

        if self.config["token"] != "":
            self.onMsg("<LOGIN_TOKEN_SUCCESS>", self.onLoginTokenSucces, oneTime=True)
            self.onMsg("<LOGIN_TOKEN_FAIL>", self.onLoginTokenFail, oneTime=True)

    def onMessage(self, args):
        msg = args.data
        self.lastMsg = msg

        if msg.startswith("{") and msg.endswith("}"):
            try:
                data = loads(msg)
            except JSONDecodeError:
                console.log(f'Error:\n{format_exc()}')
                console.log(f'Message:\n{msg}')

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
        console.error(args)
        self.close()

    def onClose(self, args=None, msg: str = "The connection to the server was lost!"):
        if not self.loggedIn:
            return None
        self.loggedIn = False

        if self.config["token"] == "" or self.reconnectTries > 4:
            from WebKit.Widget import raiseError
            raiseError("WARNING!", f'Connection lost to the server!\n{msg}\nPlease refresh the page to try again.', ("page_Portal", ))
            return None

        self.ws = None
        self.pub = None
        self.reconnectTries += 1

        self.afterReconnect.append("access")
        self.start(self.protocol, self.ip, self.port)

    def onLogin(self, args=None):
        if not self.msg().startswith("<LOGIN> "):
            return None

        self.pub = PublicKey.load_pkcs1(self.msg().split("<LOGIN> ")[1])

        if self.config["token"] == "" or self.reconnectTries > 4 or not self.config["autoSignIn"]:
            self.raiseOnLoginUpdate("loginTokenNotFound")
            return None

        self.ws.send(f'<LOGIN_TOKEN> {self.config["token"]}')
        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenWasSend")

    def onLoginTokenSucces(self):
        self.loggedIn = True

        for msg in self.afterReconnect:
            self.ws.send(msg)
        self.afterReconnect = []

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenSucces")
            self.raiseOnLoginUpdate = None

    def onLoginTokenFail(self):
        self.loggedIn = False
        self.config["token"] = ""
        window.localStorage.setItem("configWS", dumps(self.config))
        self.reconnectTries = 99
        self.onClose(msg="Unable to connect to the server, token authetication failed!")

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginTokenFail")

    def onLoginSucces(self):
        if self.msg().startswith("<LOGIN_SUCCESS> "):
            self.config["token"] = f'{self.msg().split("<LOGIN_SUCCESS> ")[1]}'
            window.localStorage.setItem("configWS", dumps(self.config))

        self.loggedIn = True

        for msg in self.afterReconnect:
            self.ws.send(msg)
        self.afterReconnect = []

        if callable(self.raiseOnLoginUpdate):
            self.raiseOnLoginUpdate("loginSucces")
            self.raiseOnLoginUpdate = None

    def onLoginFail(self):
        self.loggedIn = False
        self.config["token"] = ""
        window.localStorage.setItem("configWS", dumps(self.config))

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
        self.ws = eval(f'new WebSocket("{self.protocol}://{self.ip}:{self.port}")')

        self.ws.onopen = self.onOpen
        self.ws.onmessage = self.onMessage
        self.ws.onerror = self.onError
        self.ws.onclose = self.onClose

    def close(self):
        self.loggedIn = False
        self.ws.close()

    def logout(self):
        if not window.confirm("Log off?"):
            return None

        if self.ws.readyState == 1:
            self.ws.send("logout")

        self.config["token"] = ""
        window.localStorage.setItem("configWS", dumps(self.config))
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
                self.close()

            return None

        self.ws.send(com)

    def msg(self):
        if not self.ws.readyState in [0, 1]:
            self.close()
        return self.lastMsg

    def dict(self):
        if not self.ws.readyState in [0, 1]:
            self.close()
        return deepcopy(self.msgDict)

    def onMsg(self, msgRecv: str, msgOrFunc: str, args: tuple = (), kwargs: dict = {}, oneTime: bool = False):
        self.msgReply[msgRecv] = (oneTime, msgOrFunc, args, kwargs)