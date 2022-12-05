async function LOGIN_SAVE(arg) {
    obj.AUTHTOKEN = arg
};

async function CLOSE(args) {
    obj.ws.close()
};

async function NEWMESSAGE(data) {
    // console.log("Got msg: " + data)
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
    AUTHTOKEN;
    lastCom;
    lastMsg;
    msgDict;
    fmap;
};

function wsStart() {
    if (obj.ws === undefined) {
        obj.ws = null;
        // obj.IP = "139.162.141.79";
        obj.IP = "127.0.0.1";
        obj.PORT = 6900;
        obj.AUTHTOKEN = "89UibZOFCKmPObSBnBxSNcorbp4eUYAKPX5V5qepEYw7tVwO0nZ3wwXGK48VXBjc";
        obj.lastCom = "";
        obj.lastMsg = "";
        obj.msgDict = {};
        obj.fmap = {
            // "<LOGIN_SUCCESS>": LOGIN_SAVE,
            "<LOGIN_CANCEL>": CLOSE,
            "<LOGOUT>": CLOSE,
            "<SHUTDOWN>": CLOSE
        };

        obj.ws = new WebSocket("ws://" + obj.IP + ":" + obj.PORT);

        obj.ws.onopen = (event) => {
            console.log("Opened connection to ws://" + obj.IP + ":" + obj.PORT)
        };


        obj.ws.onmessage = (event) => {
            // console.log(event);
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
