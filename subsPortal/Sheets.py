from datetime import datetime, timedelta
from json import dumps, load, loads
from os import path as osPath

from WebKit import Widget
from WebKit.init import CSS, HTML, JS, WS


class sheets:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        self.lastUpdate = 0
        self.template = {}
        self.evalMap = {
            "compact": self.toggleOption,
            "active": self.toggleOption,
            "wordwrap": self.toggleOption,
            "export": self.exportAsJson,
            "import": self.importFromJson,
            "add": self.userAdd,
            "clean": self.clean,
            "restart": self.restart,
            "shutdown": self.shutdown,
        }

        self.compactView = True
        self.hideInactive = True
        self.wordWrap = False

        self.allConfigKeys = ("dates", "halfView", "quarterView", "excludeView", "invokePswChange", "optionsDict", "hideInput", "mainCom", "extraButtons")

        self.sheet = None
        self.dates = None
        self.halfView = None  # Sheets only
        self.quarterView = None  # Sheets only
        self.excludeView = None  # Sheets only
        self.invokePswChange = None
        self.optionsDict = None
        self.mainCom = None
        self.extraButtons = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self.lastUpdate:
            for file in (*self.template["sheets"], *self.template["configs"], *self.template["logs"]):
                WS.send(f'{self.mainCom} read {file.replace(" ", "%20")}')
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
            WS.onMsg('{"' + self.mainCom + '": {"' + (*self.template["sheets"], *self.template["configs"], *self.template["logs"])[-1] + '":', self.preload, kwargs={"firstRun": False}, oneTime=True)
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
            config = load(fileR)["sheets"][JS.cache("portalPage")]
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

    def layout(self):
        data = WS.dict()[self.mainCom]

        navBtns = ""
        for file in data:
            if not file in (*self.template["sheets"], *self.template["configs"], *self.template["logs"]):
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
            btnTxt = button["text"] if not hasattr(button, "toggleVar") or getattr(self, button["toggleVar"]) else button["textInactive"]
            navBtns += HTML.genElement("button", nest=btnTxt, id=f'portalSubPage_nav_options_{button["id"]}', type="button", align="right", style="buttonSmall")
        navDivs += HTML.genElement("div", id="portalSubPage_nav_options", nest=navBtns, align="right", style="width: 40%;")

        mainDiv = HTML.genElement("div", id="portalPageNav", nest=navDivs, align="center", style="pagePortal_Nav")
        mainDiv += HTML.genElement("div", id="portalSubPage", align="center", style="width: 100%; margin: 10px 0px; overflow: hidden;")
        HTML.setElementRaw("portalPage", mainDiv)

        def addEvents():
            self.busy = True
            for file in data:
                if not file in (*self.template["sheets"], *self.template["configs"], *self.template["logs"]):
                    continue

                JS.addEvent(f"portalSubPage_nav_main_{file}", self.loadPortalSubPage, kwargs={"portalSubPage": file})
                JS.addEvent(f"portalSubPage_nav_main_{file}", WS.send, args=(f'{self.mainCom} read {file.replace(" ", "%20")}',), action="mousedown")
                CSS.onHoverClick(f"portalSubPage_nav_main_{file}", "buttonHover", "buttonClick")

            for button in self.extraButtons:
                JS.addEvent(f'portalSubPage_nav_options_{button["id"]}', self.evalMap[button["id"]], kwargs={"id": f'portalSubPage_nav_options_{button["id"]}'})
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
        if JS.cache("portalSubPage") in self.template["sheets"]:
            self.generateSheet()
        elif JS.cache("portalSubPage") in self.template["configs"]:
            self.generateConfig()
        elif JS.cache("portalSubPage") in self.template["logs"]:
            self.generateLog()

        if not disableAnimation:
            CSS.setStyle("portalSubPage", "maxHeight", "")
            elHeight = f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px'
            CSS.setStyle("portalSubPage", "maxHeight", "0px")
            JS.aSync(CSS.setStyles, ("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", elHeight))))
            JS.afterDelay(CSS.setStyle, ("portalSubPage", "maxHeight", ""), delay=250)
        self.busy = False

    def generateSheet(self):
        file = JS.cache("portalSubPage")
        if not file in self.template["sheets"]:
            return None

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

        options = self.optionsDict[file] if file in self.optionsDict else {}
        for f in WS.dict()[self.mainCom]:
            if f in [file, "template"] or not f in self.template["sheets"]:
                continue

            optionsData = WS.dict()[self.mainCom][f]
            for index in dict(optionsData):
                headersTmp = [headerTmp[0] for headerTmp in WS.dict()[self.mainCom]["template"]["sheets"][f]]
                if self.hideInactive and "Active" in headersTmp:
                    if not optionsData[index][headersTmp.index("Active")]:
                        optionsData.pop(index)

            options = {**options, f: [optionsData[dataIndex][0] for dataIndex in optionsData]}

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
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, kwargs={"onAdd": self.addRecord, "onDel": self.delRecord, "onMod": self.modRecord}, delay=50)

    def generateConfig(self):
        file = JS.cache("portalSubPage")
        if not file in self.template["configs"]:
            return None

        for button in self.extraButtons:
            if not button["active"]:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

        options = self.optionsDict[file] if file in self.optionsDict else {}
        for f in WS.dict()[self.mainCom]:
            if f in [file, "template"] or not f in self.template["sheets"]:
                continue

            optionsData = WS.dict()[self.mainCom][f]
            for index in dict(optionsData):
                headersTmp = [headerTmp[0] for headerTmp in WS.dict()[self.mainCom]["template"]["sheets"][f]]
                if self.hideInactive and "Active" in headersTmp:
                    if not optionsData[index][headersTmp.index("Active")]:
                        optionsData.pop(index)

            options = {**options, f: [optionsData[dataIndex][0] for dataIndex in optionsData]}

        self.sheet = Widget.sheetConfig(
            name=file,
            header=("Key", "Value"),
            data=WS.dict()[self.mainCom][file],
            dates=list(self.dates),
            wordWrap=self.wordWrap,
            optionsDict=options,
        )
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, kwargs={"onMod": self.modCfgRecord}, delay=50)

    def generateLog(self):
        file = JS.cache("portalSubPage")
        if not file in self.template["logs"]:
            return None

        for button in self.extraButtons:
            if not button["active"]:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

    def toggleOption(self, id):
        for button in self.extraButtons:
            if id.split("_")[-1] != button["id"]:
                continue

            option = not getattr(self, button["toggleVar"])
            setattr(self, button["toggleVar"], option)
            CSS.setAttribute(id, "innerHTML", button["text"] if option else button["textInactive"])

            break

        self.loadPortalSubPage()

    def exportAsJson(self, typ: str = None, id: str = None):
        if typ is None:
            Widget.popup("buttons", "Export\nDo an minimal or full export?\nMinimal export only include values and not keys.", self.exportAsJson, kwargs={"id": id}, custom=("Minimal", "Full"))
            return None

        headers = []
        types = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            headers.append(name)
            types.append(type(ktype))

        sheetData = WS.dict()[self.mainCom][JS.cache("portalSubPage")]
        if typ == "Minimal":
            sheetData = str(dumps([sheetData[dataIndex] for dataIndex in sheetData]))
        else:
            sheetData = str(dumps({dataIndex: {header: sheetData[dataIndex][i] for i, header in enumerate(headers)} for dataIndex in sheetData}))

        HTML.addElement("a", "portalSubPage", id=f'{JS.cache("portalSubPage")}_Download', style="display: none;", custom=f'href="data:text/json;charset=utf-8,{JS.uriFriendlyfy(sheetData)}" download="{JS.cache("portalSubPage")}.json"')
        JS.aSync(HTML.getElement(f'{JS.cache("portalSubPage")}_Download').click)
        JS.aSync(HTML.remElement, (f'{JS.cache("portalSubPage")}_Download',))

    def importFromJson(self, id: str = None):
        def doImport(confirmation: bool, data: list | dict):
            if not confirmation:
                return None

            headers = []
            types = []
            for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
                headers.append(name)
                types.append(type(ktype))

            if type(data) is list:
                for dataIndex, record in enumerate(data):
                    record = [ktype(record[i]) for i, ktype in enumerate(types)]
                    WS.send(f'{self.mainCom} add {JS.cache("portalSubPage").replace(" ", "%20")} {dataIndex} 1 {str(dumps(record)).replace(" ", "")}')

                self.loadPortalSubPage()
                return None

            for i, dataIndex in enumerate(data):
                if i + 1 >= len(data):
                    WS.onMsg('{"' + self.mainCom + '": {"' + JS.cache("portalSubPage").replace(" ", "%20") + '":', self.loadPortalSubPage, kwargs={"disableAnimation": True}, oneTime=True)

                record = [data[dataIndex][header] for header in headers]
                WS.send(f'{self.mainCom} add {JS.cache("portalSubPage").replace(" ", "%20")} {dataIndex} 1 {str(dumps(record)).replace(" ", "")}')

        def submit(value):
            file, value = value
            if file is None:
                return None
            if not file.endswith(".json"):
                Widget.popup("warning", "File submit\nOnly json files are supported.")
                return None

            data = loads(value)
            if type(data) in [list, dict]:
                Widget.popup("confirm", f"Import\n{len(data)} records will be imported.\nThe import will be merged with the existing records.", onSubmit=doImport, args=(data,))
            else:
                Widget.popup("warning", "Import\nFile is formated incorretly.\nNothing was imported.")

        Widget.popup("file", "Import\nImport from a previous export.", onSubmit=submit)

    def addRecord(self, index, count, data):
        sendData = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            if name in data:
                sendData.append(data[name].replace(" ", "%20") if type(ktype) is str else data[name])
                continue
            sendData.append(True if type(ktype) is bool else ktype)

        WS.send(f'{self.mainCom} add {JS.cache("portalSubPage").replace(" ", "%20")} {index} {count} {str(dumps(sendData)).replace(" ", "")}')

    def delRecord(self, index):
        WS.send(f'{self.mainCom} del {JS.cache("portalSubPage").replace(" ", "%20")} {index}')

    def modRecord(self, index, key, data):
        if not key in [None, "*"]:
            WS.send(f'{self.mainCom} mod {JS.cache("portalSubPage").replace(" ", "%20")} {index} {key.replace(" ", "%20")} {str(data.replace(" ", "%20") if type(data) is str else data).replace(" ", "")}')
            return None

        sendData = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            if name in data:
                sendData.append(data[name].replace(" ", "%20") if type(ktype) is str else data[name])
                continue
            sendData.append(True if type(ktype) is bool else ktype)

        WS.send(f'{self.mainCom} mod {JS.cache("portalSubPage").replace(" ", "%20")} {index} * {str(dumps(sendData)).replace(" ", "")}')

    def modCfgRecord(self, key, data):
        if not key in [None, "*"]:
            JS.log(f'{self.mainCom} modcfg {JS.cache("portalSubPage").replace(" ", "%20")} {key.replace(" ", "%20")} {str(data.replace(" ", "%20") if type(data) is str else data).replace(" ", "")}')
            # WS.send(f'{self.mainCom} modcfg {JS.cache("portalSubPage").replace(" ", "%20")} {key.replace(" ", "%20")} {str(data.replace(" ", "%20") if type(data) is str else data).replace(" ", "")}')
            return None

        sendData = []
        for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][JS.cache("portalSubPage")]:
            if name in data:
                sendData.append(data[name].replace(" ", "%20") if type(ktype) is str else data[name])
                continue
            sendData.append(True if type(ktype) is bool else ktype)

        JS.log(f'{self.mainCom} modcfg {JS.cache("portalSubPage").replace(" ", "%20")} * {str(dumps(sendData)).replace(" ", "")}')
        # WS.send(f'{self.mainCom} modcfg {JS.cache("portalSubPage").replace(" ", "%20")} * {str(dumps(sendData)).replace(" ", "")}')

    def userAdd(self, id: str = None):
        JS.log(str(id))

    #     if JS.cache("portalSubPage") == "":
    #         return None

    #     WS.onMsg('{"' + self.mainCom + '": {"' + {JS.cache("portalSubPage").replace(" ", "%20")} + '":', lambda: self.loadPortalSubPage(disableAnimation=True), oneTime=True)
    #     WS.send(f'{self.mainCom} uadd {JS.cache("portalSubPage").replace(" ", "%20")}')

    def shutdown(self, id: str = None):
        JS.log(str(id))

    #     if JS.popup("confirm", "Are you sure you want to shutdown the server?\nThis will disconnect everyone!"):
    #         WS.send("shutdown")

    def restart(self, id: str = None):
        JS.log(str(id))

    #     if JS.popup("confirm", "Are you sure you want to restart the server?\nThis will disconnect everyone!"):
    #         WS.send("restart")

    def clean(self, id: str = None):
        JS.log(str(id))

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
