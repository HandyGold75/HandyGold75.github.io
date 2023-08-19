from WebKit import HTML, CSS, JS, WS, Widget
from json import dumps, loads
from datetime import datetime, timedelta
from json import load
from os import path as osPath


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
            WS.send(f'{self.mainCom} state')

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
            config = load(fileR)["ytdl"][JS.cache("portalPage")]
        for attribute in self.allConfigKeys:
            setattr(self, attribute, config[attribute])

        WS.onMsg("{\"" + self.mainCom + "\":", self.preload, kwargs={"firstRun": False}, oneTime=True)
        self.getData()

    def deload(self):
        def fininalize(self):
            self.busy = False

        self.busy = True
        JS.onResize("ytdl", None)

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
        mainDiv += HTML.genElement("div", id="portalSubPage", align="center", style="margin: 10px 0px; overflow: hidden;")
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

    def downloadPage(self):
        pass

    def historyPage(self):
        pass

    def configPage(self):
        for button in self.extraButtons:
            if not button["active"]:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

        fileData = loads(JS.cache("configYTDL"))
        if fileData == {}:
            JS.cache("configYTDL", dumps(self.defaultConfig))
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
            self.loadPortalSubPage(JS.cache("portalSubPage"))

        JS.onResize("ytdl", self.onResize)

    def pageSub(args=None):
        def download():
            def slowUIRefresh():
                def update(data):
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

                    records = ""

                    if data == glb.lastDataPackage:
                        return None

                    glb.lastDataPackage = data

                    for index in reversed(data["downloads"]):
                        values = HTML.genElement("h1", nest=f'{index}', style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                        remImg = HTML.genElement(f'img', id=f'portalSubPage_results_rem_img_{index}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                        remBtn = HTML.genElement(f'button', nest=f'{remImg}', id=f'portalSubPage_results_rem_{index}', style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                        rem = HTML.genElement(f'div', nest=f'{remBtn}', align=f'right', style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                        values += HTML.genElement(f'div', nest=f'{rem}', style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                        if type(data["downloads"][index]["Modified"]) is int:
                            data["downloads"][index]["Modified"] = f'{datetime.fromtimestamp(data["downloads"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                        for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                            if not key2 is None:
                                txt = HTML.genElement("p", nest=key1, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                                if key1 == "State":
                                    if data["downloads"][index][key1] == "Done":
                                        txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                                    elif data["downloads"][index][key1] == "Failed":
                                        txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                                    else:
                                        txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                                else:
                                    txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                                div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                            else:
                                txt = HTML.genElement("p", nest=key1, style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                                txt += HTML.genElement("p", nest=f'{data["downloads"][index][key1]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                                div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                            if not key2 is None:
                                txt = HTML.genElement("p", nest=key2, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                                txt += HTML.genElement("p", nest=f'{data["downloads"][index][key2]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                                div += HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                                values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                                continue

                            values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                        if not data["downloads"][index]["Error"] == "":
                            txt = HTML.genElement("p", nest=f'Error', style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.genElement("p", nest=f'{data["downloads"][index]["Error"]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                            div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                            values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                        records += HTML.genElement("div", nest=f'{values}', style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

                    HTML.setElement("div", f'portalSubPage_results_out', nest=f'{records}', style=f'divNormal')

                    for index in reversed(data["downloads"]):
                        JS.addEvent(f'portalSubPage_results_rem_{index}', removeFromDownload, includeElement=True)
                        CSS.onHoverClick(f'portalSubPage_results_rem_{index}', f'imgHover', f'imgClick')

                if not JS.cache("page_portalSub") == "Download":
                    return False

                data = WS.dict()[self.mainCom]

                try:
                    update(data)
                except AttributeError:
                    return None

                JS.afterDelay(getData, delay=2000)
                JS.afterDelay(slowUIRefresh, delay=2500)

            def addHeader():
                HTML.addElement(f'h1', f'portalSubPage_header', nest=f'YouTube Downloader', style=f'headerBig %% margin: 0px auto;')

            def addDownload():
                def submitDownload(args):
                    if hasattr(args, "key") and not args.key in ["Enter"]:
                        return None

                    input = HTML.getElement("download_input").value

                    if not input.startswith("https://www.youtube.com/watch?v=") and not input.startswith("https://www.youtube.com/shorts/"):
                        return None

                    if (datetime.now() - timedelta(seconds=15)).timestamp() < glb.lastDownload:
                        JS.popup("alert", f'Please wait {int(glb.lastDownload - (datetime.now() - timedelta(seconds=15)).timestamp())} seconds until starting the next download.')
                        return None

                    glb.lastDownload = datetime.now().timestamp()

                    if glb.config["audioOnly"]:
                        WS.send(f'{self.mainCom} download audio {glb.config["quality"][0]} {input}')
                    else:
                        WS.send(f'{self.mainCom} download video {glb.config["quality"][0]} {input}')

                HTML.addElement(f'input', f'portalSubPage_download', id=f'download_input', type=f'text', style=f'inputMedium %% width: 75%;')
                HTML.addElement(f'button', f'portalSubPage_download', nest=f'Download', id=f'download_button', type=f'button', style=f'buttonMedium %% width: 25%;')

                JS.addEvent(f'download_input', submitDownload, action="keyup", includeElement=True)
                CSS.onHoverFocus(f'download_input', f'inputHover', f'inputFocus')

                JS.addEvent(f'download_button', submitDownload, includeElement=True)
                CSS.onHoverClick(f'download_button', f'buttonHover', f'buttonClick')

            def addResults():
                data = WS.dict()[self.mainCom]

                HTML.addElement(f'h1', f'portalSubPage_results', nest=f'Recent Downloads', style=f'headerBig %% margin: 0px auto;')
                HTML.addElement(f'div', f'portalSubPage_results', id=f'portalSubPage_results_out', style=f'divNormal %% margin-bottom: 0px;')

            HTML.setElement(f'div', f'portalSubPage', id=f'portalSubPage_header', style=f'divNormal %% flex %% width: 95%;')
            HTML.addElement(f'div', f'portalSubPage', id=f'portalSubPage_download', style=f'divNormal %% flex %% width: 75%;')
            HTML.addElement(f'div', f'portalSubPage', id=f'portalSubPage_results', style=f'divNormal %% width: 95%; margin-top: 50px;')

            addHeader()
            addDownload()
            addResults()

            JS.afterDelay(slowUIRefresh, delay=50)

        def history():
            def update(data):
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

                records = ""

                if data == glb.lastDataPackage:
                    return None

                glb.lastDataPackage = data

                for index in reversed(data["history"]):
                    values = HTML.genElement("h1", nest=f'{index}', style=f'headerMedium %% margin: 0px 0px 0px 5px; text-align: left; position: absolute;')

                    remImg = HTML.genElement(f'img', id=f'portalSubPage_results_rem_img_{index}', style=f'width: 100%;', custom=f'src="docs/assets/Portal/Sonos/Trash.png" alt="Rem"')
                    remBtn = HTML.genElement(f'button', nest=f'{remImg}', id=f'portalSubPage_results_rem_{index}', style=f'buttonImg %% padding: 2px; background: transparent; border: 0px solid #222; border-radius: 4px;')
                    rem = HTML.genElement(f'div', nest=f'{remBtn}', align=f'right', style=f'max-width: 50px; max-height: 50px; margin: 0px 0px 0px auto;')
                    values += HTML.genElement(f'div', nest=f'{rem}', style=f'flex %% width: 7.5%; height: 0px; margin: 0px 0px 0px 92.5%;')

                    if type(data["history"][index]["Modified"]) is int:
                        data["history"][index]["Modified"] = f'{datetime.fromtimestamp(data["history"][index]["Modified"]).strftime("%d %b %y - %H:%M")}'

                    for key1, key2 in (("Title", None), ("Link", None), ("URL", None), ("State", "Modified"), ("Resolution", "AudioBitrate")):
                        if not key2 is None:
                            txt = HTML.genElement("p", nest=key1, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            if key1 == "State":
                                if data["history"][index][key1] == "Done":
                                    txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #0F5; overflow: hidden;')
                                elif data["history"][index][key1] == "Failed":
                                    txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F05; overflow: hidden;')
                                else:
                                    txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; color: #F85; overflow: hidden;')
                            else:
                                txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px; border-right: 2px solid #111; border-radius: 0px;')
                        else:
                            txt = HTML.genElement("p", nest=key1, style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.genElement("p", nest=f'{data["history"][index][key1]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                            div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')

                        if not key2 is None:
                            txt = HTML.genElement("p", nest=key2, style=f'width: 50%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                            txt += HTML.genElement("p", nest=f'{data["history"][index][key2]}', style=f'width: 50%; margin: 0px auto; overflow: hidden;')
                            div += HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 50%; margin: 0px auto; padding: 0px;')

                            values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')
                            continue

                        values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    if not data["history"][index]["Error"] == "":
                        txt = HTML.genElement("p", nest=f'Error', style=f'width: 25%; margin: 0px auto; border-right: 2px dotted #111; border-radius: 0px;')
                        txt += HTML.genElement("p", nest=f'{data["history"][index]["Error"]}', style=f'width: 75%; margin: 0px auto; overflow: hidden;')
                        div = HTML.genElement("div", nest=f'{txt}', style=f'divNormal %% flex %% width: 100%; margin: 0px auto; padding: 0px;')
                        values += HTML.genElement("div", nest=f'{div}', style=f'divNormal %% flex %% width: 82.5%; margin: 0px auto -2px auto; padding: 0px; border: 2px solid #111; border-radius: 4px;')

                    records += HTML.genElement("div", nest=f'{values}', style=f'divNormal %% margin: 0px auto -6px auto; border: 6px solid #FBDF56; border-radius: 4px;')

                HTML.setElement("div", f'portalSubPage_results_out', nest=f'{records}', style=f'divNormal')

                for index in reversed(data["history"]):
                    JS.addEvent(f'portalSubPage_results_rem_{index}', removeFromDownload, includeElement=True)
                    CSS.onHoverClick(f'portalSubPage_results_rem_{index}', f'imgHover', f'imgClick')

            def addHeader():
                HTML.addElement(f'h1', f'portalSubPage_header', nest=f'History', style=f'headerBig %% margin: 0px auto;')

            def addResults():
                data = WS.dict()[self.mainCom]

                HTML.addElement(f'div', f'portalSubPage_results', id=f'portalSubPage_results_out', style=f'divNormal %% margin-bottom: 0px;')
                update(data)

            HTML.setElement(f'div', f'portalSubPage', id=f'portalSubPage_header', style=f'divNormal %% flex %% width: 95%;')
            HTML.addElement(f'div', f'portalSubPage', id=f'portalSubPage_results', style=f'divNormal %% width: 95%; margin-top: 50px;')

            addHeader()
            addResults()

        pageSubMap = {"Download": download, "History": history, "Config": config}

        HTML.clrElement(f'portalSubPage')
        glb.lastDataPackage = {}

        pageSubMap[JS.cache("page_portalSub")]()
