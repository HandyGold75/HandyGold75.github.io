from js import document, window, eval, setTimeout, setInterval, console
from pyodide.ffi import create_proxy, create_once_callable # type: ignore
from rsa import PublicKey
from json import loads


class CSS:
    styleMap = {
        "buttonHover": "z-index: 101; color: #FFF; background: #444; transition: 0.25s",
        "buttonClick": "z-index: 102; color: #55F; background: #BBF; transition: 0.1s",
        "inputHover": "z-index: 111; color: #FFF; background: #444; transition: 0.25s",
        "inputFocus": "z-index: 112; color: #FFF; background: #444; transition: 0.1s",
        "selectHover": "z-index: 121; margin-bottom: -80px; height: 108px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.25s",
        "selectFocus": "z-index: 122; margin-bottom: -80px; height: 108px; color: #FFF; background: #444; overflow-y: scroll; scrollbar-width: auto; transition: 0.1s",
        "imgHover": "z-index: 101; color: #FFF; background: #444; border: 3px solid #FBDF56; transition: 0.25s",
        "imgClick": "z-index: 102; color: #55F; background: #550; border: 3px solid #FBDF56; transition: 0.1s",
        "disabled": f'color: #88B; background: #222'
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
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            for prop in CSS.onHoverStyles[f'{id}_mouseover']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseout(args=None):
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            if document.getElementById(id).tagName != f'BUTTON' and document.activeElement == args.target:
                return None

            for prop in CSS.onHoverStyles[f'{id}_mouseout']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onHoverStyles[f'{id}_mouseover'] = []
        CSS.onHoverStyles[f'{id}_mouseout'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(f' %% ')

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

        for prop in style.split(f';')[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == f'transition':
                el.style.transition = f'{prop.split(": ")[1]}'
                continue

            CSS.onHoverStyles[f'{id}_mouseout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onHoverStyles[f'{id}_mouseover'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener(f'mouseover', create_proxy(mouseover))
        el.addEventListener(f'mouseout', create_proxy(mouseout))

    def onClick(id: str, style: str):
        def mousedown(args=None):
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            for prop in CSS.onClickStyles[f'{id}_mousedown']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseup(args=None):
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            for prop in CSS.onClickStyles[f'{id}_mouseup']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onClickStyles[f'{id}_mousedown'] = []
        CSS.onClickStyles[f'{id}_mouseup'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(f' %% ')

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

        for prop in style.split(f';')[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == f'transition':
                el.style.transition = f'{prop.split(": ")[1]}'
                continue

            CSS.onClickStyles[f'{id}_mouseup'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onClickStyles[f'{id}_mousedown'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener(f'mousedown', create_proxy(mousedown))
        el.addEventListener(f'mouseup', create_proxy(mouseup))

    def onFocus(id: str, style: str):
        def focusin(args=None):
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            for prop in CSS.onFocusStyles[f'{id}_focusin']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        def focusout(args=None):
            id = args.target.id

            try:
                if id == "" or id.split("_")[-2].startswith("img"):
                    id = args.target.parentElement.id
            except IndexError:
                pass

            for prop in CSS.onFocusStyles[f'{id}_focusout']:
                setattr(document.getElementById(id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)

        CSS.onFocusStyles[f'{id}_focusin'] = []
        CSS.onFocusStyles[f'{id}_focusout'] = []

        if style.split(" %% ")[0] in CSS.styleMap:
            subStyleMerged = ""
            styleTmp = style.split(f' %% ')

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

        for prop in style.split(f';')[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == f'transition':
                el.style.transition = f'{prop.split(": ")[1]}'
                continue

            CSS.onFocusStyles[f'{id}_focusout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
            CSS.onFocusStyles[f'{id}_focusin'].append(f'{styleKey}: {prop.split(": ")[1]}')

        el.addEventListener(f'focusin', create_proxy(focusin))
        el.addEventListener(f'focusout', create_proxy(focusout))


class HTML:
    styleMap = {
        "headerVeryBig": f'margin: 10px auto; text-align: center; font-size: 175%; font-weight: bold; color: #55F; user-select: none',
        "headerBig": f'margin: 10px auto; text-align: center; font-size: 150%; font-weight: bold; color: #55F; user-select: none',
        "headerMedium": f'margin: 10px auto; text-align: center; font-size: 125%; font-weight: bold; color: #55F; user-select: none',
        "headerSmall": f'margin: 10px auto; text-align: center; font-size: 100%; font-weight: bold; color: #55F; user-select: none',
        "headerVerySmall": f'margin: 10px auto; text-align: center; font-size: 75%; font-weight: bold; color: #55F; user-select: none',
        "buttonBig": f'z-index: 100; padding: 1px 8px 3px 8px; margin: 3px; text-align: center; font-size: 125%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonMedium": f'z-index: 100; padding: 1px 6px 3px 6px; margin: 3px; text-align: center; font-size: 100%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonSmall": f'z-index: 100; padding: 1px 4px 3px 4px; margin: 3px; text-align: center; font-size: 70%; word-wrap: break-word; color: #BFF; background: #333; border: 2px solid #55F; border-radius: 4px',
        "buttonImg": f'z-index: 100; padding: 4px; color: #55F; background: #222; border: 2px solid #222; border-radius: 8px; user-select: none',
        "inputMedium": f'z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none',
        "inputSmall": f'z-index: 110; padding: 1px 10px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none',
        "inputRange": f'z-index: 110; padding: 1px 10px; margin: 3px; accent-color: #F7E163; background: #333; border: 0px solid #55F; border-radius: 4px; outline: none',
        "selectMedium": f'z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 100%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none',
        "selectSmall": f'z-index: 120; padding: 0px; margin: 3px; color: #BFF; font-size: 75%; background: #333; border: 2px solid #55F; border-radius: 4px; outline: none; overflow-y: hidden; scrollbar-width: none',
        "divNormal": f'background: #222; padding: 5px; margin: 15px auto; border-radius: 10px',
        "divAlt": f'background: #55F; color: #111; padding: 5px; margin: 15px auto; border-radius: 10px',
        "disabled": f'color: #88B; background: #222',
        "flex": f'display: flex',
        "pageLinks_Base": f'width: 95%; color: #55F; margin-bottom: 0px; transition: opacity 0.25s, border-bottom 0.1s; border-radius: 6px; border-right: 4px solid #111; border-left: 4px solid #111'
    }
    disabledStyles = {}

    get = lambda id, isClass=False: list(document.getElementsByClassName(id)) if isClass else document.getElementById(id)
    move = lambda sourceId, targetId: document.getElementById(targetId).appendChild(document.getElementById(sourceId))

    def getLink(href: str, _nest: str = None, _style: str = None):
        if not _style is None and _style.split(" %% ")[0] in HTML.styleMap:
            subStyleMerged = ""
            _styleTmp = _style.split(f' %% ')

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

        style = f'color: #44F;'

        if not _style is None:
            style = f'{style} {_style}'

        htmlStr = f'<a href="{href}" target="_blank" style="{style}">'

        if not _nest is None:
            htmlStr += f'{_nest}'

        htmlStr += f'</a>'

        return f'{htmlStr}'

    def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
        if not _style is None and _style.split(" %% ")[0] in HTML.styleMap:
            subStyleMerged = ""
            _styleTmp = _style.split(f' %% ')

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
            document.getElementById(f'{id}').innerHTML += f'{htmlStr}'

        return f'{htmlStr}'

    def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
        htmlStr = HTML.add(type, None, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

        if not id is None:
            document.getElementById(f'{id}').innerHTML = htmlStr

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
                "style": bridge.CSS.onHoverStyles(),
                "actions": ["mouseover", "mouseout"]
            },
            "onClick": {
                "style": bridge.CSS.onClickStyles(),
                "actions": ["mousedown", "mouseup"]
            },
            "onFocus": {
                "style": bridge.CSS.onFocusStyles(),
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
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = f'color: #88B'

                    elif item.startswith("background: "):
                        HTML.disabledStyles[id]["events"][f'{id}_{action}']["background"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = f'background: #222'

        el.style.color = f'#88B'
        el.style.background = f'#222'

    def clear(id: str, isClass: bool = False):
        if isClass:
            for item in document.getElementsByClassName(id):
                item.innerHTML = f''
                return None

        document.getElementById(id).innerHTML = f''

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
    afterDelay = lambda func, delay: setTimeout(create_once_callable(func), delay)
    aSync = lambda func: setTimeout(create_once_callable(func), 0)
    atInterval = lambda func, delay: setInterval(create_proxy(func), delay)
    jsEval = lambda com: eval(f'{com}')
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

            document.getElementById(f'body').style.padding = sizeMap[str(size)][0]
            document.getElementById(f'body').style.fontSize = sizeMap[str(size)][1]
            document.getElementById(f'nav_logo').style.maxWidth = sizeMap[str(size)][2]

        def update_links(size: int):
            sizeMap = {"0": 3, "1": 4, "2": 5, "max": 6}

            if size >= 3:
                size = "max"

            if not str(size) in sizeMap:
                return None

            JS.cache("page_links_colums", sizeMap[str(size)])
            from index import pageIndex
            pageIndex("noResize", page=window.localStorage.getItem(f'page_index'))

        def update_sonos(size: int):
            sizeMap = {"0": ("0%", "100%", "40px", "35px", "none"), "1": ("50%", "50%", "20px", "45px", ""), "max": ("75%", "25%", "0px", "55px", "")}

            if size >= 2:
                size = "max"

            if not str(size) in sizeMap:
                return None

            el = document.getElementById(f'SubPage_page_art')
            if not el is None:
                el.style.width = sizeMap[str(size)][0]
                el.style.display = sizeMap[str(size)][4]

            el = document.getElementById(f'SubPage_page_que')
            if not el is None:
                el.style.width = sizeMap[str(size)][1]
                el.style.marginBottom = sizeMap[str(size)][2]

            el = document.getElementById(f'SubPage_page_queAdd')
            if not el is None:
                el.style.minHeight = sizeMap[str(size)][3]

        page = window.localStorage.getItem(f'page_index')
        if page == "Portal":
            page = window.localStorage.getItem(f'page_portal')

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

    def sheet(data: dict): #, dates: tuple, halfView: tuple, excludeView: tuple, disabledInputs: tuple, invokePasswordOnChange: tuple, optionsList: tuple, tagIsList: bool, extraButtons: tuple, comMap: tuple):
        def getLines(data):
            headers = []
            for key in data:
                for item in data[key]:
                    if item in headers:
                        continue

                    headers.append(item)

            lines = [["Tag"] + headers]
            for key in data:
                line = [key]
                for header in headers:
                    if not header in data[key]:
                        line.append(None)
                        continue
                    line.append(data[key][header])

                lines.append(line)

            return lines

        lines = getLines(data)
        return lines

    def graph(name: str, rowHeight: str, rows: int, rowStep: int, cols: int, colStep: int = None, origin: tuple = (), rowPrefix: str = "", rowAfterfix: str = "", colNames: tuple = ()):
        htmlRows = ""
        for i1 in range(0, rows):
            borderStyle = ""
            if i1 > 0:
                borderStyle = f' border-top: 2px dashed #111;'

            txt = bridge.HTML.add(f'h1', _nest=f'{rowPrefix}{(rows - i1) * rowStep}{rowAfterfix}', _style=f'headerSmall %% height: 25%; margin: 0px auto auto auto;')
            if i1 == rows - 1:
                txt += bridge.HTML.add(f'h1', _style=f'headerSmall %% height: 40%; margin: auto auto auto auto;')
                txt += bridge.HTML.add(f'h1', _nest=f'{rowPrefix}{(rows - i1 - 1) * rowStep}{rowAfterfix}', _style=f'headerSmall %% height: 25%; margin: auto auto auto 5px;')

            htmlCols = bridge.HTML.add(f'div', _nest=txt, _id=f'{name}_row_{rows - i1 - 1}_col_header', _style=f'background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 2px solid #111;{borderStyle}')
            for i2 in range(0, cols):
                if i2 == cols - 1:
                    htmlCols += bridge.HTML.add(f'div', _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {100 / cols}%; height: {rowHeight};{borderStyle}')
                else:
                    htmlCols += bridge.HTML.add(f'div', _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {100 / cols}%; height: {rowHeight}; border-right: 1px dashed #111;{borderStyle}')

            htmlRows += bridge.HTML.add(f'div', _nest=htmlCols, _id=f'{name}_row_{rows - i1 - 1}', _style=f'flex %% width: 100%; height: {rowHeight};')

        txt = ""
        if len(origin) == 1:
            txt += bridge.HTML.add(f'h1', _nest=f'{origin[0]}', _style=f'headerSmall %% margin: auto;')
        elif len(origin) > 1:
            txt += bridge.HTML.add(f'h1', _nest=f'{origin[0]}', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: left;')
            txt += bridge.HTML.add(f'h1', _nest=f'/', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: center;')
            txt += bridge.HTML.add(f'h1', _nest=f'{origin[1]}', _style=f'headerSmall %% margin: 0px 5%; width: 90%; text-align: right;')

        htmlCols = bridge.HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_header', _style=f'background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 2px solid #111; border-top: 2px solid #111;')
        for i2 in range(0, cols):
            try:
                txt = bridge.HTML.add(f'h1', _nest=f'{colNames[i2]}', _style=f'headerSmall %% margin: auto;')
            except IndexError:
                txt = bridge.HTML.add(f'h1', _nest=f'', _style=f'headerSmall %% margin: auto;')

            if i2 == cols - 1:
                htmlCols += bridge.HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-top: 2px solid #111;')
            else:
                htmlCols += bridge.HTML.add(f'div', _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {100 / cols}%; height: {rowHeight}; border-right: 1px dashed #111; border-top: 2px solid #111;')

        htmlRows += bridge.HTML.add(f'div', _nest=htmlCols, _id=f'{name}_row_header', _style=f'flex %% width: 100%; height: {rowHeight};')

        return bridge.HTML.add(f'div', _nest=htmlRows, _id=f'{name}', _style=f'margin: 10px; padding-bottom: 2px; border: 2px solid #111;')

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
                    bridge.HTML.add(
                        f'div',
                        f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                        _style=
                        f'z-index: 10; width: 10px; height: 10px; margin: -5px; background: #55F; border-radius: 10px; position: relative; top: {95 - int(rowFloat[:2] + "0" * (2 - len(rowFloat[:2])))}%; left: {-5 + int(colFloat[:2] + "0" * (2 - len(colFloat[:2])))}%'
                    )
                else:
                    vw = "-25vw"
                    if int(colNum) < 4:
                        vw = "0.5vw"

                    vh = "0.5vh"
                    if int(rowNum) < 3:
                        vh = "-25vh"

                    txt = bridge.HTML.add(f'h1', _nest=f'{onHoverTxt}', _style=f'headerSmall %% white-space: nowrap; text-overflow: ellipsis;')
                    details = bridge.HTML.add(f'div',
                                              _nest=txt,
                                              _id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHoverTxt',
                                              _style=f'divNormal %% z-index: 12; width: 0vw; height: 25vh; margin: {vh} 0px 0px {vw}; padding: 0px; position: relative; opacity: 0%; transition: width 0.25s, opacity 0.5s; overflow-x: hidden;')
                    bridge.HTML.add(
                        f'div',
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

            JS.graphDraw(name, steps, lineRes=lineRes, disalowRecursive=True)

        for id in addOnHovers:
            el = document.getElementById(id)
            el.addEventListener(f'mouseover', create_proxy(mouseover))
            el.addEventListener(f'mouseout', create_proxy(mouseout))


class WS:
    PROTO = ""
    IP = ""
    PORT = ""
    PK = ""

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

            if msg.split(f' ')[0] in WS.msgReply:
                msg = msg.split(f' ')[0]

                if callable(WS.msgReply[msg][0]):
                    WS.msgReply[msg][0]()
                    return None
                WS.ws.send(WS.msgReply[msg][0])

                if WS.msgReply[msg][1]:
                    WS.msgReply.pop(msg)

        error = lambda arg=None: (console.error(arg), WS.close)
        close = lambda arg=None: WS.on.connectionError("The connection to the server was lost!")

        def login(arg=None):
            WS.PK = PublicKey.load_pkcs1(f'{WS.msg().split("<LOGIN> ")[1]}')

            if window.localStorage.getItem("token") == "" or WS.reconnectTries > 4:
                return None

            WS.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')

        def connectionError(msg: str):
            def loginTokenSucces():
                WS.ws.send(f'access')

                for msg in WS.afterReconnect:
                    WS.ws.send(msg)

                WS.afterReconnect = []

            def loginTokenFail():
                WS.reconnectTries = 99
                WS.on.connectionError("Unable to reconnect to the server, token authetication failed!")

            if not WS.loggedIn:
                return None

            if window.localStorage.getItem("token") == "" or WS.reconnectTries > 4:
                bridge.HTML.enable("page_Portal", False)

                bridge.HTML.set(f'div', f'page', _id=f'page_error', _align=f'center')
                bridge.HTML.set(f'h1', f'page_error', _nest=f'WARNING!', _style=f'headerVeryBig')
                bridge.HTML.add(f'p', f'page_error', _nest=f'Connection lost to the server! {msg}')
                bridge.HTML.add(f'p', f'page_error', _nest=f'Please refresh the page to try again.')

                return None

            WS.ws = None
            WS.reconnectTries += 1

            WS.onMsg(f'<LOGIN_TOKEN_SUCCESS>', loginTokenSucces, oneTime=True)
            WS.onMsg(f'<LOGIN_TOKEN_FAIL>', loginTokenFail, oneTime=True)

            WS.start(WS.PROTO, WS.IP, WS.PORT)

    state = lambda: True if WS.ws.readyState in [0, 1] else False
    msg = lambda: (WS.close() if not WS.ws.readyState in [0, 1] else None, WS.lastMsg)[-1]
    dict = lambda: (WS.close() if not WS.ws.readyState in [0, 1] else None, WS.msgDict)[-1]

    def start(protocol: str, ip: str, port: str):
        if not WS.ws is None:
            WS.close()
            WS.ws = None

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


class bridge:
    class HTML:
        def enable(id: str, state: bool = True):
            return HTML.enable(id, state)

        def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
            return HTML.set(type, id, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

        def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
            return HTML.add(type, id, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

    class CSS:
        onHoverStyles = lambda: CSS.onHoverStyles
        onClickStyles = lambda: CSS.onClickStyles
        onFocusStyles = lambda: CSS.onFocusStyles