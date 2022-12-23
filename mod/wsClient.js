async function CLOSE(args) {
    obj.ws.close()
};

async function NEWMESSAGE(data) {
    console.log("Got msg: " + data)
    if (data.startsWith("{") && data.endsWith("}")) {
        obj.msgDict = { ...obj.msgDict, ...JSON.parse(data) }
    }

    obj.lastMsg = data;

    arg = data.split("> ")[1]
    data = data.split(">")[0] + ">"

    if (data in obj.fmap) {
        obj.fmap[data](arg)
    }
};

class obj {
    ws;
    IP;
    PORT;
    lastCom;
    lastMsg;
    msgDict;
    fmap;
};

function wsStart() {
    if (obj.ws === undefined) {
        obj.ws = null;
        obj.IP = "wss.HandyGold75.ga";
        // obj.IP = "127.0.0.1";
        obj.PORT = 6900;
        obj.lastCom = "";
        obj.lastMsg = "";
        obj.msgDict = {};
        obj.fmap = {
            "<LOGIN_CANCEL>": CLOSE,
            "<LOGOUT>": CLOSE,
            "<SHUTDOWN>": CLOSE
        };

        obj.ws = new WebSocket("wss://" + obj.IP + ":" + obj.PORT);
        // obj.ws = new WebSocket("ws://" + obj.IP + ":" + obj.PORT);

        obj.ws.onopen = (event) => {
            console.log("Opened connection to wss://" + obj.IP + ":" + obj.PORT)
            // console.log("Opened connection to ws://" + obj.IP + ":" + obj.PORT)
        };

        obj.ws.onmessage = (event) => {
            NEWMESSAGE(event.data)
        }
    }
};

function wsUpState() {
    if (obj.ws.readyState === 0 || obj.ws.readyState === 1) {
        return true
    }

    else if (obj.ws.readyState === 2 || obj.ws.readyState === 3) {
        return false
    }
};

function wsSend(com) {
    obj.lastCom = com;
    obj.ws.send(com);

    return obj.lastCom
};

function wsMsg() {
    return obj.lastMsg
};

function wsMsgDict() {
    return JSON.stringify(obj.msgDict)
}
