from js import document, window, eval, setTimeout, setInterval, console
from pyodide.ffi import create_proxy, create_once_callable # type: ignore
from rsa import PublicKey
from json import loads
from datetime import datetime
from copy import deepcopy
from rsa import encrypt


class CSS:
    styleMap = {
        "buttonHover": "z-index: 101; color: #FFF; background: #444; transition: 0.25s",
        "buttonClick": "z-index: 102; color: #55F; background: #BBF; transition: 0.1s",
        "inputHover": "z-index: 111; color: #FFF; background: #444; transition: 0.25s",
        "inputFocus": "z-index: 112; color: #FFF; background: #444; transition: 0.1s",
        "selectHover": "z-index: 121; margin-bottom: -100px; min-height: 100px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.25s",
        "selectFocus": "z-index: 122; margin-bottom: -100px; min-height: 100px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.1s",
        "imgHover": "z-index: 101; color: #FFF; background: #444; border: 3px solid #FBDF56; transition: 0.25s",
        "imgClick": "z-index: 102; color: #55F; background: #550; border: 3px solid #FBDF56; transition: 0.1s",
        "disabled": "color: #88B; background: #222"
    }
    onHoverStyles = {}
    onClickStyles = {}
    onFocusStyles = {}

    get = lambda id, key: getattr(document.getElementById(id), key)
    set = lambda id, key, value: setattr(document.getElementById(id), key, value)
    getStyle = lambda id, key: getattr(document.getElementById(id).style, key)
    setStyle = lambda id, key, value: setattr(document.getElementById(id).style, key, value)
    onHoverClick = lambda id, styleHover, styleClick: (CSS.onHover(id, styleHover), CSS.onClick(id, styleClick))
    onHoverFocus = lambda id, styleHover, styleClick: (CSS.onHover(id, styleHover), CSS.onFocus(id, styleClick))

    def sets(id: str, keyValue: tuple):
        for key, value in keyValue:
            setattr(document.getElementById(id), key, value)

    def setStyles(id: str, keyValue: tuple):
        for key, value in keyValue:
            setattr(document.getElementById(id).style, key, value)

    def onHover(id: str, style: str):
        def mouseover(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_mouseover' in CSS.onHoverStyles:
                    el = el.parentElement
                    continue
                break

            for prop in CSS.onHoverStyles[f'{el.id}_mouseover']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseout(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_mouseout' in CSS.onHoverStyles:
                    el = el.parentElement
                    continue
                break

            if document.getElementById(el.id).tagName != "BUTTON" and document.activeElement == args.target:
                return None

            for prop in CSS.onHoverStyles[f'{el.id}_mouseout']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onHoverStyles[f'{id}_mouseover'] = []
        CSS.onHoverStyles[f'{id}_mouseout'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(" %% ")

            for styleKey in styleTmp:
                if not styleKey in CSS.styleMap:
                    continue

                for subStyle in CSS.styleMap[styleKey].split(";"):
                    subStyleKey, subStyleValue = subStyle.split(":")
                    subStyleKey = subStyleKey.replace(" ", "")

                    if subStyleKey in subStyleMerged or subStyleKey in style:
                        continue

                    subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

                style = style.replace(styleKey, "")

            style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

        for prop in style.split(";")[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == "transition":
                el.style.transition = f'{prop.split(": ")[1]}'
                continue

            CSS.onHoverStyles[f'{id}_mouseout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onHoverStyles[f'{id}_mouseover'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener("mouseover", create_proxy(mouseover))
        el.addEventListener("mouseout", create_proxy(mouseout))

    def onClick(id: str, style: str):
        def mousedown(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_mousedown' in CSS.onClickStyles:
                    el = el.parentElement
                    continue
                break

            for prop in CSS.onClickStyles[f'{el.id}_mousedown']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseup(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_mouseup' in CSS.onClickStyles:
                    el = el.parentElement
                    continue
                break

            for prop in CSS.onClickStyles[f'{el.id}_mouseup']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onClickStyles[f'{id}_mousedown'] = []
        CSS.onClickStyles[f'{id}_mouseup'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(" %% ")

            for styleKey in styleTmp:
                if not styleKey in CSS.styleMap:
                    continue

                for subStyle in CSS.styleMap[styleKey].split(";"):
                    subStyleKey, subStyleValue = subStyle.split(":")
                    subStyleKey = subStyleKey.replace(" ", "")

                    if subStyleKey in subStyleMerged or subStyleKey in style:
                        continue

                    subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

                style = style.replace(styleKey, "")

            style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

        for prop in style.split(";")[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == "transition":
                el.style.transition = prop.split(": ")[1]
                continue

            CSS.onClickStyles[f'{id}_mouseup'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onClickStyles[f'{id}_mousedown'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener("mousedown", create_proxy(mousedown))
        el.addEventListener("mouseup", create_proxy(mouseup))

    def onFocus(id: str, style: str):
        def focusin(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_focusin' in CSS.onFocusStyles:
                    el = el.parentElement
                    continue
                break

            for prop in CSS.onFocusStyles[f'{el.id}_focusin']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def focusout(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f'{el.id}_focusout' in CSS.onFocusStyles:
                    el = el.parentElement
                    continue
                break

            for prop in CSS.onFocusStyles[f'{el.id}_focusout']:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onFocusStyles[f'{id}_focusin'] = []
        CSS.onFocusStyles[f'{id}_focusout'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(" %% ")

            for styleKey in styleTmp:
                if not styleKey in CSS.styleMap:
                    continue

                for subStyle in CSS.styleMap[styleKey].split(";"):
                    subStyleKey, subStyleValue = subStyle.split(":")
                    subStyleKey = subStyleKey.replace(" ", "")

                    if subStyleKey in subStyleMerged or subStyleKey in style:
                        continue

                    subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

                style = style.replace(styleKey, "")

            style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

        for prop in style.split(";")[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == "transition":
                el.style.transition = prop.split(": ")[1]
                continue

            CSS.onFocusStyles[f'{id}_focusout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onFocusStyles[f'{id}_focusin'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener("focusin", create_proxy(focusin))
        el.addEventListener("focusout", create_proxy(focusout))


class HTML:
    styleMap = {
        "headerVeryBig": "margin: 10px auto; text-align: center; font-size: 175%; font-weight: bold; color: #55F; user-select: none",
        "headerBig": "margin: 10px auto; text-align: center; font-size: 150%; font-weight: bold; color: #55F; user-select: none",
        "headerMedium": "margin: 10px auto; text-align: center; font-size: 125%; font-weight: bold; color: #55F; user-select: none",
        "headerSmall": "margin: 10px auto; text-align: center; font-size: 100%; font-weight: bold; color: #55F; user-select: none",
        "headerVerySmall": "margin: 10px auto; text-align: center; font-size: 75%; font-weight: bold; color: #55F; user-select: none",
        "buttonBig": "z-index: 100; padding: 1px 8px 3px 8px; margin: 3px; text-align: center; font-size: 125%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px",
        "buttonMedium": "z-index: 100; padding: 1px 6px 3px 6px; margin: 3px; text-align: center; font-size: 100%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px",
        "buttonSmall": "z-index: 100; padding: 1px 4px 3px 4px; margin: 3px; text-align: center; font-size: 70%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px",
        "buttonImg": "z-index: 100; padding: 4px; color: #55F; background: #222; border: 2px solid #222; border-radius: 8px; user-select: none",
        "inputMedium": "z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none",
        "inputSmall": "z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none",
        "inputRange": "z-index: 110; padding: 1px 10px; margin: 3px; accent-color: #F7E163; background: #333; border: 0px solid #55F; border-radius: 4px; outline: none",
        "selectMedium": "z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none",
        "selectSmall": "z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none",
        "divNormal": "background: #222; padding: 5px; margin: 15px auto; border-radius: 10px",
        "divAlt": "background: #55F; color: #111; padding: 5px; margin: 15px auto; border-radius: 10px",
        "disabled": "color: #88B; background: #222",
        "flex": "display: flex",
        "pageLinks_Base": "width: 95%; color: #55F; margin-bottom: 0px; transition: opacity 0.25s, border-bottom 0.1s; border-radius: 6px; border-right: 4px solid #111; border-left: 4px solid #111"
    }
    disabledStyles = {}

    get = lambda id, isClass=False: list(document.getElementsByClassName(id)) if isClass else document.getElementById(id)
    move = lambda sourceId, targetId: document.getElementById(targetId).appendChild(document.getElementById(sourceId))

    def getLink(href: str, _nest: str = None, _style: str = None):
        if not _style is None and _style.split(" %% ")[0] in HTML.styleMap:
            subStyleMerged = ""
            _styleTmp = _style.split(" %% ")

            for style in _styleTmp:
                if not style in HTML.styleMap:
                    continue

                for subStyle in HTML.styleMap[style].split(";"):
                    subStyleKey, subStyleValue = subStyle.split(":")
                    subStyleKey = subStyleKey.replace(" ", "")

                    if subStyleKey in subStyleMerged or subStyleKey in _style:
                        continue

                    subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

                _style = _style.replace(style, "")

            _style = f'{subStyleMerged}{_style.split(" %% ")[-1]}'

        style = "color: #44F;"

        if not _style is None:
            style = f'{style} {_style}'

        htmlStr = f'<a href="{href}" target="_blank" style="{style}">'

        if not _nest is None:
            htmlStr += f'{_nest}'

        htmlStr += "</a>"

        return htmlStr

    def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
        if not _style is None and _style.split(" %% ")[0] in HTML.styleMap:
            subStyleMerged = ""
            _styleTmp = _style.split(" %% ")

            for style in _styleTmp:
                if not style in HTML.styleMap:
                    continue

                for subStyle in HTML.styleMap[style].split(";"):
                    subStyleKey, subStyleValue = subStyle.split(":")
                    subStyleKey = subStyleKey.replace(" ", "")

                    if subStyleKey in subStyleMerged or subStyleKey in _style:
                        continue

                    subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

                _style = _style.replace(style, "")

            _style = f'{subStyleMerged}{_style.split(" %% ")[-1]}'

        args = {"id": _id, "class": _class, "type": _type, "align": _align, "style": _style}
        additionsStr = ""

        for arg in args:
            if args[arg] is None:
                continue

            additionsStr += f' {arg}="{args[arg]}"'

        if not _custom is None:
            additionsStr += f' {_custom}'

        htmlStr = f'<{type}{additionsStr}>'

        if not _nest is None:
            htmlStr += _nest

        if not type in ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]:
            htmlStr += f'</{type}>'

        if not _prepend is None:
            htmlStr = f'{_prepend}{htmlStr}'

        if not id is None:
            document.getElementById(id).innerHTML += htmlStr

        return htmlStr

    def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
        htmlStr = HTML.add(type, None, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

        if not id is None:
            document.getElementById(id).innerHTML = htmlStr

        return htmlStr

    def addRaw(id: str, HTML: str):
        document.getElementById(id).innerHTML += HTML

    def setRaw(id: str, HTML: str):
        document.getElementById(id).innerHTML = HTML

    def copy(sourceId: str, targetId: str):
        el = document.getElementById(sourceId).cloneNode(True)
        el.id = f'{el.id}_NEW'
        document.getElementById(targetId).appendChild(el)

    def enable(id: str, state: bool = True):
        el = document.getElementById(id)

        if el.disabled is not state:
            return None

        onStyles = {
            "onHover": {
                "style": brdg.CSS.onHoverStyles(),
                "actions": ["mouseover", "mouseout"]
            },
            "onClick": {
                "style": brdg.CSS.onClickStyles(),
                "actions": ["mousedown", "mouseup"]
            },
            "onFocus": {
                "style": brdg.CSS.onFocusStyles(),
                "actions": ["focusout", "focusin"]
            }
        }

        el.disabled = not state

        if state:
            if not id in HTML.disabledStyles:
                return None

            for onStyle in onStyles:
                for action in onStyles[onStyle]["actions"]:
                    if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                        continue

                    if not f'{id}_{action}' in HTML.disabledStyles[id]["events"]:
                        continue

                    itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])

                    for i, item in enumerate(itemListTmp):
                        if item.startswith("color: ") and "color" in HTML.disabledStyles[id]["events"][f'{id}_{action}']:
                            onStyles[onStyle]["style"][f'{id}_{action}'][i] = HTML.disabledStyles[id]["events"][f'{id}_{action}']["color"]

                        elif item.startswith("background: ") and "background" in HTML.disabledStyles[id]["events"][f'{id}_{action}']:
                            onStyles[onStyle]["style"][f'{id}_{action}'][i] = HTML.disabledStyles[id]["events"][f'{id}_{action}']["background"]

            el.style.color = HTML.disabledStyles[id]["color"]
            el.style.background = HTML.disabledStyles[id]["background"]

            HTML.disabledStyles.pop(id)

            return None

        HTML.disabledStyles[id] = {"color": el.style.color, "background": el.style.background, "events": {}}

        for onStyle in onStyles:
            for action in onStyles[onStyle]["actions"]:
                if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                    continue

                HTML.disabledStyles[id]["events"][f'{id}_{action}'] = {}
                itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])

                for i, item in enumerate(itemListTmp):

                    if item.startswith("color: "):
                        HTML.disabledStyles[id]["events"][f'{id}_{action}']["color"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = "color: #88B"

                    elif item.startswith("background: "):
                        HTML.disabledStyles[id]["events"][f'{id}_{action}']["background"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = "background: #222"

        el.style.color = "#88B"
        el.style.background = "#222"

    def clear(id: str, isClass: bool = False):
        if isClass:
            for item in document.getElementsByClassName(id):
                item.innerHTML = ""
                return None

        document.getElementById(id).innerHTML = ""

    def remove(id: str, isClass: bool = False):
        if isClass:
            for item in document.getElementsByClassName(id):
                item.remove()

            return None

        document.getElementById(id).remove()


class JS:
    log = console.log
    f5 = window.location.reload
    getWindow = lambda: window
    getVP = lambda: window.innerHeight, window.innerWidth
    afterDelay = lambda func, delay: setTimeout(create_once_callable(func), delay)
    aSync = lambda func: setTimeout(create_once_callable(func), 0)
    atInterval = lambda func, delay: setInterval(create_proxy(func), delay)
    jsEval = lambda com: eval(str(com))
    popup = lambda type, txt: {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}[type](txt)
    clearCache = lambda: (window.localStorage.clear(), window.location.reload())
    cache = lambda key, value=None: (window.localStorage.setItem(key, value) if not value is None else None, window.localStorage.getItem(key))[-1]
    addEvent = lambda id, func, action="click", isClass=False: id.addEventListener(action, create_proxy(func)) if isClass else document.getElementById(id).addEventListener(action, create_proxy(func))

    def clearEvents(id):
        el = document.getElementById(id)
        el.outerHTML = el.outerHTML

    def setTitle(title: str):
        document.title = title

    def onResize(args=None):
        def update(size: int):
            sizeMap = {"0": ("0px", "50%", "85px"), "1": ("0px 20px", "75%", "85px"), "max": ("0px 20px", "100%", "100px")}

            if size >= 2:
                size = "max"

            if not str(size) in sizeMap:
                return None

            document.getElementById("body").style.padding = sizeMap[str(size)][0]
            document.getElementById("body").style.fontSize = sizeMap[str(size)][1]
            document.getElementById("nav_logo").style.maxWidth = sizeMap[str(size)][2]

        def update_links(size: int):
            sizeMap = {"0": 3, "1": 4, "2": 5, "max": 6}

            if size >= 3:
                size = "max"

            if not str(size) in sizeMap:
                return None

            JS.cache("page_links_colums", sizeMap[str(size)])
            from index import pageIndex
            pageIndex("noResize", page=window.localStorage.getItem("page_index"))

        def update_sonos(size: int):
            sizeMap = {"0": ("0%", "100%", "40px", "35px", "none"), "1": ("50%", "50%", "20px", "45px", ""), "max": ("75%", "25%", "0px", "55px", "")}

            if size >= 2:
                size = "max"

            if not str(size) in sizeMap:
                return None

            el = document.getElementById("SubPage_page_art")
            if not el is None:
                el.style.width = sizeMap[str(size)][0]
                el.style.display = sizeMap[str(size)][4]

            el = document.getElementById("SubPage_page_que")
            if not el is None:
                el.style.width = sizeMap[str(size)][1]
                el.style.marginBottom = sizeMap[str(size)][2]

            el = document.getElementById("SubPage_page_queAdd")
            if not el is None:
                el.style.minHeight = sizeMap[str(size)][3]

        page = window.localStorage.getItem("page_index")
        if page == "Portal":
            page = window.localStorage.getItem("page_portal")

        fmap = {"Links": update_links, "Sonos": update_sonos}

        size = 99
        if window.innerWidth < 450:
            size = 0
        elif window.innerWidth < 700:
            size = 1
        elif window.innerWidth < 950:
            size = 2

        update(size)
        if page in fmap:
            fmap[page](size)


class WS:
    PROTO = ""
    IP = ""
    PORT = ""
    PK = None

    ws = None
    loggedIn = False

    msgReply = {}
    lastMsg = ""
    msgDict = {}

    reconnectTries = 0
    afterReconnect = []

    class on:
        def open(arg=None):
            WS.reconnectTries = 0

        def message(arg):
            msg = arg.data
            WS.lastMsg = msg

            if msg.startswith("{") and msg.endswith("}"):
                data = loads(msg)

                for dict in data:
                    if not dict in WS.msgDict:
                        WS.msgDict[dict] = {}

                    WS.msgDict[dict] = {**WS.msgDict[dict], **data[dict]}

            if msg.split(" ")[0] in WS.msgReply:
                msg = msg.split(" ")[0]

                if callable(WS.msgReply[msg][0]):
                    WS.msgReply[msg][0]()
                    return None
                WS.ws.send(WS.msgReply[msg][0])

                if WS.msgReply[msg][1]:
                    WS.msgReply.pop(msg)

        error = lambda arg=None: (console.error(arg), WS.close)
        close = lambda arg=None: WS.on.connectionError("The connection to the server was lost!")

        def login(arg=None):
            WS.PK = PublicKey.load_pkcs1(WS.msg().split("<LOGIN> ")[1])

            if window.localStorage.getItem("token") == "" or WS.reconnectTries > 4:
                return None

            WS.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')

        def connectionError(msg: str):
            def loginTokenSucces():
                WS.ws.send("access")

                for msg in WS.afterReconnect:
                    WS.ws.send(msg)

                WS.afterReconnect = []

            def loginTokenFail():
                WS.reconnectTries = 99
                WS.on.connectionError("Unable to reconnect to the server, token authetication failed!")

            if not WS.loggedIn:
                return None

            if window.localStorage.getItem("token") == "" or WS.reconnectTries > 4:
                brdg.HTML.enable("page_Portal", False)

                brdg.HTML.set("div", "page", _id="page_error", _align="center")
                brdg.HTML.set("h1", "page_error", _nest="WARNING!", _style="headerVeryBig")
                brdg.HTML.add("p", "page_error", _nest=f'Connection lost to the server! {msg}')
                brdg.HTML.add("p", "page_error", _nest="Please refresh the page to try again.")

                return None

            WS.ws = None
            WS.PK = None
            WS.reconnectTries += 1

            WS.onMsg("<LOGIN_TOKEN_SUCCESS>", loginTokenSucces, oneTime=True)
            WS.onMsg("<LOGIN_TOKEN_FAIL>", loginTokenFail, oneTime=True)

            WS.start(WS.PROTO, WS.IP, WS.PORT)

    state = lambda: True if WS.ws.readyState in [0, 1] else False
    msg = lambda: (WS.close() if not WS.ws.readyState in [0, 1] else None, WS.lastMsg)[-1]
    dict = lambda: (WS.close() if not WS.ws.readyState in [0, 1] else None, deepcopy(WS.msgDict))[-1]

    def start(protocol: str, ip: str, port: str):
        if not WS.ws is None:
            WS.close()
            WS.ws = None
            WS.PK = None

        WS.PROTO = str(protocol)[:3]
        WS.IP = str(ip[:32])
        WS.PORT = str(port)[:5]

        WS.ws = eval(f'new WebSocket("{WS.PROTO}://{WS.IP}:{WS.PORT}")')

        WS.ws.onopen = WS.on.open
        WS.ws.onmessage = WS.on.message
        WS.ws.onerror = WS.on.error
        WS.ws.onclose = WS.on.close

        WS.onMsg("<LOGIN>", WS.on.login, oneTime=True)
        WS.onMsg("<LOGIN_CANCEL>", WS.close, oneTime=True)
        WS.onMsg("<CLOSE>", WS.close, oneTime=True)

    def close():
        WS.ws.close()

    def send(com: str):
        if WS.ws.readyState != 1:
            WS.afterReconnect.append(com)

            if WS.ws.readyState != 0:
                WS.close()

            return None

        WS.ws.send(com)

    def onMsg(msgRecv: str, msgOrFunc: msg, oneTime: bool = False):
        WS.msgReply[msgRecv] = (msgOrFunc, oneTime)


class widgets:
    def sheet(maincom: str,
              name: str,
              data: dict,
              elId: str = None,
              dates: tuple = (),
              halfView: list = [],
              excludeView: tuple = (),
              typeDict: dict = {},
              optionsDict: dict = {},
              showInput: bool = True,
              showAction: bool = True,
              showTag: bool = True,
              tagIsList: bool = True,
              index: int = 0):
        def recursion(args=None):
            el = document.getElementById(f'{maincom}_{name}_loadMore')
            if el is None:
                return None

            el.outerHTML = el.outerHTML
            widgets.sheet(maincom=maincom, name=name, data=data, elId=elId, dates=dates, halfView=halfView, excludeView=excludeView, typeDict=typeDict, optionsDict=optionsDict, showAction=showAction, showTag=showTag, index=index + 1)

        def getLines(data, exclude):
            headers = []
            for key in data:
                for item in data[key]:
                    (lambda: None if item in headers or item in exclude else headers.append(item))()

            lines = [["Tag"] + headers]
            for key in data:
                line = [key]
                for header in headers:
                    (lambda: line.append(None) if not header in data[key] else line.append(data[key][header]))()

                lines.append(line)

            return lines

        lines = getLines(data, excludeView)

        if not elId is None and index == 0:
            brdg.HTML.add("div", elId, _id=f'{maincom}_{name}', _style="margin: 10px; border: 2px solid #111;")
            brdg.HTML.add(f'button', elId, _id=f'{maincom}_{name}_loadMore', _nest=f'Load more (0 / {len(lines)})', _type=f'button', _style=f'buttonBig %% width: 50%;')
            document.getElementById(f'{maincom}_{name}_loadMore').addEventListener("click", create_proxy(recursion))
            brdg.CSS.onHoverClick(f'{maincom}_{name}_loadMore', f'buttonHover', f'buttonClick')

        halfViewTmp = list(halfView)
        halfView = (lambda: ["Action"] if showAction and "Action" in halfViewTmp else [])()
        for key in halfViewTmp:
            if key in lines[0]:
                halfView.append(key)

        defaultWidth = 100 / (len(lines[0]) + (showAction - (not showTag)) - (len(halfView) / 2))
        rows = ""
        eventConfig = {"editIds": [], "inputIds": [], "actionIds": [], "popupIds": []}
        for lineIndex, line in (lambda: enumerate(lines) if elId is None else enumerate([lines[index]]))():
            if not elId is None:
                lineIndex = index

            background = (lambda: " background: #191919;" if lineIndex == 0 else " background: #202020;")()
            borderBottom = (lambda: "" if lineIndex + 1 >= len(lines) else " border-bottom: 2px solid #111;")()
            fontStyle = (lambda: "headerSmall %% " if lineIndex == 0 else "font-size: 75%; ")()
            tag = line[0]

            cols = ""
            for valueIndex, value in enumerate(line):
                borderRight = (lambda: "" if valueIndex + 1 >= len(line) and not showAction else " border-right: 2px solid #111;")()
                key = lines[0][valueIndex]

                if key == "Tag" and not showTag:
                    continue

                valueType = (lambda: typeDict[key].__name__ if key in typeDict else type(value).__name__)()

                if key in dates and type(value) in (int, float):
                    value = datetime.fromtimestamp(value).strftime("%d %b %y")
                    valueType = "date"
                elif type(value) is bool:
                    value = (lambda: "Yes" if value else "No")()
                elif type(value) in [list, tuple]:
                    value = ", ".join(value)
                elif type(value) is type(None):
                    value = ""

                txt = brdg.HTML.add("p", _id=f'{maincom}_{name}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')

                if lineIndex != 0 and valueIndex != 0:
                    cols += brdg.HTML.add("div", _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}', _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')
                    eventConfig["editIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')
                    if valueType in ["str", "list", "tuple"]:
                        eventConfig["popupIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

                elif lineIndex != 0:
                    cols += brdg.HTML.add("div", _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}', _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')
                    if valueType in ["str", "list", "tuple"]:
                        eventConfig["popupIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

                else:
                    cols += brdg.HTML.add("div", _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')

                if valueIndex + 1 < len(line) or not showAction:
                    continue

                if lineIndex == 0:
                    valueType, value, key = ("none", "Action", "Action")
                    txt = brdg.HTML.add("p", _id=f'{maincom}_{name}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                    cols += brdg.HTML.add("div", _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;')
                    continue

                valueType, value, key = ("rem", "Remove", "Action")
                btn = brdg.HTML.add("button",
                                    _id=f'{maincom}_{name}_{tag}_{key}_{valueType}',
                                    _nest=value,
                                    _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -6px; background: #333; color: #BFF;')
                cols += brdg.HTML.add(
                    "div",
                    _nest=btn,
                    _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden; margin: 0px -2px 0px 0px;')
                eventConfig["actionIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

            if not elId is None:
                brdg.HTML.add("div", f'{maincom}_{name}', _nest=cols, _style=f'flex %%{(lambda: " height: 29px;" if lineIndex == 0 else "")()}{background}{borderBottom}')
                brdg.HTML.setRaw(f'{maincom}_{name}_loadMore', f'Load more ({lineIndex} / {len(lines)})')
                if lineIndex > 100:
                    document.getElementById(f'{maincom}_{name}_loadMore').scrollIntoView()
            else:
                rows += brdg.HTML.add("div", _nest=cols, _style=f'flex %%{(lambda: " height: 29px;" if lineIndex == 0 else " height: 21px;")()}{background}{borderBottom}')

            if lineIndex != 0 or not showInput:
                continue

            cols = ""
            for valueIndex, value in enumerate(line):
                key = lines[0][valueIndex]
                margin = (lambda: " margin: 0px -2px;" if valueIndex == 0 else " margin: 0px -2px 0px 0px;")()

                try:
                    valueType = (lambda: typeDict[key].__name__ if key in typeDict else type(lines[1][valueIndex]).__name__)()
                except IndexError:
                    valueType = "NoneType"

                main, typ, custom, nest, styleInp, styleDiv = ("input", "text", "", "", " height: 100%; top: -1px; background: #333; color: #BFF; overflow: hidden;", " overflow: hidden;")
                if valueType == "NoneType":
                    typ = "text"
                elif key in dates and valueType in ("int", "float"):
                    typ, custom, valueType = ("date", f' value="{datetime.now().strftime("%Y-%m-%d")}"', "date")
                elif valueType in ("int", "float"):
                    typ = "number"
                elif valueType == "bool":
                    typ, custom, styleInp = ("checkbox", " checked", " height: 75%; top: 1px; background: #333; color: #BFF; overflow: hidden;")
                elif valueType in ["list", "tuple"]:
                    main, typ, custom, styleInp, styleDiv = ("select", "", " size=\"1\" multiple", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;", " background: #333; color: #BFF; overflow: hidden;")

                    allData = []
                    if key in optionsDict:
                        allData = optionsDict[key]
                    elif f'/{key}.json' in optionsDict:
                        allData = optionsDict[f'/{key}.json']

                    for option in allData:
                        nest += HTML.add(f'option', _nest=f'{option}', _style="margin: 0px 1px; background: transparent; color: inherit;", _custom=f'value="{option}"')

                if valueIndex == 0 and tagIsList:
                    valueType = "str"
                    main, typ, custom, styleInp, styleDiv = ("select", "", " size=\"1\"", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;", " background: #333; color: #BFF; overflow: hidden;")

                    allData = []
                    if key in optionsDict:
                        allData = optionsDict[key]
                    elif f'/{key}.json' in optionsDict:
                        allData = optionsDict[f'/{key}.json']

                    for option in allData:
                        nest += HTML.add(f'option', _nest=f'{option}', _style="margin: 0px 1px; background: transparent; color: inherit;", _custom=f'value="{option}"')

                txt = brdg.HTML.add(main,
                                    _id=f'Input_{maincom}_{name}_{tag}_{key}_{valueType}',
                                    _class=f'Input_{maincom}_{name}_{tag}',
                                    _nest=nest,
                                    _type=typ,
                                    _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center;{styleInp}',
                                    _custom=f'placeholder="{value}"{custom}')
                cols += brdg.HTML.add("div",
                                      _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}',
                                      _nest=txt,
                                      _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; border: 2px solid #55F; border-radius: 0px;{styleDiv}{margin}')
                eventConfig["inputIds"].append(f'Input_{maincom}_{name}_{tag}_{key}_{valueType}')

                if valueIndex + 1 < len(line):
                    continue

                valueType, value, key = "add", "Add", "Action"
                btn = brdg.HTML.add("button",
                                    _id=f'{maincom}_{name}_{tag}_{key}_{valueType}',
                                    _nest=value,
                                    _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -1px; background: #333; color: #BFF')
                cols += brdg.HTML.add(
                    "div",
                    _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}',
                    _nest=btn,
                    _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden;{styleDiv}{margin}')
                eventConfig["actionIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

            if not elId is None:
                brdg.HTML.add("div", f'{maincom}_{name}', _nest=cols, _style=f'flex %% height: 29px; background: #202020;{borderBottom}')
            else:
                rows += brdg.HTML.add("div", _nest=cols, _style=f'flex %% height: 29px; background: #202020;{borderBottom}')

        if not elId is None and index + 1 < len(lines):
            if index % 100 == 0 and not index == 0:
                document.getElementById(f'{maincom}_{name}_loadMore').addEventListener("click", create_proxy(recursion))
                brdg.CSS.onHoverClick(f'{maincom}_{name}_loadMore', f'buttonHover', f'buttonClick')
                return None
            setTimeout(create_once_callable(recursion), 0)

        elif not elId is None:
            return eventConfig

        return (brdg.HTML.add("div", _id=f'{maincom}_{name}', _nest=rows, _style="margin: 10px; border: 2px solid #111;"), eventConfig)

    def sheetMakeEvents(eventConfig: dict, optionsDict: dict = {}, pswChangeDict: dict = {}, sendKey: bool = True):
        def onContextMenu(args):
            def submit(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = document.getElementById(args.target.id)
                maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
                value = el.value

                if sendKey:
                    if key in pswChangeDict:
                        psw = JS.popup(f'prompt', "Please enter the new password -for the user.")
                        if psw is None or psw == "":
                            return None
                        psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.PK)) if key == "User" else str(encrypt(psw.encode(), WS.PK)).replace(" ", "%20"))()
                        brdg.WS.send(f'{maincom} rpwmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {pswChangeDict[key].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                    brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')

                else:
                    if tag in pswChangeDict:
                        psw = JS.popup(f'prompt', "Please enter the new password for the user.")
                        if psw is None or psw == "":
                            return None
                        psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.PK)) if tag == "User" else str(encrypt(psw.encode(), WS.PK)).replace(" ", "%20"))()
                        brdg.WS.send(f'{maincom} kpwmodify {sheet.replace(" ", "%20")} {pswChangeDict[tag].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                    brdg.WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

                txt = brdg.HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                el.parentElement.innerHTML = txt
                document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

            def submitDate(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = document.getElementById(args.target.id)
                maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
                value = int(datetime.strptime(el.value, "%Y-%m-%d").timestamp())

                if sendKey:
                    brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
                else:
                    brdg.WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

                value = datetime.fromtimestamp(value).strftime("%d %b %y")
                txt = brdg.HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                el.parentElement.innerHTML = txt
                document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

            def submitNumber(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = document.getElementById(args.target.id)
                maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
                value = (lambda: float(el.value) if valueType == "float" else int(el.value))()

                if sendKey:
                    brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
                else:
                    brdg.WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

                txt = brdg.HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                el.parentElement.innerHTML = txt
                document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

            def submitBool(args):
                el = document.getElementById(args.target.id)
                maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
                value = not (lambda: False if el.innerHTML == "No" else True)()

                if sendKey:
                    brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
                else:
                    brdg.WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

                if value:
                    el.innerHTML = "Yes"
                    return None
                el.innerHTML = "No"

            def submitList(args):
                if not args.key in ["Enter", "Escape"]:
                    return None

                el = document.getElementById(args.target.id.replace("Div_", "Input_"))
                maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

                value = []
                for subEls in list(args.target.childNodes):
                    if subEls.selected is True:
                        value.append(subEls.value)
                value = ", ".join(value)

                if sendKey:
                    brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')
                else:
                    brdg.WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

                pel = el.parentElement
                for style in ("z-index", "margin-bottom", "min-height", "color", "background", "overflow", "scrollbar-width", "transition", "margin-bottom", "min-height"):
                    setattr(pel.style, style, "")

                txt = brdg.HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                pel.innerHTML = txt
                pel.outerHTML = pel.outerHTML

                document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

            args.preventDefault()
            maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

            main, typ, custom, nest, styleInp = ("input", "text", f' value="{args.target.innerHTML}"', "", " height: 100%; top: -3px; background: #333; color: #BFF; overflow-x: hidden;")
            if valueType == "NoneType":
                typ = "text"
            elif valueType == "date":
                typ, custom, valueType = ("date", f' value="{datetime.strptime(args.target.innerHTML, "%d %b %y").strftime("%Y-%m-%d")}"', "date")
            elif valueType in ("int", "float"):
                typ = "number"
            elif valueType == "bool":
                submitBool(args)
                return None
            elif valueType in ["list", "tuple"]:
                main, typ, custom, styleInp = ("select", "", " size=\"1\" multiple", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;")

                keyTmp = key
                if not sendKey:
                    keyTmp = tag

                allData = []
                if keyTmp in optionsDict:
                    allData = optionsDict[keyTmp]
                elif f'/{keyTmp}.json' in optionsDict:
                    allData = optionsDict[f'/{keyTmp}.json']

                for option in allData:
                    nest += HTML.add(f'option', _nest=f'{option}', _style="margin: 0px 1px; background: transparent; color: inherit;", _custom=f'value="{option}"')

            txt = brdg.HTML.add(main,
                                _id=f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}',
                                _class=f'Input_{maincom}_{sheet}_{tag}',
                                _nest=nest,
                                _type=typ,
                                _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center;{styleInp}',
                                _custom=f'placeholder="{key}"{custom}')
            pel = args.target.parentElement
            pel.innerHTML = txt

            func = submit
            if valueType == "date":
                func = submitDate
            elif valueType in ("int", "float"):
                func = submitNumber
            elif valueType == "list":
                pel.style.background = "#333"
                pel.style.color = "#BFF"
                brdg.CSS.onHoverFocus(pel.id, "selectHover %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;", "selectFocus %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;")
                document.getElementById(pel.id).addEventListener("keyup", create_proxy(submitList))
                return None

            brdg.CSS.onHoverFocus(f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}', "inputHover", "inputFocus")
            document.getElementById(f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("keyup", create_proxy(func))

        def onDblClick(args):
            window.alert(str(args.target.innerHTML))

        def addRecord(args):
            maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

            for i, els in enumerate(list(document.getElementsByClassName(f'Input_{maincom}_{sheet}_{tag}'))):
                if els.value in ["", " "]:
                    continue

                key = els.id.split("_")[-2]
                value = els.value
                if els.id.split("_")[-1] == "date":
                    value = str(int(datetime.strptime(els.value, "%Y-%m-%d").timestamp()))
                elif els.id.split("_")[-1] == "bool":
                    value = (lambda: "True" if els.checked else "False")()
                elif els.id.split("_")[-1] in ["list", "tuple"]:
                    value = []
                    for subEls in list(els.childNodes):
                        if subEls.selected is True:
                            value.append(subEls.value)
                    value = ", ".join(value)
                elif els.id.split("_")[-1] == "NoneType":
                    continue

                if i == 0:
                    tag = els.value
                    brdg.WS.send(f'{maincom} add {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}')
                    continue

                from subs.portal_sheets import pageSub
                WS.onMsg("{\"" + maincom + "\":", pageSub, oneTime=True)
                brdg.WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')

        def remRecord(args):
            maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

            if not JS.popup("confirm", f'Are you sure you want to delete "{tag}"?\nThis can not be reverted!'):
                return None

            from subs.portal_sheets import pageSub
            WS.onMsg("{\"" + maincom + "\":", pageSub, oneTime=True)
            brdg.WS.send(f'{maincom} delete {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}')

        for id in eventConfig["editIds"]:
            el = document.getElementById(id)
            if el is None:
                return None
            el.addEventListener("contextmenu", create_proxy(onContextMenu))

        for id in eventConfig["inputIds"]:
            el = document.getElementById(id)
            if el is None:
                return None

            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]

            if valueType == "list":
                el = document.getElementById(el.id.replace("Input_", "Div_"))
                brdg.CSS.onHoverFocus(el.id, "selectHover %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;", "selectFocus %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;")
            else:
                brdg.CSS.onHoverFocus(el.id, "inputHover", "inputFocus")

        for id in eventConfig["actionIds"]:
            el = document.getElementById(id)
            if el is None:
                return None

            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]

            (lambda: document.getElementById(el.id).addEventListener("click", create_proxy(remRecord)) if valueType == "rem" else document.getElementById(el.id).addEventListener("click", create_proxy(addRecord)))()
            brdg.CSS.onHoverClick(el.id, "buttonHover", "buttonClick")

        for id in eventConfig["popupIds"]:
            el = document.getElementById(id)
            if el is None:
                return None
            el.addEventListener("dblclick", create_proxy(onDblClick))

    def graph(name: str, rowHeight: str, rows: int, rowStep: int, cols: int, colStep: int = None, origin: tuple = (), rowPrefix: str = "", rowAfterfix: str = "", colNames: tuple = (), smallHeaders: bool = False):
        rowHeightSmall = rowHeight
        colsNormal = 100 / (cols + 1)
        colsSmall = 100 / (cols + 1)
        if smallHeaders:
            rowHeightValue = ""
            rowHeightFormat = ""
            for i, char in enumerate(rowHeight):
                if char in "0123456789":
                    rowHeightValue += char
                    continue

                rowHeightFormat = rowHeight[i:]
                break

            rowHeightSmall = f'{int(rowHeightValue) / 2}{rowHeightFormat}'
            colsSmall = 100 / ((cols + 1) * 2)
            colsNormal = (100 / (cols + 1)) + (colsSmall / cols)

        htmlRows = ""
        for i1 in range(0, rows):
            borderStyle = ""
            if i1 > 0:
                borderStyle = " border-top: 2px dashed #111;"

            txt = brdg.HTML.add("h1", _nest=f'{rowPrefix}{(rows - i1) * rowStep}{rowAfterfix}', _style="headerSmall %% height: 25%; margin: 0px auto auto auto;")
            if i1 == rows - 1:
                txt += brdg.HTML.add("h1", _style="headerSmall %% height: 40%; margin: auto auto auto auto;")
                txt += brdg.HTML.add("h1", _nest=f'{rowPrefix}{(rows - i1 - 1) * rowStep}{rowAfterfix}', _style="headerSmall %% height: 25%; margin: auto auto auto 5px;")

            htmlCols = brdg.HTML.add("div", _nest=txt, _id=f'{name}_row_{rows - i1 - 1}_col_header', _style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeight}; border-right: 2px solid #111;{borderStyle}')
            for i2 in range(0, cols):
                if i2 == cols - 1:
                    htmlCols += brdg.HTML.add("div", _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight};{borderStyle}')
                else:
                    htmlCols += brdg.HTML.add("div", _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight}; border-right: 1px dashed #111;{borderStyle}')

            htmlRows += brdg.HTML.add("div", _nest=htmlCols, _id=f'{name}_row_{rows - i1 - 1}', _style=f'flex %% width: 100%; height: {rowHeight};')

        txt = ""
        if not smallHeaders:
            if len(origin) == 1:
                txt += brdg.HTML.add("h1", _nest=f'{origin[0]}', _style="headerSmall %% margin: auto;")
            elif len(origin) > 1:
                txt += brdg.HTML.add("h1", _nest=f'{origin[0]}', _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: left;")
                txt += brdg.HTML.add("h1", _nest="/", _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: center;")
                txt += brdg.HTML.add("h1", _nest=f'{origin[1]}', _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: right;")

        htmlCols = brdg.HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_header', _style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeightSmall}; border-right: 2px solid #111; border-top: 2px solid #111;')
        for i2 in range(0, cols):
            try:
                txt = brdg.HTML.add("h1", _nest=f'{colNames[i2]}', _style="headerSmall %% margin: auto;")
            except IndexError:
                txt = brdg.HTML.add("h1", _nest="", _style="headerSmall %% margin: auto;")

            if i2 == cols - 1:
                htmlCols += brdg.HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-top: 2px solid #111;')
            else:
                htmlCols += brdg.HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-right: 1px dashed #111; border-top: 2px solid #111;')

        htmlRows += brdg.HTML.add("div", _nest=htmlCols, _id=f'{name}_row_header', _style=f'flex %% width: 100%; height: {rowHeightSmall};')

        return brdg.HTML.add("div", _nest=htmlRows, _id=name, _style="margin: 10px; padding-bottom: 2px; border: 2px solid #111;")

    def graphDraw(name: str, cords: tuple, lineRes: int = 100, disalowRecursive: bool = False):
        def mouseover(args):
            id = args.target.id
            if id == "":
                el = document.getElementById(args.target.parentElement.id)
            elif not id.endswith("Txt"):
                el = document.getElementById(f'{args.target.id}Txt')
            else:
                el = document.getElementById(id)

            el.style.width = "25vw"
            el.style.opacity = "90%"
            el.style.transition = "width 0.25s, opacity 0.5s"

        def mouseout(args):
            id = args.target.id
            if id == "":
                el = document.getElementById(args.target.parentElement.id)
            elif not id.endswith("Txt"):
                el = document.getElementById(f'{args.target.id}Txt')
            else:
                el = document.getElementById(id)

            el.style.width = "0vw"
            el.style.opacity = "0%"
            el.style.transition = "width 0.5s, opacity 0.25s"

        def getLineSteps(oldCords, curCords, resolution):
            diff1, diff2 = (curCords[0] - oldCords[0], curCords[1] - oldCords[1])

            if diff1 < 0:
                diff1 = -diff1
            if diff2 < 0:
                diff2 = -diff2

            biggestDiff = 0
            smallestDiff = 1
            altDiff = curCords[1] - oldCords[1]
            if diff2 > diff1:
                biggestDiff = 1
                smallestDiff = 0
                altDiff = curCords[0] - oldCords[0]

            increments = 1
            if curCords[biggestDiff] > oldCords[biggestDiff]:
                increments = -1

            steps = []
            totalSteps = len(range(int(curCords[biggestDiff] * resolution), int(oldCords[biggestDiff] * resolution), increments))
            for i, step in enumerate(range(int(curCords[biggestDiff] * resolution), int(oldCords[biggestDiff] * resolution), increments)):
                if biggestDiff == 0:
                    steps.append((step / resolution, round(curCords[smallestDiff] - ((altDiff / totalSteps) * i), 2)))
                else:
                    steps.append((round(curCords[smallestDiff] - ((altDiff / totalSteps) * i), 2), step / resolution))

            return steps

        addOnHovers = []
        for i, cord in enumerate(cords):
            colNum, colFloat = str(float(cord[0])).split(".")
            rowNum, rowFloat = str(float(cord[1])).split(".")

            onHoverTxt = None
            if len(cord) > 2:
                onHoverTxt = str(cord[2])

            try:
                if onHoverTxt is None:
                    brdg.HTML.add(
                        "div",
                        f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                        _style=
                        f'z-index: 10; width: 10px; height: 10px; margin: -5px; background: #55F; border-radius: 10px; position: relative; top: {95 - int(rowFloat[:2] + "0" * (2 - len(rowFloat[:2])))}%; left: {-5 + int(colFloat[:2] + "0" * (2 - len(colFloat[:2])))}%'
                    )
                else:
                    vw = "-25vw"
                    if int(colNum) < 3:
                        vw = "0.5vw"

                    vh = "0.5vh"
                    if int(rowNum) < 3:
                        vh = "-25vh"

                    txt = brdg.HTML.add("h1", _nest=onHoverTxt, _style="headerSmall %% white-space: nowrap; text-overflow: ellipsis;")
                    details = brdg.HTML.add("div",
                                            _nest=txt,
                                            _id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHoverTxt',
                                            _style=f'divNormal %% z-index: 12; width: 0vw; height: 25vh; margin: {vh} 0px 0px {vw}; padding: 0px; position: relative; opacity: 0%; transition: width 0.25s, opacity 0.5s; overflow-x: hidden;')
                    brdg.HTML.add(
                        "div",
                        f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                        _nest=details,
                        _id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHover',
                        _style=
                        f'z-index: 11; width: 10px; height: 10px; margin: -5px; background: #55F; border-radius: 10px; position: relative; top: {95 - int(rowFloat[:2] + "0" * (2 - len(rowFloat[:2])))}%; left: {-5 + int(colFloat[:2] + "0" * (2 - len(colFloat[:2])))}%'
                    )

                    addOnHovers.append(f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHover')
            except AttributeError:
                raise AttributeError(f'Invalid ID/ Cords: {name}_row_{rowNum[:2]}_col_{colNum[:2]} {cord}')

            if i <= 0 or disalowRecursive:
                continue

            oldCords = list(cords[i - 1])
            curCords = list(cords[i])

            steps = getLineSteps(oldCords, curCords, lineRes)

            widgets.graphDraw(name, steps, lineRes=lineRes, disalowRecursive=True)

        for id in addOnHovers:
            el = document.getElementById(id)
            el.addEventListener("mouseover", create_proxy(mouseover))
            el.addEventListener("mouseout", create_proxy(mouseout))


class brdg:
    class HTML:
        def enable(id: str, state: bool = True):
            return HTML.enable(id, state)

        def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
            return HTML.set(type, id, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

        def setRaw(id: str, html: str):
            return HTML.setRaw(id, html)

        def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
            return HTML.add(type, id, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

    class CSS:
        def onHover(id: str, style: str):
            CSS.onHover(id, style)

        def onClick(id: str, style: str):
            CSS.onClick(id, style)

        def onFocus(id: str, style: str):
            CSS.onFocus(id, style)

        onHoverClick = lambda id, styleHover, styleClick: CSS.onHoverClick(id, styleHover, styleClick)
        onHoverFocus = lambda id, styleHover, styleClick: CSS.onHoverFocus(id, styleHover, styleClick)

        onHoverStyles = lambda: CSS.onHoverStyles
        onClickStyles = lambda: CSS.onClickStyles
        onFocusStyles = lambda: CSS.onFocusStyles

    class WS:
        msg = lambda: WS.msg
        dict = lambda: WS.dict
        send = lambda com: WS.send(com)

        def onMsg(msgRecv: str, msgOrFunc: msg, oneTime: bool = False):
            WS.onMsg(msgRecv, msgOrFunc, oneTime)