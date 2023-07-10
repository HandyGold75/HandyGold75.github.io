from js import document, window, setTimeout
from pyodide.ffi import create_proxy, create_once_callable # type: ignore
from WebKit import HTML, CSS, JS, WS
from datetime import datetime
from rsa import encrypt


def raiseError(header: str, msg: str, disableIds: list = ()):
    for id in disableIds:
        HTML.enable(str(id), False)

    error = HTML.add("h1", _nest="WARNING!", _style="headerVeryBig")
    for line in msg.split("\n"):
        error = HTML.add("p", _nest=str(line))

    HTML.set("div", "page", _nest=error, _id="page_error", _align="center")


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
        sheet(maincom=maincom, name=name, data=data, elId=elId, dates=dates, halfView=halfView, excludeView=excludeView, typeDict=typeDict, optionsDict=optionsDict, showAction=showAction, showTag=showTag, index=index + 1)

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
        HTML.add("div", elId, _id=f'{maincom}_{name}', _style="margin: 10px; border: 2px solid #111;")
        HTML.add(f'button', elId, _id=f'{maincom}_{name}_loadMore', _nest=f'Load more (0 / {len(lines)})', _type=f'button', _style=f'buttonBig %% width: 50%;')
        document.getElementById(f'{maincom}_{name}_loadMore').addEventListener("click", create_proxy(recursion))
        CSS.onHoverClick(f'{maincom}_{name}_loadMore', f'buttonHover', f'buttonClick')

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

            txt = HTML.add("p", _id=f'{maincom}_{name}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')

            if lineIndex != 0 and valueIndex != 0:
                cols += HTML.add("div", _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}', _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')
                eventConfig["editIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')
                if valueType in ["str", "list", "tuple"]:
                    eventConfig["popupIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

            elif lineIndex != 0:
                cols += HTML.add("div", _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}', _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')
                if valueType in ["str", "list", "tuple"]:
                    eventConfig["popupIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

            else:
                cols += HTML.add("div", _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;{borderRight}')

            if valueIndex + 1 < len(line) or not showAction:
                continue

            if lineIndex == 0:
                valueType, value, key = ("none", "Action", "Action")
                txt = HTML.add("p", _id=f'{maincom}_{name}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                cols += HTML.add("div", _nest=txt, _style=f'width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; overflow: hidden;')
                continue

            valueType, value, key = ("rem", "Remove", "Action")
            btn = HTML.add("button",
                           _id=f'{maincom}_{name}_{tag}_{key}_{valueType}',
                           _nest=value,
                           _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -6px; background: #333; color: #BFF;')
            cols += HTML.add("div",
                             _nest=btn,
                             _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden; margin: 0px -2px 0px 0px;')
            eventConfig["actionIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

        if not elId is None:
            HTML.add("div", f'{maincom}_{name}', _nest=cols, _style=f'flex %%{(lambda: " height: 29px;" if lineIndex == 0 else "")()}{background}{borderBottom}')
            HTML.setRaw(f'{maincom}_{name}_loadMore', f'Load more ({lineIndex} / {len(lines)})')
            if lineIndex > 100:
                document.getElementById(f'{maincom}_{name}_loadMore').scrollIntoView()
        else:
            rows += HTML.add("div", _nest=cols, _style=f'flex %%{(lambda: " height: 29px;" if lineIndex == 0 else " height: 21px;")()}{background}{borderBottom}')

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

            txt = HTML.add(main,
                           _id=f'Input_{maincom}_{name}_{tag}_{key}_{valueType}',
                           _class=f'Input_{maincom}_{name}_{tag}',
                           _nest=nest,
                           _type=typ,
                           _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center;{styleInp}',
                           _custom=f'placeholder="{value}"{custom}')
            cols += HTML.add("div",
                             _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}',
                             _nest=txt,
                             _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; border: 2px solid #55F; border-radius: 0px;{styleDiv}{margin}')
            eventConfig["inputIds"].append(f'Input_{maincom}_{name}_{tag}_{key}_{valueType}')

            if valueIndex + 1 < len(line):
                continue

            valueType, value, key = "add", "Add", "Action"
            btn = HTML.add("button",
                           _id=f'{maincom}_{name}_{tag}_{key}_{valueType}',
                           _nest=value,
                           _style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -1px; background: #333; color: #BFF')
            cols += HTML.add("div",
                             _id=f'Div_{maincom}_{name}_{tag}_{key}_{valueType}',
                             _nest=btn,
                             _style=f'z-index: 111; width: {(lambda: defaultWidth / 2 if key in halfView else defaultWidth)()}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden;{styleDiv}{margin}')
            eventConfig["actionIds"].append(f'{maincom}_{name}_{tag}_{key}_{valueType}')

        if not elId is None:
            HTML.add("div", f'{maincom}_{name}', _nest=cols, _style=f'flex %% height: 29px; background: #202020;{borderBottom}')
        else:
            rows += HTML.add("div", _nest=cols, _style=f'flex %% height: 29px; background: #202020;{borderBottom}')

    if not elId is None and index + 1 < len(lines):
        if index % 100 == 0 and not index == 0:
            document.getElementById(f'{maincom}_{name}_loadMore').addEventListener("click", create_proxy(recursion))
            CSS.onHoverClick(f'{maincom}_{name}_loadMore', f'buttonHover', f'buttonClick')
            return None
        setTimeout(create_once_callable(recursion), 0)

    elif not elId is None:
        return eventConfig

    return (HTML.add("div", _id=f'{maincom}_{name}', _nest=rows, _style="margin: 10px; border: 2px solid #111;"), eventConfig)


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
                    psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.glb.pub)) if key == "User" else str(encrypt(psw.encode(), WS.glb.pub)).replace(" ", "%20"))()
                    WS.send(f'{maincom} rpwmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {pswChangeDict[key].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')

            else:
                if tag in pswChangeDict:
                    psw = JS.popup(f'prompt', "Please enter the new password for the user.")
                    if psw is None or psw == "":
                        return None
                    psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.glb.pub)) if tag == "User" else str(encrypt(psw.encode(), WS.glb.pub)).replace(" ", "%20"))()
                    WS.send(f'{maincom} kpwmodify {sheet.replace(" ", "%20")} {pswChangeDict[tag].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

            txt = HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

        def submitDate(args):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = int(datetime.strptime(el.value, "%Y-%m-%d").timestamp())

            if sendKey:
                WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

            value = datetime.fromtimestamp(value).strftime("%d %b %y")
            txt = HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

        def submitNumber(args):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = (lambda: float(el.value) if valueType == "float" else int(el.value))()

            if sendKey:
                WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

            txt = HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(onContextMenu))

        def submitBool(args):
            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = not (lambda: False if el.innerHTML == "No" else True)()

            if sendKey:
                WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

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
                WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')
            else:
                WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

            pel = el.parentElement
            for style in ("z-index", "margin-bottom", "min-height", "color", "background", "overflow", "scrollbar-width", "transition", "margin-bottom", "min-height"):
                setattr(pel.style, style, "")

            txt = HTML.add("p", _id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', _nest=str(value), _style=f'font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
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

        txt = HTML.add(main,
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
            CSS.onHoverFocus(pel.id, "selectHover %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;", "selectFocus %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;")
            document.getElementById(pel.id).addEventListener("keyup", create_proxy(submitList))
            return None

        CSS.onHoverFocus(f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}', "inputHover", "inputFocus")
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
                WS.send(f'{maincom} add {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}')
                continue

            from subs.portal_sheets import pageSub
            WS.onMsg("{\"" + maincom + "\":", pageSub, oneTime=True)
            WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')

    def remRecord(args):
        maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

        if not JS.popup("confirm", f'Are you sure you want to delete "{tag}"?\nThis can not be reverted!'):
            return None

        from subs.portal_sheets import pageSub
        WS.onMsg("{\"" + maincom + "\":", pageSub, oneTime=True)
        WS.send(f'{maincom} delete {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}')

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
            CSS.onHoverFocus(el.id, "selectHover %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;", "selectFocus %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;")
        else:
            CSS.onHoverFocus(el.id, "inputHover", "inputFocus")

    for id in eventConfig["actionIds"]:
        el = document.getElementById(id)
        if el is None:
            return None

        maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]

        (lambda: document.getElementById(el.id).addEventListener("click", create_proxy(remRecord)) if valueType == "rem" else document.getElementById(el.id).addEventListener("click", create_proxy(addRecord)))()
        CSS.onHoverClick(el.id, "buttonHover", "buttonClick")

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

        txt = HTML.add("h1", _nest=f'{rowPrefix}{(rows - i1) * rowStep}{rowAfterfix}', _style="headerSmall %% height: 25%; margin: 0px auto auto auto;")
        if i1 == rows - 1:
            txt += HTML.add("h1", _style="headerSmall %% height: 40%; margin: auto auto auto auto;")
            txt += HTML.add("h1", _nest=f'{rowPrefix}{(rows - i1 - 1) * rowStep}{rowAfterfix}', _style="headerSmall %% height: 25%; margin: auto auto auto 5px;")

        htmlCols = HTML.add("div", _nest=txt, _id=f'{name}_row_{rows - i1 - 1}_col_header', _style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeight}; border-right: 2px solid #111;{borderStyle}')
        for i2 in range(0, cols):
            if i2 == cols - 1:
                htmlCols += HTML.add("div", _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight};{borderStyle}')
            else:
                htmlCols += HTML.add("div", _id=f'{name}_row_{rows - i1 - 1}_col_{i2}', _style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight}; border-right: 1px dashed #111;{borderStyle}')

        htmlRows += HTML.add("div", _nest=htmlCols, _id=f'{name}_row_{rows - i1 - 1}', _style=f'flex %% width: 100%; height: {rowHeight};')

    txt = ""
    if not smallHeaders:
        if len(origin) == 1:
            txt += HTML.add("h1", _nest=f'{origin[0]}', _style="headerSmall %% margin: auto;")
        elif len(origin) > 1:
            txt += HTML.add("h1", _nest=f'{origin[0]}', _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: left;")
            txt += HTML.add("h1", _nest="/", _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: center;")
            txt += HTML.add("h1", _nest=f'{origin[1]}', _style="headerSmall %% margin: 0px 5%; width: 90%; text-align: right;")

    htmlCols = HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_header', _style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeightSmall}; border-right: 2px solid #111; border-top: 2px solid #111;')
    for i2 in range(0, cols):
        try:
            txt = HTML.add("h1", _nest=f'{colNames[i2]}', _style="headerSmall %% margin: auto;")
        except IndexError:
            txt = HTML.add("h1", _nest="", _style="headerSmall %% margin: auto;")

        if i2 == cols - 1:
            htmlCols += HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-top: 2px solid #111;')
        else:
            htmlCols += HTML.add("div", _nest=txt, _id=f'{name}_row_header_col_{i2}', _style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-right: 1px dashed #111; border-top: 2px solid #111;')

    htmlRows += HTML.add("div", _nest=htmlCols, _id=f'{name}_row_header', _style=f'flex %% width: 100%; height: {rowHeightSmall};')

    return HTML.add("div", _nest=htmlRows, _id=name, _style="margin: 10px; padding-bottom: 2px; border: 2px solid #111;")


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
                HTML.add(
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

                txt = HTML.add("h1", _nest=onHoverTxt, _style="headerSmall %% white-space: nowrap; text-overflow: ellipsis;")
                details = HTML.add("div",
                                   _nest=txt,
                                   _id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHoverTxt',
                                   _style=f'divNormal %% z-index: 12; width: 0vw; height: 25vh; margin: {vh} 0px 0px {vw}; padding: 0px; position: relative; opacity: 0%; transition: width 0.25s, opacity 0.5s; overflow-x: hidden;')
                HTML.add(
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

        graphDraw(name, steps, lineRes=lineRes, disalowRecursive=True)

    for id in addOnHovers:
        el = document.getElementById(id)
        el.addEventListener("mouseover", create_proxy(mouseover))
        el.addEventListener("mouseout", create_proxy(mouseout))


def ytVideo(name: str):
    img = HTML.add(f'img', _style=f'z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'src="docs/assets/Widgets/Transparent.png" alt="Black"')
    img = HTML.add(f'div', _nest=f'{img}', _id=f'{name}_img', _style=f'margin-bottom: -56.25%; position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;')

    ifr = HTML.add(f'div', _id=f'{name}_ifr', _style=f'position: absolute; top: 0; left: 0; width: 100%; height: 100%;', _custom=f'frameborder="0"')
    ifr = HTML.add(f'div', _nest=f'{ifr}', _id=f'{name}_div', _style=f'position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;')
    
    return HTML.add(f'div', _nest=f'{img}{ifr}', _id=f'{name}', _style=f'divNormal %% width: 75%; margin: 0px auto;')

def ytVideoGetControl(name):
    return JS.jsEval("new YT.Player('" + str(name) + "_ifr', { videoId: '', playerVars: { 'autoplay': 0, 'controls': 0, 'disablekb': 1, 'fs': 0, 'iv_load_policy': 3, 'modestbranding': 1, 'rel': 0 } } );")