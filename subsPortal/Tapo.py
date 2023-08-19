from WebKit.init import HTML, CSS, JS, WS, Widget
from rsa import encrypt
from json import dumps, loads, load
from os import path as osPath
from datetime import datetime, timedelta
import math


class tapo:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        self.defaultConfig = {"costPerKw": 0.00, "costFormat": "$", "lineResolution": 25, "useMonthly": False, ":D": False}

        if JS.cache("configTapo") is None:
            JS.cache("configTapo", dumps(self.defaultConfig))

        self.lastUpdate = 0
        self.wordWrap = False

        self.evalMap = {"wrapOption": self.wrapOption}
        self.allConfigKeys = ("subPages", "knownFiles", "optionsDict", "mainCom", "extraButtons")

        self.subPages = None
        self.knownFiles = None
        self.optionsDict = None
        self.mainCom = None
        self.extraButtons = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self.lastUpdate:
            for txt in ("state", "history"):
                WS.send(f'{self.mainCom} {txt}')

            self.lastUpdate = datetime.now().timestamp()

    def onResize(self):
        if JS.getWindow().innerWidth < 500:
            CSS.setStyle("portalPageNav", "width", "75%")
            return None
        elif JS.getWindow().innerWidth < 1000:
            CSS.setStyle("portalPageNav", "width", "82.5%")
            return None
        CSS.setStyle("portalPageNav", "width", "90%")

    def preload(self, firstRun: bool = True):
        def loadingTxt():
            el = HTML.getElement("portalSubPage_loadingTxt")
            if el is None:
                return None

            if el.innerHTML.endswith(". . . "):
                el.innerHTML = el.innerHTML.replace(". . . ", "")

            el.innerHTML += ". "
            JS.afterDelay(loadingTxt, delay=500)

        def finalize(self):
            self.busy = False

        if not firstRun:
            if self.busy:
                CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
                JS.afterDelay(finalize, (self, ), delay=250)
            return None

        self.busy = True
        self.lastUpdate = 0

        content = HTML.genElement("h1", nest="Portal", style="headerMain")
        content += HTML.genElement("p", nest="Loading page", style="textBig")
        content += HTML.genElement("p", nest="Getting data from the server", id="portalSubPage_loadingTxt", style="textBig")
        HTML.setElement("div", "portalPage", nest=content, id="portalSubPage_summary", align="center")

        CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
        JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", "0px"))
        JS.aSync(loadingTxt)

        with open(f'{osPath.split(__file__)[0]}/config.json', "r", encoding="UTF-8") as fileR:
            config = load(fileR)["tapo"][JS.cache("portalPage")]
        for attribute in self.allConfigKeys:
            setattr(self, attribute, config[attribute])

        WS.onMsg("{\"" + self.mainCom + "\": {\"history\":", self.preload, kwargs={"firstRun": False}, oneTime=True)
        self.getData()

    def deload(self):
        def fininalize(self):
            self.busy = False

        self.busy = True
        JS.onResize("tapo", None)

        CSS.setStyles("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px')))
        JS.aSync(CSS.setStyle, ("portalSubPage", "maxHeight", "0px"))
        JS.afterDelay(fininalize, (self, ), delay=250)

    def layout(self, subPage: str = None):
        navBtns = ""
        for subPage in self.subPages:
            navBtns += HTML.genElement("button", nest=subPage, id=f'portalSubPage_nav_main_{subPage}', type="button", style="buttonSmall")

        if navBtns == "":
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="Unauthorized!\nReload the page if you think this is a mistake.", style="textBig")
            HTML.setElement("div", "portalPage", nest=header + body, id="loginPage", align="center")
            HTML.disableElement(f'portalSubPage_button_{JS.cache(f"portalSubPage")}')
            return None

        navDivs = HTML.genElement("div", id="portalSubPage_nav_main", nest=navBtns, align="left", style="width: 60%;")
        navBtns = ""
        for button in self.extraButtons:
            navBtns += HTML.genElement("button", nest=button["text"], id=f'portalSubPage_nav_options_{button["id"]}', type="button", align="right", style="buttonSmall")
        navDivs += HTML.genElement("div", id="portalSubPage_nav_options", nest=navBtns, align="right", style="width: 40%;")

        mainDiv = HTML.genElement("div", id="portalPageNav", nest=navDivs, align="center", style="flex %% width: 90%; padding: 10px; margin: 0px auto 10px auto; border-bottom: 5px dotted #111;")
        mainDiv += HTML.genElement("div", id="portalSubPage", align="center", style="width: 100%; margin: 10px 0px; overflow: hidden;")
        HTML.setElementRaw("portalPage", mainDiv)

        def addEvents():
            self.busy = True
            for subPage in self.subPages:
                JS.addEvent(f'portalSubPage_nav_main_{subPage}', self.loadPortalSubPage, kwargs={"portalSubPage": subPage})
                JS.addEvent(f'portalSubPage_nav_main_{subPage}', self.getData, action="mousedown")
                CSS.onHoverClick(f'portalSubPage_nav_main_{subPage}', "buttonHover", "buttonClick")

            for button in self.extraButtons:
                JS.addEvent(f'portalSubPage_nav_options_{button["id"]}', self.evalMap[button["function"]])
                CSS.onHoverClick(f'portalSubPage_nav_options_{button["id"]}', "buttonHover", "buttonClick")
                if not button["active"]:
                    HTML.disableElement(f'portalSubPage_nav_options_{button["id"]}')
            self.busy = False

        JS.afterDelay(addEvents, delay=50)

    def flyin(self):
        CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
        JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", "0px"))

    def loadPortalSubPage(self, portalSubPage: str = None, firstRun: bool = True, disableAnimation: bool = False):
        for button in self.extraButtons:
            if not button["active"]:
                HTML.disableElement(f'portalSubPage_nav_options_{button["id"]}')
        if not portalSubPage is None:
            JS.cache("portalSubPage", str(portalSubPage))
        if JS.cache("portalSubPage") == "":
            self.busy = False
            return None
        if self.busy and firstRun:
            return None

        self.busy = True
        if firstRun and not disableAnimation and HTML.getElement("portalSubPage").innerHTML != "":
            CSS.setStyles("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px')))
            JS.aSync(CSS.setStyle, ("portalSubPage", "maxHeight", "0px"))
            JS.afterDelay(self.loadPortalSubPage, kwargs={"firstRun": False}, delay=250)
            return None

        HTML.clrElement("portalSubPage")
        getattr(self, f'{JS.cache("portalSubPage").lower()}Page')()

        if not disableAnimation:
            CSS.setStyle("portalSubPage", "maxHeight", "")
            elHeight = f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px'
            CSS.setStyle("portalSubPage", "maxHeight", "0px")
            JS.aSync(CSS.setStyles, ("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", elHeight))))
            JS.afterDelay(CSS.setStyle, ("portalSubPage", "maxHeight", ""), delay=250)
        self.busy = False

    def plugsPage(self):
        pass

    def configPage(self):
        for button in self.extraButtons:
            if not button["active"]:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

        fileData = loads(JS.cache("configTapo"))
        if fileData == {}:
            JS.cache("configTapo", dumps(self.defaultConfig))
            fileData = self.defaultConfig

        dataTemp, fileData = (fileData, {})
        for i, key in enumerate(dict(self.knownFiles[JS.cache("portalSubPage")])):
            fileData[key] = {}
            try:
                fileData[key]["Value"] = dataTemp[key]
            except IndexError:
                fileData[key]["Value"] = ""

        options = (lambda: dict(self.optionsDict[JS.cache("portalSubPage")]) if JS.cache("portalSubPage") in self.optionsDict else {})()
        sheet = Widget.sheet(
            maincom=self.mainCom,
            name=JS.cache("portalSubPage"),
            typeDict=dict(self.knownFiles[JS.cache("portalSubPage")]),
            optionsDict=options,
            sendKey=False,
            showInput=False,
            showAction=False,
            wordWrap=self.wordWrap,
        )
        HTML.setElementRaw("portalSubPage", sheet.generate(dict(fileData)))
        JS.afterDelay(sheet.generateEvents, kwargs={"onReloadCall": lambda: self.loadPortalSubPage(disableAnimation=True), "onSubmit": self.configPageSubmit}, delay=50)

    def configPageSubmit(self, key, value):
        configTapo = loads(JS.cache("configTapo"))
        if key in configTapo:
            configTapo[key] = value
            JS.cache("configTapo", dumps(configTapo))

    def wrapOption(self):
        self.wordWrap = not self.wordWrap
        if self.wordWrap:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Inline")
        else:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Word wrap")

        self.loadPortalSubPage()

    def main(self):
        if not self.mainCom in WS.dict():
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="No data was found, please renavigate to this page.", style="textBig")
            HTML.setElement("div", "portalPage", nest=header + body, id="loginPage", align="center")
            self.flyin()
            return None

        self.layout()
        self.flyin()

        if not JS.cache("portalSubPage") == "":
            self.loadPortalSubPage(JS.cache("portalSubPage"))

        JS.onResize("tapo", self.onResize)

    def pageSub(args=None):
        def login():
            usr = JS.popup(f'prompt', f'Tapo Username')
            if usr is None:
                return None

            psw = JS.popup(f'prompt', f'Tapo Password')
            if psw is None:
                return None

            WS.onMsg("{\"" + self.mainCom + "\":", pageSub, oneTime=True)
            WS.onMsg("Failed", login, oneTime=True)
            WS.send(f'{self.mainCom} login {usr.replace(" ", "%20")} {str(encrypt(psw.encode(), WS.PK)).replace(" ", "%20")}')

        def plugs():
            def getDur(dur):
                for applyValue, correctionValue, format, round in [(7884000, 2628000, "M", False), (259200, 86400, "d", False), (10800, 3600, "h", False), (180, 60, "m", True)]:
                    if not dur > applyValue:
                        continue

                    if round:
                        dur = f'{int(dur / correctionValue)} {format}'
                        break

                    dur = f'{(dur / correctionValue):.2f} {format}'
                    break

                if type(dur) is int:
                    dur = f'{dur} s'

                return dur

            def verySlowUIRefresh():
                def update(data):
                    for plug in data:
                        HTML.setElementRaw(f'Details_{plug}_todayCost', f'{((data[plug]["todayPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}')
                        HTML.setElementRaw(f'Details_{plug}_monthlyCost', f'{((data[plug]["monthlyPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}')
                        HTML.setElementRaw(f'Details_{plug}_todayPower', f'{(data[plug]["todayPower"] / 1000):.2f} kW')
                        HTML.setElementRaw(f'Details_{plug}_monthlyPower', f'{(data[plug]["monthlyPower"] / 1000):.2f} kW')
                        HTML.setElementRaw(f'Details_{plug}_todayTime', f'{getDur(data[plug]["todayTime"] * 60)}')
                        HTML.setElementRaw(f'Details_{plug}_monthlyTime', f'{getDur(data[plug]["monthlyTime"] * 60)}')

                        if data[plug]["overheated"]:
                            CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'100%')
                        else:
                            CSS.setStyle(f'Gauge_{plug}_overheat', f'opacity', f'0%')

                if not JS.cache("page_portalSub") == "Plugs":
                    return False

                data = WS.dict()[self.mainCom]["current"]

                try:
                    update(data)
                except AttributeError:
                    return None

                JS.afterDelay(verySlowUIRefresh, delay=10000)

            def slowUIRefresh():
                def update(data):
                    for plug in data:
                        HTML.setElementRaw(f'Gauge_{plug}_power', f'{(data[plug]["currentPower"] / 1000):.2f}<br>Wh')
                        HTML.setElementRaw(f'Gauge_{plug}_uptime', f'{getDur(data[plug]["duration"])}')

                        if not data[plug]["state"]:
                            for i in range(0, 101):
                                CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'0%')

                            CSS.setStyles(f'Power_{plug}', ((f'background', f'#222'), (f'border', f'2px solid #222')))
                            continue

                        for i in range(0, 101):
                            if data[plug]["currentPower"] > i * 10000:
                                CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'100%')
                                continue

                            CSS.setStyle(f'Gauge_{plug}_{i}', f'opacity', f'0%')

                if not JS.cache("page_portalSub") == "Plugs":
                    return False

                data = WS.dict()[self.mainCom]["current"]

                try:
                    update(data)
                except AttributeError:
                    return None

                JS.afterDelay(getData, delay=500)
                JS.afterDelay(slowUIRefresh, delay=1000)

            def fastUIRefresh():
                def update(data):
                    for plug in data:
                        if not data[plug]["state"]:
                            continue

                        CSS.setStyles(f'Power_{plug}', ((f'background', f'#444'), (f'border', f'3px solid #FBDF56')))

                if not JS.cache("page_portalSub") == "Plugs":
                    return False

                data = WS.dict()[self.mainCom]["current"]

                try:
                    update(data)
                except AttributeError:
                    return None

                JS.afterDelay(fastUIRefresh, delay=250)

            def addGraph(plug: str):
                def drawLines():
                    def getDur(dur):
                        for applyValue, correctionValue, format, round in [(7884000, 2628000, "M", False), (259200, 86400, "d", False), (10800, 3600, "h", False), (180, 60, "m", True)]:
                            if not dur > applyValue:
                                continue

                            if round:
                                dur = f'{int(dur / correctionValue)} {format}'
                                break

                            dur = f'{(dur / correctionValue):.2f} {format}'
                            break

                        if type(dur) is int:
                            dur = f'{dur} s'

                        return dur

                    if glb.config[":D"]:
                        Widget.graphDraw(f'graph_usage_{plug}', ((1, 2, ":D"), (1, 3, ":D"), (2, 4, ":D"), (3, 4, ":D"), (4, 3, ":D"), (4, 2, ":D"), (3, 1, ":D"), (2, 1, ":D"), (1, 2, ":D")), lineRes=glb.config["lineResolution"])
                        Widget.graphDraw(f'graph_usage_{plug}', ((5, 1, ":D"), (4.5, 2, ":D"), (7.5, 2, ":D"), (7, 1, ":D"), (5, 1, ":D")), lineRes=glb.config["lineResolution"])
                        Widget.graphDraw(f'graph_usage_{plug}', ((8, 2, ":D"), (8, 3, ":D"), (9, 4, ":D"), (10, 4, ":D"), (11, 3, ":D"), (11, 2, ":D"), (10, 1, ":D"), (9, 1, ":D"), (8, 2, ":D")), lineRes=glb.config["lineResolution"])
                        Widget.graphDraw(f'graph_cost_{plug}', ((1, 2, ":D"), (1, 3, ":D"), (2, 4, ":D"), (3, 4, ":D"), (4, 3, ":D"), (4, 2, ":D"), (3, 1, ":D"), (2, 1, ":D"), (1, 2, ":D")), lineRes=glb.config["lineResolution"])
                        Widget.graphDraw(f'graph_cost_{plug}', ((5, 1, ":D"), (4.5, 2, ":D"), (7.5, 2, ":D"), (7, 1, ":D"), (5, 1, ":D")), lineRes=glb.config["lineResolution"])
                        Widget.graphDraw(f'graph_cost_{plug}', ((8, 2, ":D"), (8, 3, ":D"), (9, 4, ":D"), (10, 4, ":D"), (11, 3, ":D"), (11, 2, ":D"), (10, 1, ":D"), (9, 1, ":D"), (8, 2, ":D")), lineRes=glb.config["lineResolution"])

                        return None

                    data = WS.dict()[self.mainCom]["history"][plug]

                    usageDivision, costDivision, rowLimit, colLimit = (50, 10, 6, 13)
                    if not glb.config["useMonthly"]:
                        usageDivision, costDivision, rowLimit, colLimit = (5, 1, 4, 4)

                    date = datetime.now()
                    dates = []
                    for i in range(0, colLimit):
                        dates.append(date)
                        date = date - timedelta(days=date.day)

                    cordsUsage = []
                    cordsCost = []
                    for time in data:
                        dataDate = datetime.fromtimestamp(int(time))
                        col = None

                        for i, date in enumerate(reversed(dates)):
                            if dataDate.year != date.year or dataDate.month != date.month:
                                continue

                            col = i + 1 - (31 - dataDate.day) / 31
                            break

                        if col is None:
                            continue
                        elif col >= colLimit:
                            col = colLimit - 0.01
                        elif col < 0.01:
                            col = 0.01

                        txt = f'date: {dataDate.strftime("%d %b %y")}<br>'
                        for key in data[time]:
                            if key == "duration":
                                txt += f'{key}:	{getDur(data[time][key])}<br>'
                                continue
                            if key == "currentPower":
                                txt += f'{key}:	{(data[time][key] / 1000):.2f} W<br>'
                                continue
                            elif "Power" in key:
                                txt += f'{key}:	{(data[time][key] / 1000):.2f} kW<br>'
                                continue
                            elif "Time" in key:
                                txt += f'{key}:	{getDur(data[time][key] * 60)}<br>'
                                continue

                            txt += f'{key}:	{data[time][key]}<br>'

                        txt += f'todayCost: {((data[time]["todayPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}<br>'
                        txt += f'monthlyCost: {((data[time]["monthlyPower"] / 1000) * glb.config["costPerKw"]):.2f} {glb.config["costFormat"]}<br>'

                        dataPower = data[time]["monthlyPower"]
                        if not glb.config["useMonthly"]:
                            dataPower = data[time]["todayPower"]

                        row = dataPower / (1000 * usageDivision)
                        if row >= rowLimit:
                            row = rowLimit - 0.01
                        elif row < 0.01:
                            row = 0.01
                        cordsUsage.append((float(col), float(row), txt))

                        row = (dataPower / (1000 * costDivision)) * glb.config["costPerKw"]
                        if row >= rowLimit:
                            row = rowLimit - 0.01
                        elif row < 0.01:
                            row = 0.01
                        cordsCost.append((float(col), float(row), txt))

                    Widget.graphDraw(f'graph_usage_{plug}', cordsUsage, lineRes=glb.config["lineResolution"])
                    Widget.graphDraw(f'graph_cost_{plug}', cordsCost, lineRes=glb.config["lineResolution"])

                data = WS.dict()[self.mainCom]["current"]

                if not data[plug]["model"] in ["P115", "P110", "total"]:
                    return None

                usageStep, costStep, rowLimit, colLimit = (50, 10, 6, 13)
                if not glb.config["useMonthly"]:
                    usageStep, costStep, rowLimit, colLimit = (5, 1, 4, 4)

                date = datetime.now()
                dates = []
                for i in range(0, colLimit):
                    dates.append(date.strftime("%b (%y)"))
                    date = date - timedelta(days=date.day)

                txt = HTML.genElement("h1", nest=f'Usage - Montly', style=f'headerBig')
                if not glb.config["useMonthly"]:
                    txt = HTML.genElement("h1", nest=f'Usage - Daily', style=f'headerBig')

                HTML.setElement(f'div',
                                f'portalSubPage_graph',
                                nest=txt + Widget.graph(f'graph_usage_{plug}', rowHeight=f'75px', rows=rowLimit, rowStep=usageStep, cols=colLimit, origin=("power", "date"), rowAfterfix=" kW", colNames=tuple(reversed(dates)), smallHeaders=True),
                                id=f'portalSubPage_graph_usage',
                                style=f'divNormal')

                txt = HTML.genElement("h1", nest=f'Cost - Montly', style=f'headerBig')
                if not glb.config["useMonthly"]:
                    txt = HTML.genElement("h1", nest=f'Cost - Daily', style=f'headerBig')

                HTML.addElement(f'div',
                                f'portalSubPage_graph',
                                nest=txt +
                                Widget.graph(f'graph_cost_{plug}', rowHeight=f'75px', rows=rowLimit, rowStep=costStep, cols=colLimit, origin=("cost", "date"), rowAfterfix=f' {glb.config["costFormat"]}', colNames=tuple(reversed(dates)), smallHeaders=True),
                                id=f'portalSubPage_graph_cost',
                                style=f'divNormal')

                JS.aSync(drawLines)

            def addPlugs():
                def togglePower(args):
                    data = WS.dict()[self.mainCom]["current"]
                    plug = args.target.id.split("_")[-1]

                    if not plug in data:
                        return None

                    if not data[plug]["state"]:
                        WS.send(f'{self.mainCom} on {plug}')

                    elif JS.popup(f'confirm', f'Are you sure you want to turn off this device?\nDevice: {plug}'):
                        WS.send(f'{self.mainCom} off {plug}')

                def getInfo(args):
                    data = WS.dict()[self.mainCom]["history"]
                    plug = args.target.id.split("_")[-1]

                    if not plug in data:
                        return None

                    addGraph(plug)

                def header(plug):
                    img = HTML.genElement(f'img', id=f'Info_img_{plug}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Tapo/Info.png" alt="Info"')
                    btn = HTML.genElement(f'button', nest=f'{img}', id=f'Info_{plug}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                    info = HTML.genElement(f'div', nest=f'{btn}', align=f'center', style=f'width: 15%; min-width: 30px; margin: auto;')

                    txt = HTML.genElement(f'h1', nest=f'{plug}', style=f'headerMedium %% width: 70%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;')

                    img = HTML.genElement(f'img', id=f'Power_img_{plug}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Tapo/Power.png" alt="Power"')
                    btn = HTML.genElement(f'button', nest=f'{img}', id=f'Power_{plug}', style=f'buttonImg %% border: 0px solid #222; border-radius: 16px;')
                    power = HTML.genElement(f'div', nest=f'{btn}', align=f'center', style=f'width: 15%; min-width: 30px; margin: auto;')

                    return HTML.genElement(f'div', nest=f'{info}{txt}{power}', style=f'flex %% padding-bottom: 10px; border-bottom: 4px dotted #111;')

                def body(plug):
                    img = HTML.genElement(f'img', style=f'z-index: 1; width: 100%; margin: auto; position: relative; user-select:none;', custom=f'src="docs/assets/Portal/Tapo/Gauge.png" alt="Gauge"')

                    svg = ""
                    for i in range(0, 101):
                        if i < 50:
                            r, g = (int(255 * (i / 50)), 255)
                        else:
                            r, g = (255, int(255 * ((50 - i % 50) / 50)))

                        svg += HTML.genElement(f'line',
                                               id=f'Gauge_{plug}_{i}',
                                               style=f'z-index: 0; stroke: {"#{:02x}{:02x}{:02x}".format(r, g, 0)}; stroke-width: 5; opacity: 0%; transition: opacity 0.25s;',
                                               custom=f'x1="50%" y1="50%" x2="{i}%" y2="{256.3 * math.sin(math.pi * ((i - 50) / 100)**4)}%"')

                    svg = HTML.genElement(f'svg', nest=f'{svg}', style=f'width: 80%; height: 110px; margin: auto auto auto -80%; left: -10%; top: -5px; position: relative; user-select:none;')

                    txt = HTML.genElement(f'p',
                                          nest=f'0.00<br>Wh',
                                          id=f'Gauge_{plug}_power',
                                          style=f'z-index: 24; width: 100%; margin: auto auto auto -100%; padding: 0px 0px 5% 0px; line-height: 100%; font-weight: bold; position: relative; user-select:none;')
                    txt += HTML.genElement(f'p', nest=f'0.00 s', id=f'Gauge_{plug}_uptime', style=f'z-index: 25; width: 100%; margin: auto auto auto -100%; padding: 50% 0px 0px 0px; font-weight: bold; position: relative; user-select:none;')
                    txt += HTML.genElement(f'h1',
                                           nest=f'Overheated!',
                                           id=f'Gauge_{plug}_overheat',
                                           style=f'headerMedium %% z-index: 26; width: 100%; margin: auto auto -20px -100%; color: #F00; position: relative; opacity: 0%; transition: opacity 0.25s; user-select:none;')

                    return HTML.genElement(f'div', nest=f'{img}{svg}{txt}', style=f'flex %% padding: 20px 10px; border-bottom: 4px dotted #111;')

                def footer(plug):
                    div = ""

                    for visKey, key, format in (("Today", "", ""), ("Cost:", "todayCost", f'0 {glb.config["costFormat"]}'), ("Power:", "todayPower", "0 kW"), ("Time:", "todayTime", "0 s"), ("Monthly", "", ""),
                                                ("Cost:", "monthlyCost", f'0 {glb.config["costFormat"]}'), ("Power:", "monthlyPower", "0 kW"), ("Time:", "monthlyTime", "0 s")):

                        txt = HTML.genElement(f'p', nest=f'{visKey}', style=f'width: 45%; margin: auto; font-weight: bold; user-select:none;')

                        if not key == "":
                            txt += HTML.genElement(f'p', nest=f'{format}', id=f'Details_{plug}_{key}', style=f'width: 55%; margin: auto; font-weight: bold;')

                        div += HTML.genElement(f'div', nest=f'{txt}', align=f'center', style=f'flex')

                    return HTML.genElement(f'div', nest=f'{div}', style=f'padding-top: 10px;')

                data = WS.dict()[self.mainCom]["current"]

                for plug in data:
                    if not data[plug]["model"] in ["P115", "P110", "total"]:
                        continue

                    HTML.addElement(f'div',
                                    f'portalSubPage_main',
                                    nest=f'{header(plug)}{body(plug)}{footer(plug)}',
                                    id=f'portalSubPage_main_{plug}',
                                    style=f'divNormal %% min-width: 150px; margin: 15px; padding: 5px 15px 15px 15px; border: 4px solid #55F; border-radius: 4px;')

                for plug in data:
                    if not data[plug]["model"] in ["P115", "P110", "total"]:
                        continue

                    JS.addEvent(f'Info_{plug}', getInfo, includeElement=True)
                    CSS.onHoverClick(f'Info_{plug}', f'imgHover', f'imgClick')

                    JS.addEvent(f'Power_{plug}', togglePower, includeElement=True)
                    CSS.onHoverClick(f'Power_{plug}', f'imgHover', f'imgClick')

            HTML.setElement(f'div', f'portalSubPage', id=f'portalSubPage_main', style=f'divNormal %% flex %% margin: 15px 30px 15px auto; overflow-y: hidden;')
            HTML.addElement(f'div', f'portalSubPage', id=f'portalSubPage_graph', style=f'divNormal %% margin: 0px; padding 0px;')

            addPlugs()

            JS.afterDelay(fastUIRefresh, delay=250)
            JS.afterDelay(slowUIRefresh, delay=500)
            JS.afterDelay(verySlowUIRefresh, delay=750)

        pageSubMap = {"Plugs": plugs, "Config": config}

        HTML.clrElement(f'portalSubPage')

        if not self.mainCom in WS.dict():
            login()
            return None

        pageSubMap[JS.cache("page_portalSub")]()
