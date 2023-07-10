from js import window, eval, console
from rsa import PublicKey
from json import loads
from copy import deepcopy
from WebKit.Widget import raiseError

__all__ = ["start", "close", "state", "send", "msg", "dict", "onMsg"]


class glb:
    protocol = ""
    ip = ""
    port = ""

    ws = None
    pub = None

    msgReply = {}
    lastMsg = ""
    msgDict = {}

    loggedIn = False
    reconnectTries = 0
    afterReconnect = []


def onOpen(args=None):
    glb.reconnectTries


def onMessage(args):
    msg = args.data
    glb.lastMsg = msg

    if msg.startswith("{") and msg.endswith("}"):
        data = loads(msg)

        for dict in data:
            if not dict in glb.msgDict:
                glb.msgDict[dict] = {}

            glb.msgDict[dict] = {**glb.msgDict[dict], **data[dict]}

    if msg.split(" ")[0] in glb.msgReply:
        msg = msg.split(" ")[0]
    elif " ".join(msg.split(" ")[:2]) in glb.msgReply:
        msg = " ".join(msg.split(" ")[:2])
    else:
        return None

    msgOrFunc = glb.msgReply[msg][0]
    if glb.msgReply[msg][1]:
        glb.msgReply.pop(msg)

    if callable(msgOrFunc):
        msgOrFunc()
    else:
        glb.ws.send(msgOrFunc)


def onError(args):
    console.error(args)
    close()


def loginTokenSucces():
    glb.ws.send("access")

    for msg in glb.afterReconnect:
        glb.ws.send(msg)

    glb.afterReconnect = []


def loginTokenFail():
    window.localStorage.setItem("token", "")
    glb.reconnectTries = 99
    onClose(msg="Unable to reconnect to the server, token authetication failed!")


def onClose(args=None, msg: str = "The connection to the server was lost!"):
    if not glb.loggedIn:
        return None

    if window.localStorage.getItem("token") == "" or glb.reconnectTries > 4:
        raiseError("WARNING!", f'Connection lost to the server!\n{msg}\nPlease refresh the page to try again.', ("page_Portal", ))
        return None

    glb.ws = None
    glb.pub = None
    glb.reconnectTries += 1

    onMsg("<LOGIN_TOKEN_SUCCESS>", loginTokenSucces, oneTime=True)
    onMsg("<LOGIN_TOKEN_FAIL>", loginTokenFail, oneTime=True)

    start(glb.protocol, glb.ip, glb.port)


def onLogin(args=None):
    if not msg().startswith("<LOGIN> "):
        return None

    glb.pub = PublicKey.load_pkcs1(msg().split("<LOGIN> ")[1])

    if window.localStorage.getItem("token") == "" or glb.reconnectTries > 4:
        return None

    glb.ws.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')


def start(protocol: str, ip: str, port: str):
    if not glb.ws is None:
        close()
        glb.ws = None
        glb.pub = None

    glb.protocol = str(protocol)[:3]
    glb.ip = str(ip[:32])
    glb.port = str(port)[:5]
    glb.ws = eval(f'new WebSocket("{glb.protocol}://{glb.ip}:{glb.port}")')

    glb.ws.onopen = onOpen
    glb.ws.onmessage = onMessage
    glb.ws.onerror = onError
    glb.ws.onclose = onClose

    onMsg("<LOGIN>", onLogin, oneTime=True)
    onMsg("<LOGIN_CANCEL>", close, oneTime=True)
    onMsg("<CLOSE>", close, oneTime=True)


def close():
    glb.ws.close()


def state():
    if glb.ws.readyState in [0, 1]:
        return True
    return False


def send(com: str):
    if glb.ws.readyState != 1:
        glb.afterReconnect.append(com)

        if glb.ws.readyState != 0:
            close()

        return None

    glb.ws.send(com)


def msg():
    if not glb.ws.readyState in [0, 1]:
        close()
    return glb.lastMsg


def dict():
    if not glb.ws.readyState in [0, 1]:
        close()
    return deepcopy(glb.msgDict)


def onMsg(msgRecv: str, msgOrFunc: str, oneTime: bool = False):
    glb.msgReply[msgRecv] = (msgOrFunc, oneTime)
