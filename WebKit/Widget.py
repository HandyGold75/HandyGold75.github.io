from js import document, window, setTimeout, console
from pyodide.ffi import create_proxy, create_once_callable # type: ignore
from WebKit.init import HTML, CSS, JS, WS
from datetime import datetime
from rsa import encrypt


def raiseError(header: str, msg: str, disableIds: list = ()):
    for id in disableIds:
        HTML.disableElement(str(id))

    error = HTML.genElement("h1", nest=str(header), style="headerVeryBig")
    for line in msg.split("\n"):
        error = HTML.genElement("p", nest=str(line))

    HTML.setElement("div", "page", nest=error, id="page_error", align="center")


class sheet:
    __all__ = ["generate", "generateEvents"]

    def __init__(self,
                 maincom: str,
                 name: str,
                 elId: str = None,
                 dates: tuple = (),
                 halfView: list = [],
                 quarterView: list = [],
                 excludeView: tuple = (),
                 typeDict: dict = {},
                 optionsDict: dict = {},
                 pswChangeDict: dict = {},
                 sendKey: bool = True,
                 showInput: bool = True,
                 showAction: bool = True,
                 showTag: bool = True,
                 tagIsList: bool = True,
                 wordWrap: bool = False):
        self.maincom = maincom
        self.name = name
        self.elId = elId
        self.dates = dates
        self.halfView = halfView
        self.quarterView = quarterView
        self.excludeView = excludeView
        self.typeDict = typeDict
        self.optionsDict = optionsDict
        self.pswChangeDict = pswChangeDict
        self.sendKey = sendKey
        self.showInput = showInput
        self.showAction = showAction
        self.showTag = showTag
        self.tagIsList = tagIsList
        self.wordWrap = wordWrap

        self.index = 0
        self.defaultWidth = 0
        self.eventConfig = {}
        self.fastLoad = False
        self.loadCountPerLoad = 100
        self.rememberRows = ""

    def recursion(self):
        el = document.getElementById(f'{self.maincom}_{self.name}_loadMore')
        if el is None:
            return None

        el.outerHTML = el.outerHTML
        self.index += 1
        self.generate(False)

    def prepareData(self, data):
        headers = []
        for key in data:
            for item in data[key]:
                (lambda: None if item in headers or item in self.excludeView else headers.append(item))()

        lines = [["Tag"] + headers]
        for key in data:
            line = [key]
            for header in headers:
                (lambda: line.append(None) if not header in data[key] else line.append(data[key][header]))()
            lines.append(line)
        self.lines = lines

        halfViewTmp = (lambda: ["Action"] if self.showAction and "Action" in self.halfView else [])()
        for key in list(self.halfView):
            if key in self.lines[0]:
                halfViewTmp.append(key)
        self.halfView = halfViewTmp

        quarterViewTmp = (lambda: ["Action"] if self.showAction and "Action" in self.quarterView else [])()
        for key in list(self.quarterView):
            if key in self.lines[0] and not key in self.halfView:
                quarterViewTmp.append(key)
        self.quarterView = quarterViewTmp

        self.defaultWidth = 100 / (len(self.lines[0]) + self.showAction - (not self.showTag) - (len(self.halfView) * 0.5) - (len(self.quarterView) * 0.75))

    def getInputRow(self, tag, line, lineIndex):
        def getAdaptiveWidth(key):
            if key in self.halfView:
                return self.defaultWidth / 2
            elif key in self.quarterView:
                return self.defaultWidth / 4
            return self.defaultWidth

        cols = ""
        for valueIndex, value in enumerate(line):
            key = self.lines[0][valueIndex]
            margin = (lambda: " margin: 0px -2px;" if valueIndex == 0 else " margin: 0px -2px 0px 0px;")()

            try:
                valueType = (lambda: type(self.typeDict[key]).__name__ if key in self.typeDict else type(self.lines[1][valueIndex]).__name__)()
            except IndexError:
                valueType = "NoneType"

            main, typ, custom, nest, styleInp, styleDiv = ("input", "text", "", "", " height: 100%; top: -1px; background: #333; color: #BFF; overflow: hidden;", " overflow: hidden;")
            if valueType == "NoneType":
                typ = "text"
            elif key in self.dates and valueType in ("int", "float"):
                typ, custom, valueType = ("date", f' value="{datetime.now().strftime("%Y-%m-%d")}"', "date")
            elif valueType in ("int", "float"):
                typ = "number"
            elif valueType == "bool":
                typ, custom, styleInp = ("checkbox", " checked", " height: 75%; top: 1px; background: #333; color: #BFF; overflow: hidden;")
            elif valueType in ["list", "tuple"]:
                main, typ, custom, styleInp, styleDiv = ("select", "", " size=\"1\" multiple", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;", " background: #333; color: #BFF; overflow: hidden;")

                allData = []
                if key in self.optionsDict:
                    allData = self.optionsDict[key]
                elif f'/{key}.json' in self.optionsDict:
                    allData = self.optionsDict[f'/{key}.json']

                for option in allData:
                    nest += HTML.genElement("option", nest=option, style="margin: 0px 1px; background: transparent; color: inherit;", custom=f'value="{option}"')

            if valueIndex == 0 and self.tagIsList:
                valueType = "str"
                main, typ, custom, styleInp, styleDiv = ("select", "", " size=\"1\"", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;", " background: #333; color: #BFF; overflow: hidden;")

                allData = []
                if key in self.optionsDict:
                    allData = self.optionsDict[key]
                elif f'/{key}.json' in self.optionsDict:
                    allData = self.optionsDict[f'/{key}.json']

                for option in allData:
                    nest += HTML.genElement("option", nest=option, style="margin: 0px 1px; background: transparent; color: inherit;", custom=f'value="{option}"')

            txt = HTML.genElement(main,
                                  id=f'Input_{self.maincom}_{self.name}_{tag}_{key}_{valueType}',
                                  classes=f'Input_{self.maincom}_{self.name}_{tag}',
                                  nest=nest,
                                  type=typ,
                                  style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center;{styleInp}',
                                  custom=f'placeholder="{value}"{custom}')
            cols += HTML.genElement("div", id=f'Div_{self.maincom}_{self.name}_{tag}_{key}_{valueType}', nest=txt, style=f'z-index: 111; width: {getAdaptiveWidth(key)}%; min-height: 0px; border: 2px solid #55F; border-radius: 0px;{styleDiv}{margin}')
            self.eventConfig["inputIds"].append(f'Input_{self.maincom}_{self.name}_{tag}_{key}_{valueType}')

            if valueIndex + 1 < len(line):
                continue

            valueType, value, key = "add", "Add", "Action"
            btn = HTML.genElement("button",
                                  id=f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}',
                                  nest=value,
                                  style="z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -1px; background: #333; color: #BFF")
            cols += HTML.genElement("div",
                                    id=f'Div_{self.maincom}_{self.name}_{tag}_{key}_{valueType}',
                                    nest=btn,
                                    style=f'z-index: 111; width: {getAdaptiveWidth(key)}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden;{styleDiv}{margin}')
            self.eventConfig["actionIds"].append(f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}')

        borderBottom = (lambda: "" if lineIndex + 1 >= len(self.lines) else " border-bottom: 2px solid #111;")()
        return HTML.genElement("div", nest=cols, style=f'flex %% height: 29px; background: #202020;{borderBottom}')

    def getRow(self, tag, line, lineIndex):
        def getAdaptiveWidth(key):
            if key in self.halfView:
                return self.defaultWidth / 2
            elif key in self.quarterView:
                return self.defaultWidth / 4
            return self.defaultWidth

        cols = ""
        for valueIndex, value in enumerate(line):
            borderRight = (lambda: "" if valueIndex + 1 >= len(line) and not self.showAction else " border-right: 2px solid #111;")()
            key = self.lines[0][valueIndex]

            if key == "Tag" and not self.showTag:
                continue

            valueType = (lambda: type(self.typeDict[key]).__name__ if key in self.typeDict else type(value).__name__)()

            if key in self.dates and type(value) in (int, float):
                value = datetime.fromtimestamp(value).strftime("%d %b %y")
                valueType = "date"
            elif type(value) is bool:
                value = (lambda: "Yes" if value else "No")()
            elif type(value) in [list, tuple]:
                value = ", ".join(value)
            elif type(value) is type(None):
                value = ""

            fontStyle = (lambda: "headerSmall %% " if lineIndex == 0 else "font-size: 75%; ")()
            txt = HTML.genElement("p", id=f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}', nest=str(value), style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')

            if lineIndex != 0 and valueIndex != 0:
                cols += HTML.genElement("div", id=f'Div_{self.maincom}_{self.name}_{tag}_{key}_{valueType}', nest=txt, style=f'width: {getAdaptiveWidth(key)}%; overflow: hidden;{borderRight}')
                self.eventConfig["editIds"].append(f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}')
                if valueType in ["str", "list", "tuple"]:
                    self.eventConfig["popupIds"].append(f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}')

            elif lineIndex != 0:
                cols += HTML.genElement("div", id=f'Div_{self.maincom}_{self.name}_{tag}_{key}_{valueType}', nest=txt, style=f'width: {getAdaptiveWidth(key)}%; overflow: hidden;{borderRight}')
                if valueType in ["str", "list", "tuple"]:
                    self.eventConfig["popupIds"].append(f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}')

            else:
                cols += HTML.genElement("div", nest=txt, style=f'width: {getAdaptiveWidth(key)}%; overflow: hidden;{borderRight}')

            if valueIndex + 1 < len(line) or not self.showAction:
                continue

            if lineIndex == 0:
                valueType, value, key = ("none", "Action", "Action")
                txt = HTML.genElement("p", id=f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}', nest=str(value), style=f'{fontStyle}height: 100%; margin: 0px; padding: 1px 0px 2px 0px;')
                cols += HTML.genElement("div", nest=txt, style=f'width: {getAdaptiveWidth(key)}%; overflow: hidden;')
                continue

            valueType, value, key = ("rem", "Remove", "Action")
            btn = HTML.genElement("button",
                                  id=f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}',
                                  nest=value,
                                  style="z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center; overflow: hidden; height: 100%; top: -6px; background: #333; color: #BFF;")
            cols += HTML.genElement("div", nest=btn, style=f'z-index: 111; width: {getAdaptiveWidth(key)}%; min-height: 0px; background: #212121; border: 2px solid #55F; border-radius: 0px; overflow: hidden; margin: 0px -2px 0px 0px;')
            self.eventConfig["actionIds"].append(f'{self.maincom}_{self.name}_{tag}_{key}_{valueType}')

        background = (lambda: " background: #191919;" if lineIndex == 0 else " background: #202020;")()
        borderBottom = (lambda: "" if lineIndex + 1 >= len(self.lines) else " border-bottom: 2px solid #111;")()
        wrapStyle = " word-break: break-all;" if self.wordWrap else " height: 21px;"
        return HTML.genElement("div", nest=cols, id=f'DivRow_{self.maincom}_{self.name}_{tag}', style=f'flex %%{(lambda: " height: 29px;" if lineIndex == 0 else wrapStyle)()}{background}{borderBottom}')

    def getAllRows(self):
        rows = ""
        for lineIndex, line in (lambda: enumerate(self.lines) if self.elId is None else enumerate([self.lines[self.index]]))():
            if not self.elId is None:
                lineIndex = self.index

            tag = line[0]

            row = self.getRow(tag, line, lineIndex)
            rows += row
            if not self.elId is None:
                if not self.fastLoad:
                    HTML.addElementRaw(f'{self.maincom}_{self.name}', row)
                HTML.setElementRaw(f'{self.maincom}_{self.name}_loadMore', f'Load more ({lineIndex} / {len(self.lines)})')

            if lineIndex != 0 or not self.showInput:
                continue

            row = self.getInputRow(tag, line, lineIndex)
            rows += row
            if not self.elId is None and not self.fastLoad:
                HTML.addElementRaw(f'{self.maincom}_{self.name}', row)

        return rows

    def generate(self, data, rememberRows: str = None):
        if not data is False:
            self.prepareData(data)

            if not self.elId is None and self.index == 0:
                HTML.addElement("div", self.elId, id=f'{self.maincom}_{self.name}', style="margin: 10px; border: 2px solid #111;")
                HTML.addElement("button", self.elId, id=f'{self.maincom}_{self.name}_loadMore', nest=f'Load more (0 / {len(self.lines)})', type="button", style="buttonBig %% width: 50%;")
                document.getElementById(f'{self.maincom}_{self.name}_loadMore').addEventListener("click", create_proxy(lambda element=None: self.recursion()))
                CSS.onHoverClick(f'{self.maincom}_{self.name}_loadMore', "buttonHover", "buttonClick")

        self.eventConfig = {"editIds": [], "inputIds": [], "actionIds": [], "popupIds": []}
        rows = self.getAllRows()

        if not self.elId is None:
            if self.index + 1 >= len(self.lines):
                if self.fastLoad:
                    self.rememberRows += rows
                    HTML.addElementRaw(f'{self.maincom}_{self.name}', self.rememberRows)
                    HTML.setElementRaw(f'{self.maincom}_{self.name}_loadMore', f'Load more ({self.index + 1} / {len(self.lines)})')
                    HTML.disableElement(f'{self.maincom}_{self.name}_loadMore')
                    self.rememberRows = ""
                return None

            if self.fastLoad:
                self.rememberRows += rows

            if self.index % self.loadCountPerLoad == 0 and not self.index == 0:
                document.getElementById(f'{self.maincom}_{self.name}_loadMore').addEventListener("click", create_proxy(lambda element=None: self.recursion()))
                CSS.onHoverClick(f'{self.maincom}_{self.name}_loadMore', "buttonHover", "buttonClick")

                if self.fastLoad:
                    HTML.addElementRaw(f'{self.maincom}_{self.name}', self.rememberRows)
                    self.rememberRows = ""

                self.fastLoad = True
                self.loadCountPerLoad = 1000
                return None

            setTimeout(create_once_callable(lambda element=None: self.recursion()), 1)

        return HTML.genElement("div", id=f'{self.maincom}_{self.name}', nest=rows, style="margin: 10px; border: 2px solid #111;")

    def onContextMenu(self, args, onSubmit: object = None):
        def submit(args, callFunc: object = None):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = el.value

            if self.sendKey:
                if key in self.pswChangeDict:
                    psw = JS.popup("prompt", "Please enter the new password -for the user.")
                    if psw is None or psw == "":
                        return None
                    psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.pub)) if key == "User" else str(encrypt(psw.encode(), WS.pub)).replace(" ", "%20"))()

                    if not callFunc is None:
                        callFunc(self.pswChangeDict[key], psw)
                    else:
                        WS.send(f'{maincom} rpwmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {self.pswChangeDict[key].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                if not callFunc is None:
                    callFunc(key, value)
                else:
                    WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')

            else:
                if tag in self.pswChangeDict:
                    psw = JS.popup("prompt", "Please enter the new password for the user.")
                    if psw is None or psw == "":
                        return None
                    psw = (lambda: str(encrypt(value.encode() + "<SPLIT>".encode() + psw.encode(), WS.pub)) if tag == "User" else str(encrypt(psw.encode(), WS.pub)).replace(" ", "%20"))()

                    if not callFunc is None:
                        callFunc(self.pswChangeDict[tag], psw)
                    else:
                        WS.send(f'{maincom} kpwmodify {sheet.replace(" ", "%20")} {self.pswChangeDict[tag].replace(" ", "%20")} {psw.replace(" ", "%20")}')

                if not callFunc is None:
                    callFunc(tag, value)
                else:
                    WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

            txt = HTML.genElement("p", id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', nest=str(value), style="font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;")
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(lambda args: self.onContextMenu(args, onSubmit)))

        def submitDate(args, callFunc: object = None):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = int(datetime.strptime(el.value, "%Y-%m-%d").timestamp())

            if self.sendKey:
                if not callFunc is None:
                    callFunc(key, value)
                else:
                    WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                if not callFunc is None:
                    callFunc(tag, value)
                else:
                    WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

            value = datetime.fromtimestamp(value).strftime("%d %b %y")
            txt = HTML.genElement("p", id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', nest=str(value), style="font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;")
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(lambda args: self.onContextMenu(args, onSubmit)))

        def submitNumber(args, callFunc: object = None):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = (lambda: float(el.value) if valueType == "float" else int(el.value))()

            if self.sendKey:
                if not callFunc is None:
                    callFunc(key, value)
                else:
                    WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                if not callFunc is None:
                    callFunc(tag, value)
                else:
                    WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

            txt = HTML.genElement("p", id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', nest=str(value), style="font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;")
            el.parentElement.innerHTML = txt
            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(lambda args: self.onContextMenu(args, onSubmit)))

        def submitBool(args, callFunc: object = None):
            el = document.getElementById(args.target.id)
            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]
            value = not (lambda: False if el.innerHTML == "No" else True)()

            if self.sendKey:
                if not callFunc is None:
                    callFunc(key, value)
                else:
                    WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value}')
            else:
                if not callFunc is None:
                    callFunc(tag, value)
                else:
                    WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value}')

            if value:
                el.innerHTML = "Yes"
                return None
            el.innerHTML = "No"

        def submitList(args, callFunc: object = None):
            if not args.key in ["Enter", "Escape"]:
                return None

            el = document.getElementById(args.target.id.replace("Div_", "Input_"))
            maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

            value = []
            for subEls in list(args.target.childNodes):
                if subEls.selected is True:
                    value.append(subEls.value.replace(", ", ","))
            value = ", ".join(value)

            if self.sendKey:
                if not callFunc is None:
                    callFunc(key, value.split(", "))
                else:
                    WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}')
            else:
                if not callFunc is None:
                    callFunc(tag, value.split(", "))
                else:
                    WS.send(f'{maincom} kmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {value.replace(" ", "%20")}')

            pel = el.parentElement
            txt = HTML.genElement("p", id=f'{maincom}_{sheet}_{tag}_{key}_{valueType}', nest=str(value), style="font-size: 75%; height: 100%; margin: 0px; padding: 1px 0px 2px 0px;")
            pel.innerHTML = txt
            for style in ("color", "background", "transition"):
                setattr(pel.style, style, "")
            pel.outerHTML = pel.outerHTML

            document.getElementById(f'{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("contextmenu", create_proxy(lambda args: self.onContextMenu(args, onSubmit)))

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
            submitBool(args, onSubmit)
            return None
        elif valueType in ["list", "tuple"]:
            main, typ, custom, styleInp = ("select", "", " size=\"1\" multiple", " height: 100%; top: -1px; background: transparent; color: inherit; overflow-x: hidden;")

            keyTmp = key
            if not self.sendKey:
                keyTmp = tag

            allData = []
            if keyTmp in self.optionsDict:
                allData = self.optionsDict[keyTmp]
            elif f'/{keyTmp}.json' in self.optionsDict:
                allData = self.optionsDict[f'/{keyTmp}.json']

            for option in allData:
                nest += HTML.genElement("option", nest=option, style="margin: 0px 1px; background: transparent; color: inherit;", custom=f'value="{option}"')

        txt = HTML.genElement(main,
                              id=f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}',
                              classes=f'Input_{maincom}_{sheet}_{tag}',
                              nest=nest,
                              type=typ,
                              style=f'z-index: 110; width: 100%; position: relative; padding: 0px; margin: 0px; border: 0px none #55F; font-size: 75%; text-align: center;{styleInp}',
                              custom=f'placeholder="{key}"{custom}')
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
            document.getElementById(pel.id).addEventListener("keyup", create_proxy(lambda args: submitList(args, onSubmit)))
            return None

        CSS.onHoverFocus(f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}', "inputHover", "inputFocus")
        document.getElementById(f'Input_{maincom}_{sheet}_{tag}_{key}_{valueType}').addEventListener("keyup", create_proxy(lambda args: func(args, onSubmit)))

    def onDblClick(self, args):
        window.alert(str(args.target.innerHTML))

    def addRecord(self, args, reloadFunction: object = None):
        maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]
        toSend = []
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
                toSend.append(lambda: WS.send(f'{maincom} add {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}'))
                continue

            toSend.append(lambda: WS.send(f'{maincom} rmodify {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")} {key.replace(" ", "%20")} {value.replace(" ", "%20")}'))

        for i, sendFunc in enumerate(toSend):
            if not reloadFunction is None and i + 1 >= len(toSend):
                WS.onMsg("{\"" + maincom + "\": {\"" + sheet + "\":", lambda: setTimeout(create_once_callable(reloadFunction), 1), oneTime=True)
            sendFunc()

    def remRecord(self, args):
        maincom, sheet, tag, key, valueType = args.target.id.split("_")[-5:]

        if not JS.popup("confirm", f'Are you sure you want to delete "{tag}"?\nThis can not be reverted!'):
            return None

        WS.send(f'{maincom} delete {sheet.replace(" ", "%20")} {tag.replace(" ", "%20")}')
        HTML.remElement(f'DivRow_{maincom}_{sheet}_{tag}')

    def generateEvents(self, onReloadCall: object = None, onSubmit: object = None):
        for id in self.eventConfig["editIds"]:
            el = document.getElementById(id)
            if el is None:
                return None
            el.addEventListener("contextmenu", create_proxy(lambda args: self.onContextMenu(args, onSubmit)))

        for id in self.eventConfig["inputIds"]:
            el = document.getElementById(id)
            if el is None:
                return None

            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]

            if valueType == "list":
                el = document.getElementById(el.id.replace("Input_", "Div_"))
                CSS.onHoverFocus(el.id, "selectHover %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;", "selectFocus %% margin-bottom: -135px; min-height: 159px; overflow-y: hidden;")
            else:
                CSS.onHoverFocus(el.id, "inputHover", "inputFocus")

        for id in self.eventConfig["actionIds"]:
            el = document.getElementById(id)
            if el is None:
                return None

            maincom, sheet, tag, key, valueType = el.id.split("_")[-5:]

            if valueType == "rem":
                func = self.remRecord
            else:
                func = lambda args: self.addRecord(args, reloadFunction=onReloadCall)
            document.getElementById(el.id).addEventListener("click", create_proxy(func))

            CSS.onHoverClick(el.id, "buttonHover", "buttonClick")

        for id in self.eventConfig["popupIds"]:
            el = document.getElementById(id)
            if el is None:
                return None
            el.addEventListener("dblclick", create_proxy(self.onDblClick))


