from json import loads
from js import eval, console


class glb:
    PROTO = ""
    IP = ""
    PORT = ""
    ws = None
    msgReply = {}
    lastMsg = ""
    msgDict = {}


class ws:
    def close(arg=None):
        glb.ws.close()

    fmap = {"<LOGIN_CANCEL>": close, "<LOGOUT>": close}

    def onOpen(arg=None):
        pass

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

    def onClose(arg=None):
        pass

    def upState():
        if glb.ws.readyState in [0, 1]:
            return True

        elif glb.ws.readyState in [2, 3]:
            return False


def start(protocol: str, ip: str, port: str):
    if not glb.ws is None:
        return None

    glb.PROTO = str(protocol)[:3]
    glb.IP = str(ip[:32])
    glb.PORT = str(port)[:5]

    glb.ws = eval(f'new WebSocket("{glb.PROTO}://{glb.IP}:{glb.PORT}")')

    glb.ws.onopen = ws.onOpen
    glb.ws.onmessage = ws.onMessage
    glb.ws.onerror = ws.onError
    glb.ws.onclose = ws.onClose


def send(com: str):
    if not ws.upState():
        raise ConnectionError(f"Unable to verify healty connection!")

    glb.ws.send(com)


def msg():
    if not ws.upState():
        raise ConnectionError(f"Unable to verify healty connection!")

    return glb.lastMsg


def msgDict():
    if not ws.upState():
        raise ConnectionError(f"Unable to verify healty connection!")

    return glb.msgDict


def onMsg(msgRecv: str, msgOrFunc: msg):
    glb.msgReply[msgRecv] = msgOrFunc
