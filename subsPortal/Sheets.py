from datetime import datetime, timedelta
from json import dumps, loads

from WebKit import HTML, JS, WS, PortalPage, Widget


class sheets(PortalPage):
    def __init__(self):
        super().__init__()

        for key in ("halfView", "quarterView", "excludeView", "encryptOnSent"):
            self.configKeys.append(key)
        self.evalMap = {
            "clean": self.clean,
            "restart": self.restart,
            "shutdown": self.shutdown,
            "export": self.exportAsJson,
            "import": self.importFromJson,
        }

        self.onSubPageLoad = self.loadSubPage
        self.onPreload = self.doOnPreload

        self.dates = []
        self.optionsDict = {}
        self.wordWrap = False

        self.halfView = None
        self.quarterView = None
        self.excludeView = None
        self.encryptOnSent = None

        self.compactView = True
        self.hideInactive = True

        self.sheet = None
        self.template = {}
        self.configHeader = ("Key", "Value")
        self.logsHeader = ("Date/ Time", "Criticality", "Executor", "Message", "Status")
        self.selectedLog = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self._lastUpdate:
            for file in (*self.template["sheets"], *self.template["configs"]):
                WS.send(f'{self.mainCom} read {file.replace(" ", "%20")}')
            for file in self.template["logs"] if "logs" in self.template else {}:
                WS.send(f'{self.mainCom} readlog {file.replace(" ", "%20")} {self.template["logs"][file][-1]}')
            self._lastUpdate = datetime.now().timestamp()

    def doOnPreload(self):
        def fetchTemplate():
            self.template = WS.dict()[self.mainCom]["template"]
            self.subPages = (*self.template["sheets"], *self.template["configs"], *(self.template["logs"] if "logs" in self.template else {}))

            WS.onMsg('{"' + self.mainCom + '": {"' + (*self.template["sheets"], *self.template["configs"], *(self.template["logs"] if "logs" in self.template else {}))[-1] + '":', self.preload, kwargs={"firstRun": False}, oneTime=True)
            self.getData()

        WS.onMsg('{"' + self.mainCom + '": {"template":', fetchTemplate, oneTime=True)
        WS.send(f"{self.mainCom} template")

        return False

    def loadSubPage(self):
        if JS.cache("portalSubPage") in self.template["sheets"]:
            self.generateSheet()
        elif JS.cache("portalSubPage") in self.template["configs"]:
            self.generateConfig()
        elif JS.cache("portalSubPage") in (self.template["logs"] if "logs" in self.template else {}):
            self.generateLog()

    def generateSheet(self):
        file = JS.cache("portalSubPage")
        if not file in self.template["sheets"]:
            return None

        self.enableButtons()

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

        self.sheet = Widget.sheet(
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
            encryptOnSent=self.encryptOnSent,
        )
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, kwargs={"onAdd": self.addRecord, "onDel": self.delRecord, "onMod": self.modRecord}, delay=50)

    def generateConfig(self):
        file = JS.cache("portalSubPage")
        if not file in self.template["configs"]:
            return None

        self.enableButtons(("Inactive", "Expand", "Import"))

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
            header=self.configHeader,
            data=WS.dict()[self.mainCom][file],
            dates=list(self.dates),
            wordWrap=self.wordWrap,
            optionsDict=options,
            encryptOnSent=self.encryptOnSent,
        )
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, kwargs={"onMod": self.modCfgRecord}, delay=50)

    def generateLog(self):
        file = JS.cache("portalSubPage")
        if not file in (self.template["logs"] if "logs" in self.template else {}):
            return None

        if self.selectedLog is None:
            self.selectedLog = "2023-12"

        self.enableButtons(("Inactive", "Import"))

        headers = list(self.logsHeader)
        fileData = WS.dict()[self.mainCom][file][self.selectedLog]
        halfView = list(key for key in self.halfView if key in headers)
        quarterView = list(key for key in self.quarterView if key in headers)

        for value in tuple(self.excludeView if self.compactView else ()):
            if not value in headers:
                continue

            i = headers.index(value)
            headers.pop(i)

            for index in dict(fileData):
                fileData[index].pop(i)
            if value in self.halfView:
                halfView.remove(value)
            if value in self.quarterView:
                quarterView.remove(value)

        self.sheet = Widget.sheetLogs(
            name=file,
            header=headers,
            data=fileData,
            halfView=halfView,
            quarterView=quarterView,
            wordWrap=self.wordWrap,
        )
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, delay=50)

    def exportAsJson(self, typ: str = None, id: str = None):
        if typ is None:
            Widget.popup("buttons", "Export\nDo an minimal or full export?\nMinimal export only include values and not keys.", self.exportAsJson, kwargs={"id": id}, custom=("Minimal", "Full"))
            return None

        file = JS.cache("portalSubPage")
        sheetData = WS.dict()[self.mainCom][file]
        if file in self.template["sheets"]:
            headers = []
            for name, ktype in WS.dict()[self.mainCom]["template"]["sheets"][file]:
                headers.append(name)
        elif file in (self.template["logs"] if "logs" in self.template else {}):
            headers = self.logsHeader
            sheetData = sheetData[self.selectedLog]

        if typ == "Minimal":
            sheetData = str(dumps([sheetData[dataIndex] for dataIndex in sheetData]))
        elif typ == "Full":
            if file in self.template["configs"]:
                sheetData = str(dumps(sheetData))
            else:
                sheetData = str(dumps({dataIndex: {header: sheetData[dataIndex][i] for i, header in enumerate(headers)} for dataIndex in sheetData}))

        HTML.addElement("a", "portalSubPage", id=f"{file}_Download", style="display: none;", custom=f'href="data:text/json;charset=utf-8,{JS.uriFriendlyfy(sheetData)}" download="{file}.json"')
        JS.aSync(HTML.getElement(f"{file}_Download").click)
        JS.aSync(HTML.remElement, (f"{file}_Download",))

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

                self._loadPortalSubPage()
                return None

            for i, dataIndex in enumerate(data):
                if i + 1 >= len(data):
                    WS.onMsg('{"' + self.mainCom + '": {"' + JS.cache("portalSubPage").replace(" ", "%20") + '":', self._loadPortalSubPage, kwargs={"disableAnimation": True}, oneTime=True)

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

    def shutdown(self, id: str = None):
        if JS.popup("confirm", "Are you sure you want to shutdown the server?\nThis will disconnect everyone!"):
            WS.send("shutdown")

    def restart(self, id: str = None):
        if JS.popup("confirm", "Are you sure you want to restart the server?\nThis will disconnect everyone!"):
            WS.send("restart")

    def clean(self, id: str = None):
        def cleanResults():
            Widget.popup("warning", f'Cleaning results:\n{chr(10).join(WS.dict()[self.mainCom]["Cleaned"])}')

        def sendClean(value):
            if value == "Clean":
                WS.onMsg('{"' + self.mainCom + '": {"Cleaned":', cleanResults, oneTime=True)
                WS.send(f"{self.mainCom} clean")

        Widget.popup("input", 'Clean\nAre you sure you want to clean? This cannot be reverted!\nThis will delete all data of the server cache and no longer existing users.\nPlease type "Clean" to confirm.', onSubmit=sendClean, custom=("Clean",))


class trees(PortalPage):
    def __init__(self):
        super().__init__()

        self.onSubPageLoad = self.generateTrees

        self.customSheets = None
        self.dates = None

        self.wordWrap = False

    def generateTrees(self):
        self.enableButtons()

        data = WS.dict()[self.mainCom][JS.cache("portalSubPage")]
        if data == {}:
            mainValue = list(self.customSheets[JS.cache("portalSubPage")])[-1]
            data[" "] = {}
            for value in self.customSheets[JS.cache("portalSubPage")][mainValue]:
                data[" "][value] = self.customSheets[JS.cache("portalSubPage")][mainValue][value]()

        tree = Widget.tree(name=JS.cache("portalSubPage"), elId="portalSubPage", dates=self.dates, wordWrap=self.wordWrap)
        tree.generate(data)
