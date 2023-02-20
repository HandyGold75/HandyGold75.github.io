import mod.HTML as HTML
from json import loads
from js import eval, window, console


class glb:
    PROTO = ""
    IP = ""
    PORT = ""

    ws = None

    msgReply = {}
    lastMsg = ""
    msgDict = {}

    reconnectTries = 0
    afterReconnect = []


class ws:
    def close(arg=None):
        glb.ws.close()

    fmap = {"<LOGIN_CANCEL>": close, "<LOGOUT>": close}

    def onOpen(arg=None):
        glb.reconnectTries = 0

    def onMessage(arg):
        msg = arg.data
        glb.lastMsg = msg

        if msg.startswith("{") and msg.endswith("}"):
            data = loads(msg)

            for dict in data:
                if not dict in glb.msgDict:
                    glb.msgDict[dict] = {}

                glb.msgDict[dict] = {**glb.msgDict[dict], **data[dict]}

        elif msg.split(f' ')[0] in glb.msgReply:
            msg = msg.split(f' ')[0]

            if callable(glb.msgReply[msg]):
                glb.msgReply[msg]()
                return None

            glb.ws.send(glb.msgReply[msg])

        elif msg in ws.fmap:
            ws.fmap[msg.split(">")[0] + ">"](msg.split(">")[1])

    def onError(arg):
        console.error(arg)
        glb.ws.close()

    def onClose(arg=None):
        ws.connectionError("The connection to the server was lost!")

    def upState():
        if glb.ws.readyState in [0, 1]:
            return True

        elif glb.ws.readyState in [2, 3]:
            return False

    def connectionError(msg: str):
        def loginTokenSucces():
            glb.ws.send(f'access')

            for msg in glb.afterReconnect:
                glb.ws.send(msg)

            glb.afterReconnect = []

        def loginTokenFail():
            glb.reconnectTries = 99
            ws.connectionError("Unable to reconnect to the server, token authetication failed!")

        if window.localStorage.getItem("token") == "" or glb.reconnectTries > 4:
            HTML.enable("page_Portal", False)

            HTML.set(f'div', f'page', _id=f'page_error', _align=f'center')
            HTML.set(f'h1', f'page_error', _nest=f'WARNING!', _style=f'headerVeryBig')
            HTML.add(f'p', f'page_error', _nest=f'Connection lost to the server! {msg}')
            HTML.add(f'p', f'page_error', _nest=f'Please refresh the page to try again.')

            return None

        glb.ws = None
        glb.reconnectTries += 1

        onMsg(f'<LOGIN>', f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')
        onMsg(f'<LOGIN_TOKEN_SUCCESS>', loginTokenSucces)
        onMsg(f'<LOGIN_TOKEN_FAIL>', loginTokenFail)

        start(glb.PROTO, glb.IP, glb.PORT)


def start(protocol: str, ip: str, port: str):
    if not glb.ws is None:
        glb.ws.close()
        glb.ws = None

    glb.PROTO = str(protocol)[:3]
    glb.IP = str(ip[:32])
    glb.PORT = str(port)[:5]

    glb.ws = eval(f'new WebSocket("{glb.PROTO}://{glb.IP}:{glb.PORT}")')

    glb.ws.onopen = ws.onOpen
    glb.ws.onmessage = ws.onMessage
    glb.ws.onerror = ws.onError
    glb.ws.onclose = ws.onClose


def send(com: str):
    if glb.ws.readyState != 1:
        glb.afterReconnect.append(com)

        if glb.ws.readyState != 0:
            ws.close()

        return None

    glb.ws.send(com)


def msg():
    if not glb.ws.readyState in [0, 1]:
        ws.close()

    return glb.lastMsg


def msgDict():
    if not glb.ws.readyState in [0, 1]:
        ws.close()

    return glb.msgDict


def onMsg(msgRecv: str, msgOrFunc: msg):
    glb.msgReply[msgRecv] = msgOrFunc
