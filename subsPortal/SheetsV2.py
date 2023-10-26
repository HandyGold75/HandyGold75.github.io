from datetime import datetime, timedelta
from json import dumps, load
from os import path as osPath

from WebKit import Widget
from WebKit.init import CSS, HTML, JS, WS


class sheetsV2:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        self.lastUpdate = 0
        self.compactView = True
        self.hideInactive = True
        self.wordWrap = False

        self.template = {}

        self.evalMap = {
            "compactOption": self.compactOption,
            "activeOption": self.activeOption,
            "wrapOption": self.wrapOption,
            # "userAdd": self.userAdd,
            # "clean": self.clean,
            # "restart": self.restart,
            # "shutdown": self.shutdown,
        }
        self.allConfigKeys = ("dates", "halfView", "quarterView", "excludeView", "invokePswChange", "optionsDict", "hideInput", "mainCom", "extraButtons")

        self.sheet = None
        self.dates = None
        self.halfView = None
        self.quarterView = None
        self.excludeView = None
        self.invokePswChange = None
        self.optionsDict = None
        self.hideInput = None
        self.mainCom = None
        self.extraButtons = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self.lastUpdate:
            for file in (*self.template["sheets"], *self.template["configs"], *self.template["configs"]):
                WS.send(f"{self.mainCom} read {file}")
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

        def fetchTemplate():
            self.template = WS.dict()[self.mainCom]["template"]
            WS.onMsg('{"' + self.mainCom + '": {"' + (*self.template["sheets"], *self.template["configs"], *self.template["configs"])[-1] + '":', self.preload, kwargs={"firstRun": False}, oneTime=True)
            self.getData()

        def finalize(self):
            self.busy = False

        if not firstRun:
            if self.template == {}:
                JS.afterDelay(self.preload, kwargs={"firstRun": False}, delay=50)

            if self.busy:
                CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
                JS.afterDelay(finalize, (self,), delay=250)
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

        with open(f"{osPath.split(__file__)[0]}/config.json", "r", encoding="UTF-8") as fileR:
            config = load(fileR)["sheetsV2"][JS.cache("portalPage")]
        for attribute in self.allConfigKeys:
            setattr(self, attribute, config[attribute])

        WS.onMsg('{"' + self.mainCom + '": {"template":', fetchTemplate, oneTime=True)
        WS.send(f"{self.mainCom} template")

    def deload(self):
        def fininalize(self):
            self.busy = False

        self.busy = True
        if not self.sheet is None:
            self.sheet.destorySheet()
        JS.onResize("sheets", None)
        for attribute in self.allConfigKeys:
            setattr(self, attribute, None)

        CSS.setStyles("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px')))
        JS.aSync(CSS.setStyle, ("portalSubPage", "maxHeight", "0px"))
        JS.afterDelay(fininalize, (self,), delay=250)

    def layout(self, subPage: str = None):
        data = WS.dict()[self.mainCom]

        navBtns = ""
        for file in data:
            if not file in (*self.template["sheets"], *self.template["configs"], *self.template["configs"]):
                continue
            navBtns += HTML.genElement("button", nest=f'{file.replace("/", "").replace(".json", "").replace(".log", "")}', id=f"portalSubPage_nav_main_{file}", type="button", style="buttonSmall")

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
            for file in data:
                if not file in (*self.template["sheets"], *self.template["configs"], *self.template["configs"]):
                    continue

                JS.addEvent(f"portalSubPage_nav_main_{file}", self.loadPortalSubPage, kwargs={"portalSubPage": file})
                JS.addEvent(f"portalSubPage_nav_main_{file}", self.getData, action="mousedown")
                CSS.onHoverClick(f"portalSubPage_nav_main_{file}", "buttonHover", "buttonClick")

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

        if not self.sheet is None:
            self.sheet.destorySheet()

        HTML.clrElement("portalSubPage")
        self.generateSheet()

        if not disableAnimation:
            CSS.setStyle("portalSubPage", "maxHeight", "")
            elHeight = f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px'
            CSS.setStyle("portalSubPage", "maxHeight", "0px")
            JS.aSync(CSS.setStyles, ("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", elHeight))))
            JS.afterDelay(CSS.setStyle, ("portalSubPage", "maxHeight", ""), delay=250)
        self.busy = False

    def generateSheet(self):
        file = JS.cache("portalSubPage")
        if file in self.template["sheets"]:
            for button in self.extraButtons:
                if not button["active"]:
                    HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

            headers = []
            types = []
            for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][file]:
                headers.append(name)
                types.append(type(ktype))

            fileData = WS.dict()[self.mainCom][file]
            fileDataLen = len(fileData)
            if self.hideInactive and "Active" in headers:
                for index in dict(fileData):
                    if not fileData[index][headers.index("Active")]:
                        fileData.pop(index)

            dates = list(self.dates)
            halfView = list(key for key in self.halfView if key in headers + ["Action"])
            quarterView = list(key for key in self.quarterView if key in headers + ["Action"])

            for value in tuple(self.excludeView if self.compactView else ()) + (("Active",) if self.hideInactive else ()):
                if not value in headers:
                    continue

                i = headers.index(value)
                headers.pop(i)
                types.pop(i)
                for index in dict(fileData):
                    fileData[index].pop(i)

                if value in self.dates:
                    dates.remove(value)
                if value in self.halfView:
                    halfView.remove(value)
                if value in self.quarterView:
                    quarterView.remove(value)

            options = self.optionsDict[file] if file in self.optionsDict else {}
            for f in WS.dict()[self.mainCom]:
                if f in [file, "template"]:
                    continue

                optionsData = WS.dict()[self.mainCom][f]
                options = {**options, f: [optionsData[opt][0] for opt in optionsData]}

            self.sheet = Widget.sheetV2(
                name=file,
                header=headers,
                types=types,
                data=fileData,
                dataLen=fileDataLen,
                dates=dates,
                halfView=halfView,
                quarterView=quarterView,
                wordWrap=self.wordWrap,
                optionsDict=options,
            )
            HTML.setElementRaw("portalSubPage", self.sheet.generateSheet())
            JS.afterDelay(self.sheet.generateEvents, kwargs={"onAdd": self.addRecord, "onDel": self.delRecord, "onMod": self.modRecord}, delay=50)

    def compactOption(self):
        self.compactView = not self.compactView
        if self.compactView:
            CSS.setAttribute("portalSubPage_nav_options_compact", "innerHTML", "Expand")
        else:
            CSS.setAttribute("portalSubPage_nav_options_compact", "innerHTML", "Compact")

        self.loadPortalSubPage()

    def activeOption(self):
        self.hideInactive = not self.hideInactive
        if self.hideInactive:
            CSS.setAttribute("portalSubPage_nav_options_active", "innerHTML", "Inactive")
        else:
            CSS.setAttribute("portalSubPage_nav_options_active", "innerHTML", "Active")

        self.loadPortalSubPage()

    def wrapOption(self):
        self.wordWrap = not self.wordWrap
        if self.wordWrap:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Inline")
        else:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Word wrap")

        self.loadPortalSubPage()

    def addRecord(self, index, count, data):
        sendData = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            if name in data:
                sendData.append(data[name])
                continue
            sendData.append(True if type(ktype) is bool else ktype)

        JS.log(str(sendData))

        WS.send(f'{self.mainCom} add {JS.cache("portalSubPage").replace(" ", "%20")} {index} {count} {str(dumps(sendData)).replace(" ", "")}')

    def delRecord(self, index):
        WS.send(f'{self.mainCom} del {JS.cache("portalSubPage").replace(" ", "%20")} {index}')

    def modRecord(self, index, key, data):
        if not key in [None, "*"]:
            WS.send(f'{self.mainCom} mod {JS.cache("portalSubPage").replace(" ", "%20")} {index} {key.replace(" ", "%20")} {str(data).replace(" ", "")}')
            return None

        sendData = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            if name in data:
                sendData.append(data[name])
                continue
            sendData.append(True if type(ktype) is bool else ktype)

        JS.log(f'{self.mainCom} mod {JS.cache("portalSubPage").replace(" ", "%20")} {index} * {str(dumps(sendData)).replace(" ", "")}')

    # def userAdd(self):
    #     if JS.cache("portalSubPage") == "":
    #         return None

    #     WS.onMsg('{"' + self.mainCom + '": {"' + {JS.cache("portalSubPage").replace(" ", "%20")} + '":', lambda: self.loadPortalSubPage(disableAnimation=True), oneTime=True)
    #     WS.send(f'{self.mainCom} uadd {JS.cache("portalSubPage").replace(" ", "%20")}')

    # def shutdown(self):
    #     if JS.popup("confirm", "Are you sure you want to shutdown the server?\nThis will disconnect everyone!"):
    #         WS.send("shutdown")

    # def restart(self):
    #     if JS.popup("confirm", "Are you sure you want to restart the server?\nThis will disconnect everyone!"):
    #         WS.send("restart")

    # def clean(self):
    #     def cleanResults():
    #         JS.popup("alert", f'Cleaning results:\n{chr(10).join(WS.dict()[self.mainCom]["Cleaned"])}')

    #     if JS.popup("confirm", "Are you sure you want to clean?\nThis will delete all data of no longer existing users and making it imposable to recover this data!"):
    #         WS.onMsg('{"' + self.mainCom + '": {"Cleaned":', cleanResults, oneTime=True)
    #         WS.send(f"{self.mainCom} clean")

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
            JS.afterDelay(self.loadPortalSubPage, args=(JS.cache("portalSubPage"),), delay=250)

        JS.onResize("sheets", self.onResize)
