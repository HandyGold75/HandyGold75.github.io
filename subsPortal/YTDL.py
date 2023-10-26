from datetime import datetime, timedelta
from json import dumps, load, loads
from os import path as osPath

from WebKit import Widget
from WebKit.init import CSS, HTML, JS, WS


class ytdl:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        self.defaultConfig = {"quality": ["Medium"], "audioOnly": False}

        if JS.cache("configYTDL") is None:
            JS.cache("configYTDL", dumps(self.defaultConfig))

        self.lastUpdate = 0
        self.wordWrap = False
        self.lastDownload = 0
        self.lastDataPackage = {}

        self.evalMap = {"wrapOption": self.wrapOption}
        self.allConfigKeys = ("subPages", "dates", "knownFiles", "optionsDict", "mainCom", "extraButtons")

        self.subPages = None
        self.dates = None
        self.knownFiles = None
        self.optionsDict = None
        self.mainCom = None
        self.extraButtons = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self.lastUpdate:
            WS.send(f"{self.mainCom} state")

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
            config = load(fileR)["ytdl"][JS.cache("portalPage")]
        for attribute in self.allConfigKeys:
            setattr(self, attribute, config[attribute])

        WS.onMsg('{"' + self.mainCom + '":', self.preload, kwargs={"firstRun": False}, oneTime=True)
        self.getData()

    def deload(self):
        def fininalize(self):
            self.busy = False

        self.busy = True
        JS.onResize("ytdl", None)

        CSS.setStyles("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px')))
        JS.aSync(CSS.setStyle, ("portalSubPage", "maxHeight", "0px"))
        JS.afterDelay(fininalize, (self,), delay=250)

    def layout(self, subPage: str = None):
        navBtns = ""
        for subPage in self.subPages:
            navBtns += HTML.genElement("button", nest=subPage, id=f"portalSubPage_nav_main_{subPage}", type="button", style="buttonSmall")

        if navBtns == "":
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="Unauthorized!\nReload the page if you think this is a mistake.", style="textBig")
            HTML.setElement("div", "portalPage", nest=header + body, id="loginPage", align="center")
            HTML.disableElement(f'portalSubPage_button_{JS.cache("portalSubPage")}')
            return None

        navDivs = HTML.genElement("div", id="portalSubPage_nav_main", nest=navBtns, align="left", style="width: 60%;")
        navBtns = ""
        for button in self.extraButtons:
            navBtns += HTML.genElement("button", nest=button["text"], id=f'portalSubPage_nav_options_{button["id"]}', type="button", align="right", style="buttonSmall")
        navDivs += HTML.genElement("div", id="portalSubPage_nav_options", nest=navBtns, align="right", style="width: 40%;")

        mainDiv = HTML.genElement("div", id="portalPageNav", nest=navDivs, align="center", style="flex %% width: 90%; padding: 10px; margin: 0px auto 10px auto; border-bottom: 5px dotted #111;")
        mainDiv += HTML.genElement("div", id="portalSubPage", align="center", style="margin: 10px 0px; overflow: hidden;")
        HTML.setElementRaw("portalPage", mainDiv)

        def addEvents():
            self.busy = True
            for subPage in self.subPages:
                JS.addEvent(f"portalSubPage_nav_main_{subPage}", self.loadPortalSubPage, kwargs={"portalSubPage": subPage})
                JS.addEvent(f"portalSubPage_nav_main_{subPage}", self.getData, action="mousedown")
                CSS.onHoverClick(f"portalSubPage_nav_main_{subPage}", "buttonHover", "buttonClick")

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

    def uiRefresh(self):
        def slowUIRefresh():
            def download():
                def removeFromDownload(args):
                    el = args.target
                    for i in range(0, 6):
                        if el.id == "":
                            el = el.parentElement
                            continue

                        try:
                            int(el.id.split("_")[-1])
                        except ValueError:
                            el = el.parentElement
                            continue

                        WS.send(f'{self.mainCom} remove {el.id.split("_")[-1]}')
                        return None

                data = WS.dict()[self.mainCom]
                HTML.setElement("div", "portalSubPage_results_out", nest=self.getRecords(), style="divNormal")
                for index in reversed(data["downloads"]):
                    JS.addEvent(f"portalSubPage_results_rem_{index}", removeFromDownload, includeElement=True)
                    CSS.onHoverClick(f"portalSubPage_results_rem_{index}", "imgHover", "imgClick")

            if not JS.cache("portalSubPage") == "Download":
                return False

            data = WS.dict()[self.mainCom]
            if data != self.lastDataPackage:
                download()
                self.lastDataPackage = data

            JS.afterDelay(self.getData, delay=1000)
            JS.afterDelay(slowUIRefresh, delay=2000)

        self.lastDataPackage = {}
        JS.afterDelay(slowUIRefresh, delay=50)

    def downloadPage(self):
        def submitDownload(args):
            if hasattr(args, "key") and not args.key in ["Enter"]:
                return None

            input = HTML.getElement("download_input").value
            if not input.startswith("https://www.youtube.com/watch?v=") and not input.startswith("https://www.youtube.com/shorts/"):
                return None

            if (datetime.now() - timedelta(seconds=15)).timestamp() < self.lastDownload:
                JS.popup("alert", f"Please wait {int(self.lastDownload - (datetime.now() - timedelta(seconds=15)).timestamp())} seconds until starting the next download.")
                return None
            self.lastDownload = datetime.now().timestamp()

            configYTDL = loads(JS.cache("configYTDL"))
            if configYTDL["audioOnly"]:
                WS.send(f'{self.mainCom} download audio {configYTDL["quality"][0]} {input}')
            else:
                WS.send(f'{self.mainCom} download video {configYTDL["quality"][0]} {input}')

        dlHeader = HTML.genElement("h1", nest="YouTube Downloader", style="headerMain %% width: 100%; margin: 0px auto -4px auto;")
        dlInp = HTML.genElement("input", id="download_input", type="text", style="inputMedium %% width: 70%; margin: 10px 3px 10px auto;")
        dlBtn = HTML.genElement("button", nest="Download", id="download_button", type="button", style="buttonMedium %% width: 10%; margin: 10px auto 10px 3px;")
        dlBody = HTML.genElement("div", nest=dlInp + dlBtn, style="background %% flex %% width: 100%;  margin: 0px auto;")
        dl = HTML.genElement("div", nest=dlHeader + dlBody, id="portalSubPage_download", style="divNormal %% width: 95%;")

        resHeader = HTML.genElement("h1", nest="Recent Downloads", style="headerMain %% width: 100%; margin: 0px auto -4px auto;")
        resBody = HTML.genElement("div", id="portalSubPage_results_out", style="background %% width: 100%; min-height: 20px; margin: 0px auto;")
        res = HTML.genElement("div", nest=resHeader + resBody, id="portalSubPage_results", style="divNormal %% width: 95%; margin-top: 50px;")

        HTML.addElementRaw("portalSubPage", dl + res)

        def addEvents():
            JS.addEvent("download_input", submitDownload, action="keyup", includeElement=True)
            CSS.onHoverFocus("download_input", "inputHover", "inputFocus")
            JS.addEvent("download_button", submitDownload, includeElement=True)
            CSS.onHoverClick("download_button", "buttonHover", "buttonClick")

        JS.afterDelay(addEvents, delay=50)
        JS.afterDelay(self.uiRefresh, delay=100)

    def historyPage(self):
        def removeFromDownload(args):
            el = args.target
            for i in range(0, 6):
                if el.id == "":
                    el = el.parentElement
                    continue

                try:
                    int(el.id.split("_")[-1])
                except ValueError:
                    el = el.parentElement
                    continue

                WS.send(f'{self.mainCom} remove {el.id.split("_")[-1]}')
                return None

        resDiv = HTML.genElement("div", nest=self.getRecords(history=True), style="divNormal")

        resHeader = HTML.genElement("h1", nest="History", style="headerMain %% width: 95%; width: 100%;  margin: 0px auto -4px auto;")
        resBody = HTML.genElement("div", nest=resDiv, id="portalSubPage_results_out", style="background %% width: 100%; min-height: 20px; margin: 0px auto;")
        res = HTML.genElement("div", nest=resHeader + resBody, id="portalSubPage_results", style="divNormal %% width: 95%; ")

        HTML.addElementRaw("portalSubPage", res)

        def addEvents():
            data = WS.dict()[self.mainCom]
            for index in reversed(data["history"]):
                JS.addEvent(f"portalSubPage_results_rem_{index}", removeFromDownload, includeElement=True)
                CSS.onHoverClick(f"portalSubPage_results_rem_{index}", "imgHover", "imgClick")

        JS.afterDelay(addEvents, delay=50)

    def getRecords(self, history=False):
        dataKey = "history" if history else "downloads"
        data = WS.dict()[self.mainCom]
        records = ""
        for i, index in enumerate(reversed(data[dataKey])):
            values = HTML.genElement("h1", nest=index, style="headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;")
            remImg = HTML.genElement("img", id=f"portalSubPage_results_rem_img_{index}", style="width: 100%;", custom='src="docs/assets/Portal/Sonos/Trash.svg" alt="Rem"')
            remBtn = HTML.genElement("button", nest=remImg, id=f"portalSubPage_results_rem_{index}", style="buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;")
            rem = HTML.genElement("div", nest=remBtn, align="right", style="max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;")
            values += HTML.genElement("div", nest=rem, style="flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;")

            if type(data[dataKey][index]["Modified"]) is int:
                data[dataKey][index]["Modified"] = datetime.fromtimestamp(data[dataKey][index]["Modified"]).strftime("%d %b %y - %H:%M")

            for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                if not key2 is None:
                    txt = HTML.genElement("p", nest=key1, style="width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    if key1 == "State":
                        if data[dataKey][index][key1] == "Done":
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;")
                        elif data[dataKey][index][key1] == "Failed":
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #F05; overflow: hidden;")
                        else:
                            txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; color: #F85; overflow: hidden;")
                    else:
                        txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;")
                else:
                    txt = HTML.genElement("p", nest=key1, style="width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    if key1 in ["Link", "URL"]:
                        txt += HTML.linkWrap(data[dataKey][index][key1], nest=data[dataKey][index][key1], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    else:
                        txt += HTML.genElement("p", nest=data[dataKey][index][key1], style="width: 75%; margin: 0px auto; overflow: hidden;")
                    div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;")

                if not key2 is None:
                    txt = HTML.genElement("p", nest=key2, style="width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                    txt += HTML.genElement("p", nest=data[dataKey][index][key2], style="width: 50%; margin: 0px auto; overflow: hidden;")
                    div += HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;")
                    values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")
                    continue

                values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")

            if not data[dataKey][index]["Error"] == "":
                txt = HTML.genElement("p", nest="Error", style="width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;")
                txt += HTML.genElement("p", nest=data[dataKey][index]["Error"], style="width: 75%; margin: 0px auto; overflow: hidden;")
                div = HTML.genElement("div", nest=txt, style="divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;")
                values += HTML.genElement("div", nest=div, style="divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;")

            if i == 0:
                records += HTML.genElement("div", nest=values, style="divNormal %% margin: 0px auto 6px auto;")
                continue
            records += HTML.genElement("div", nest=values, style="divNormal %% margin: 0px auto 6px auto; padding: 8px 5px 5px 5px; border-top: 3px dashed #55F; border-radius: 0px;")

        return records

    def configPage(self):
        for button in self.extraButtons:
            if not button["active"]:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

        configYTDL = loads(JS.cache("configYTDL"))
        if configYTDL == {}:
            JS.cache("configYTDL", dumps(self.defaultConfig))
            configYTDL = self.defaultConfig

        dataTemp, configYTDL = (configYTDL, {})
        for i, key in enumerate(dict(self.knownFiles[JS.cache("portalSubPage")])):
            configYTDL[key] = {}
            try:
                configYTDL[key]["Value"] = dataTemp[key]
            except IndexError:
                configYTDL[key]["Value"] = ""

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
        HTML.setElementRaw("portalSubPage", sheet.generate(dict(configYTDL)))
        JS.afterDelay(sheet.generateEvents, kwargs={"onReloadCall": lambda: self.loadPortalSubPage(disableAnimation=True), "onSubmit": self.configPageSubmit}, delay=50)

    def configPageSubmit(self, key, value):
        configYTDL = loads(JS.cache("configYTDL"))
        if key in configYTDL:
            configYTDL[key] = value
            JS.cache("configYTDL", dumps(configYTDL))

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
            JS.afterDelay(self.loadPortalSubPage, args=(JS.cache("portalSubPage"),), delay=250)

        JS.onResize("ytdl", self.onResize)
