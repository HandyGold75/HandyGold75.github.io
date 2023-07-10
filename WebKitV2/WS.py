from js import window, eval, console
from rsa import PublicKey
from json import loads
from copy import deepcopy


class WS:
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

        self.loggedIn = False
        self.reconnectTries = 0
        self.afterReconnect = []

    def onOpen(self, args=None):
        self.reconnectTries

    def onMessage(self, args):
        msg = args.data
        self.lastMsg = msg

        if msg.startswith("{") and msg.endswith("}"):
            data = loads(msg)

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

        msgOrFunc = self.msgReply[msg][0]
        if self.msgReply[msg][1]:
            self.msgReply.pop(msg)

        if callable(msgOrFunc):
            msgOrFunc()
        else:
            self.ws.send(msgOrFunc)

    def onError(self, args):
        console.error(args)
        self.close()

    def loginTokenSucces(self):
        self.ws.send("access")

        for msg in afterReconnect:
            self.ws.send(msg)

        afterReconnect = []

    def loginTokenFail(self):
        window.localStorage.setItem("token", "")
        self.reconnectTries = 99
        self.onClose(msg="Unable to reconnect to the server, token authetication failed!")

    def onClose(self, args=None, msg: str = "The connection to the server was lost!"):
        if not self.loggedIn:
            return None

        if window.localStorage.getItem("token") == "" or self.reconnectTries > 4:
            from WebKit.Widget import raiseError
            raiseError("WARNING!", f'Connection lost to the server!\n{msg}\nPlease refresh the page to try again.', ("page_Portal", ))
            return None

        self.ws = None
        self.pub = None
        self.reconnectTries += 1

        self.onMsg("<LOGIN_TOKEN_SUCCESS>", self.loginTokenSucces, oneTime=True)
        self.onMsg("<LOGIN_TOKEN_FAIL>", self.loginTokenFail, oneTime=True)

        self.start(self.protocol, self.ip, self.port)

    def onLogin(self, args=None):
        if not self.msg().startswith("<LOGIN> "):
            return None

        self.pub = PublicKey.load_pkcs1(self.msg().split("<LOGIN> ")[1])

        if window.localStorage.getItem("token") == "" or self.reconnectTries > 4:
            return None

        self.ws.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')

    def start(self, protocol: str, ip: str, port: str):
        if not self.ws is None:
            self.close()
            self.ws = None
            self.pub = None

        self.protocol = str(protocol)[:3]
        self.ip = str(ip[:32])
        self.port = str(port)[:5]
        self.ws = eval(f'new WebSocket("{self.protocol}://{self.ip}:{self.port}")')

        self.ws.onopen = self.onOpen
        self.ws.onmessage = self.onMessage
        self.ws.onerror = self.onError
        self.ws.onclose = self.onClose

        self.onMsg("<LOGIN>", self.onLogin, oneTime=True)
        self.onMsg("<LOGIN_CANCEL>", self.close, oneTime=True)
        self.onMsg("<CLOSE>", self.close, oneTime=True)

    def close(self):
        self.ws.close()

    def state(self):
        if self.ws.readyState in [0, 1]:
            return True
        return False

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

    def onMsg(self, msgRecv: str, msgOrFunc: str, oneTime: bool = False):
        self.msgReply[msgRecv] = (msgOrFunc, oneTime)