class tree:
    __all__ = ["generate"]

    def __init__(self, name: str, elId: str, dates: tuple = (), wordWrap: bool = False):
        self.name = name
        self.elId = elId
        self.dates = dates
        self.wordWrap = wordWrap

    def recursive(self, data, rowC, colC, layer, prtSpc={}):
        if layer + 2 > colC:
            colC = layer + 2

        wrapStyle = " word-break: break-all;" if self.wordWrap else " height: 15px;"
        styleP = "margin: 0px; padding: 0px; text-align: left; font-size: 75%; overflow: hidden;"
        prtChar = "bCross"
        prtSpc[str(layer)] = True
        for i, record in enumerate(data):
            if len(data) - 1 == i:
                prtChar = "bEnd"
                if record == list(data)[-1]:
                    prtSpc[str(layer)] = False

            spacer = ""
            if layer > 1:
                for i1 in range(1, layer):
                    if prtSpc[str(i1)]:
                        spacer += HTML.genElement("p", classes=f'{self.name}_bLeft', style=styleP)
                        continue
                    spacer += HTML.genElement("p", classes=f'{self.name}_rows_p1', style=styleP + wrapStyle)

            if layer > 0:
                if prtChar == "bCross":
                    spacer += HTML.genElement("p", nest="───────────────", classes=f'{self.name}_bCross', style=styleP)
                elif prtChar == "bEnd":
                    spacer += HTML.genElement("p", classes=f'{self.name}_bEnd', style=styleP)

            if type(data[record]) is dict:
                HTML.addElement("div", self.elId, id=f'{self.name}_row{rowC}', align="left", style="display: flex;")
                HTML.addElement("p", f'{self.name}_row{rowC}', nest=record, prepend=spacer, classes=f'{self.name}_rows_p1', style=styleP.replace("left", "center") + wrapStyle)
                rowC, colC = self.recursive(data[record], rowC + 1, colC, layer + 1, prtSpc)

            else:
                HTML.addElement("div", self.elId, id=f'{self.name}_row{rowC}', align="left", style="display: flex;")
                value = data[record]
                if record in self.dates:
                    value = datetime.fromtimestamp(value).strftime("%d-%m-%y %H:%M")

                if layer > 0:
                    HTML.addElement("p", f'{self.name}_row{rowC}', nest=f'{record}:', prepend=spacer, classes=f'{self.name}_rows_p1', style=styleP + wrapStyle)
                else:
                    HTML.addElement("p", f'{self.name}_row{rowC}', nest=f'{record}:', prepend=spacer, classes=f'{self.name}_rows_p1', style=styleP.replace("left", "center") + wrapStyle)

                HTML.addElement("p", f'{self.name}_row{rowC}', nest=str(value), classes=f'{self.name}_rows_p2', style=styleP + wrapStyle)
                rowC += 1

        return rowC, colC

    def setStyling(self, colC):
        for item in HTML.getElements(f'{self.name}_rows_p1'):
            item.style.width = f'{80 / colC}%'
            item.style.marginTop = "3px"

        for item in HTML.getElements(f'{self.name}_rows_p2'):
            item.style.width = f'{140 / colC}%'
            item.style.marginTop = "3px"
            item.style.whiteSpace = "normal"
            item.style.wordWrap = "break-word"

        for item in HTML.getElements(f'{self.name}_bCross'):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.fontSize = "100%"
            item.style.overflow = "hidden"
            item.style.borderLeft = "2px solid #44F"
            item.style.userSelect = "none"

        for item in HTML.getElements(f'{self.name}_bEnd'):
            item.style.width = f'{40/ colC}%'
            item.style.height = "12px"
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = "2px solid #44F"
            item.style.borderBottom = "2px solid #44F"

        for item in HTML.getElements(f'{self.name}_bLeft'):
            item.style.width = f'{40/ colC}%'
            item.style.margin = f'0px 0px 0px {40 / colC}%'
            item.style.borderLeft = "2px solid #44F"

        for item in HTML.getElements(f'{self.name}_bBottom'):
            item.style.width = f'{80/ colC}%'
            item.style.height = "9px"
            item.style.borderBottom = "2px solid #44F"

    def generate(self, data):
        HTML.clrElement(self.elId)
        rowC, colC = self.recursive(data, 0, 0, 0)
        self.setStyling(colC)


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

        txt = HTML.genElement("h1", nest=f'{rowPrefix}{(rows - i1) * rowStep}{rowAfterfix}', style="headerSmall %% height: 25%; margin: 0px auto auto auto;")
        if i1 == rows - 1:
            txt += HTML.genElement("h1", style="headerSmall %% height: 40%; margin: auto auto auto auto;")
            txt += HTML.genElement("h1", nest=f'{rowPrefix}{(rows - i1 - 1) * rowStep}{rowAfterfix}', style="headerSmall %% height: 25%; margin: auto auto auto 5px;")

        htmlCols = HTML.genElement("div", nest=txt, id=f'{name}_row_{rows - i1 - 1}_col_header', style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeight}; border-right: 2px solid #111;{borderStyle}')
        for i2 in range(0, cols):
            if i2 == cols - 1:
                htmlCols += HTML.genElement("div", id=f'{name}_row_{rows - i1 - 1}_col_{i2}', style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight};{borderStyle}')
            else:
                htmlCols += HTML.genElement("div", id=f'{name}_row_{rows - i1 - 1}_col_{i2}', style=f'flex %% background: #333; width: {colsNormal}%; height: {rowHeight}; border-right: 1px dashed #111;{borderStyle}')

        htmlRows += HTML.genElement("div", nest=htmlCols, id=f'{name}_row_{rows - i1 - 1}', style=f'flex %% width: 100%; height: {rowHeight};')

    txt = ""
    if not smallHeaders:
        if len(origin) == 1:
            txt += HTML.genElement("h1", nest=str(origin[0]), style="headerSmall %% margin: auto;")
        elif len(origin) > 1:
            txt += HTML.genElement("h1", nest=str(origin[0]), style="headerSmall %% margin: 0px 5%; width: 90%; text-align: left;")
            txt += HTML.genElement("h1", nest="/", style="headerSmall %% margin: 0px 5%; width: 90%; text-align: center;")
            txt += HTML.genElement("h1", nest=str(origin[1]), style="headerSmall %% margin: 0px 5%; width: 90%; text-align: right;")

    htmlCols = HTML.genElement("div", nest=txt, id=f'{name}_row_header_col_header', style=f'background: #FBDF56; width: {colsSmall}%; height: {rowHeightSmall}; border-right: 2px solid #111; border-top: 2px solid #111;')
    for i2 in range(0, cols):
        try:
            txt = HTML.genElement("h1", nest=f'{colNames[i2]}', style="headerSmall %% margin: auto;")
        except IndexError:
            txt = HTML.genElement("h1", nest="", style="headerSmall %% margin: auto;")

        if i2 == cols - 1:
            htmlCols += HTML.genElement("div", nest=txt, id=f'{name}_row_header_col_{i2}', style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-top: 2px solid #111;')
        else:
            htmlCols += HTML.genElement("div", nest=txt, id=f'{name}_row_header_col_{i2}', style=f'flex %% background: #FBDF56; width: {colsNormal}%; height: {rowHeightSmall}; border-right: 1px dashed #111; border-top: 2px solid #111;')

    htmlRows += HTML.genElement("div", nest=htmlCols, id=f'{name}_row_header', style=f'flex %% width: 100%; height: {rowHeightSmall};')

    return HTML.genElement("div", nest=htmlRows, id=name, style="margin: 10px; padding-bottom: 2px; border: 2px solid #111;")


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
                HTML.addElement(
                    "div",
                    f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                    style=
                    f'z-index: 10; width: 10px; height: 10px; margin: -5px; background: #55F; border-radius: 10px; position: relative; top: {95 - int(rowFloat[:2] + "0" * (2 - len(rowFloat[:2])))}%; left: {-5 + int(colFloat[:2] + "0" * (2 - len(colFloat[:2])))}%'
                )
            else:
                vw = "-25vw"
                if int(colNum) < 3:
                    vw = "0.5vw"

                vh = "0.5vh"
                if int(rowNum) < 3:
                    vh = "-25vh"

                txt = HTML.genElement("h1", nest=onHoverTxt, style="headerSmall %% white-space: nowrap; text-overflow: ellipsis;")
                details = HTML.genElement("div",
                                          nest=txt,
                                          id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHoverTxt',
                                          style=f'divNormal %% z-index: 12; width: 0vw; height: 25vh; margin: {vh} 0px 0px {vw}; padding: 0px; position: relative; opacity: 0%; transition: width 0.25s, opacity 0.5s; overflow-x: hidden;')
                HTML.addElement(
                    "div",
                    f'{name}_row_{rowNum[:2]}_col_{colNum[:2]}',
                    nest=details,
                    id=f'{name}_row_{rowNum[:2]}-{rowFloat[:2]}_col_{colNum[:2]}-{colFloat[:2]}_onHover',
                    style=
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
    img = HTML.genElement("img", style="z-index: 1; user-select: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%;", custom='src="docs/assets/Widgets/Transparent.png" alt="Black"')
    img = HTML.genElement("div", nest=img, id=f'{name}_img', style="margin-bottom: -56.25%; position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;")

    ifr = HTML.genElement("div", id=f'{name}_ifr', style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;", custom='frameborder="0"')
    ifr = HTML.genElement("div", nest=ifr, id=f'{name}_div', style="position: relative; width: 100%; height: 0px; padding-bottom: 56.25%;")

    return HTML.genElement("div", nest=img + ifr, id=name, style="divNormalNoEdge %% max-width: 96%; margin: auto 1%; border-radius: 10px; overflow: hidden;")


def ytVideoGetControl(name):
    return JS.jsEval("new YT.Player('" + str(name) + "_ifr', { videoId: '', playerVars: { 'autoplay': 0, 'controls': 0, 'disablekb': 1, 'fs': 0, 'iv_load_policy': 3, 'modestbranding': 1, 'rel': 0 } } );")