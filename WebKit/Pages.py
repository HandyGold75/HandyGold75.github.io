from datetime import datetime, timedelta
from json import dumps, load, loads
from os import path as osPath

from WebKit import CSS, HTML, JS, WS, Buttons, Widget


class PortalPage:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self._lastUpdate = 0
        self._pageName = ""

        # May be reconfigured
        self.evalMap = {}
        self.configKeys = ["mainCom"]
        self.optinalConfigKeys = ["subPages", "customSheets", "extraButtons", "defaultCachedConfig", "optionsDict", "dates"]
        self.mainComReadCommands = ["read"]
        self.requireLogin = True
        self.wordWrap = False

        # May be reconfigured in pagesConfig.json
        self.subPages = []
        self.customSheets = []
        self.extraButtons = []
        self.defaultCachedConfig = {}
        self.optionsDict = {}
        self.dates = ["Modified"]

        # May hook onto existing functions
        self.onResize = lambda: None
        self.onPreload = lambda: None
        self.onDeload = lambda: None
        self.onLayout = lambda: None
        self.onSubPageLoad = lambda: None

        # May be used during runtime
        self.busy = False

        # May be read after preload
        self.mainCom = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self._lastUpdate:
            for com in self.mainComReadCommands:
                WS.send(f"{self.mainCom} {com}")

            self._lastUpdate = datetime.now().timestamp()

    def _onResize(self):
        if self._pageName != JS.cache("portalPage"):
            return None

        self.onResize()

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

        self._pageName = JS.cache("portalPage")

        if not firstRun:
            if self.busy:
                CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
                JS.afterDelay(finalize, (self,), delay=250)
            return None

        self.busy = True
        self._lastUpdate = 0

        content = HTML.genElement("h1", nest="Portal", style="headerMain")
        content += HTML.genElement("p", nest="Loading page", style="textBig")
        content += HTML.genElement("p", nest="Getting data from the server", id="portalSubPage_loadingTxt", style="textBig")
        HTML.setElement("div", "portalPage", nest=content, id="portalSubPage_summary", align="center")

        CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
        JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", "0px"))
        JS.aSync(loadingTxt)

        with open(f"{osPath.split(__file__)[0]}/pagesConfig.json", "r", encoding="UTF-8") as fileR:
            config = load(fileR)[self._pageName]

        for attribute in self.configKeys:
            setattr(self, attribute, config[attribute])
        for attribute in self.optinalConfigKeys:
            if attribute in config:
                setattr(self, attribute, config[attribute])

        if firstRun and self.onPreload() is False:
            return None

        if self.subPages == []:
            if self.customSheets != [] and "customSheets" in config:
                self.subPages = list(self.customSheets)
            else:
                raise LookupError("Can't resolve subPages from config!")

        WS.onMsg('{"' + self.mainCom + '":', self.preload, kwargs={"firstRun": False}, oneTime=True)
        self.getData()

    def deload(self):
        def fininalize(self):
            self.busy = False

        self.busy = True
        self.onDeload()

        JS.onResize(self._pageName, None)
        for attribute in self.configKeys:
            setattr(self, attribute, None)

        self.__init__()

        CSS.setStyles("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px')))
        JS.aSync(CSS.setStyle, ("portalSubPage", "maxHeight", "0px"))
        JS.afterDelay(fininalize, (self,), delay=250)

    def startLoadSubPage(self, subPage):
        self.getData()
        self._loadPortalSubPage(subPage)

    def _layout(self):
        navBtns = ""
        for subPage in self.subPages:
            navBtns += Buttons.small(f"portalSubPage_nav_main_{subPage}", subPage, onClick=self.startLoadSubPage, args=(subPage,))

        if navBtns == "":
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="Unauthorized!\nReload the page if you think this is a mistake.", style="textBig")
            HTML.setElement("div", "portalPage", nest=header + body, id="loginPage", align="center")
            HTML.disableElement(f'portalSubPage_button_{JS.cache("portalSubPage")}')
            return None

        navDivs = HTML.genElement("div", id="portalSubPage_nav_main", nest=navBtns, align="left", style="width: 60%;")
        navBtns = ""
        for button in self.extraButtons:
            if "function" in button:
                navBtns += Buttons.small(f'portalSubPage_nav_options_{button["id"]}', button["text"], buttonKwargs={"align": "right"}, onClick=self.evalMap[button["function"]])
            else:
                txt = button["text"] if getattr(self, button["toggleVar"]) else button["textInactive"]
                navBtns += Buttons.small(f'portalSubPage_nav_options_{button["id"]}', txt, buttonKwargs={"align": "right"}, onClick=self._toggleOption, args=(f'portalSubPage_nav_options_{button["id"]}',))
        navDivs += HTML.genElement("div", id="portalSubPage_nav_options", nest=navBtns, align="right", style="width: 40%;")

        mainDiv = HTML.genElement("div", id="portalPageNav", nest=navDivs, align="center", style="display: flex; padding: 5px; margin: 0px 5% 10px 5%; border: 6px solid #111; border-radius: 10px; transition: margin 0.25s 0.1s;")
        mainDiv += HTML.genElement("div", id="portalSubPage", align="center", style="margin: 10px 0px; overflow: hidden;")
        HTML.setElementRaw("portalPage", mainDiv)

        for button in self.extraButtons:
            if not button["active"]:
                JS.aSync(HTML.disableElement, args=(f'portalSubPage_nav_options_{button["id"]}',))

        Buttons.applyEvents()

        self.onLayout()

    def _flyin(self):
        CSS.setStyle("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px')
        JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", "0px"))

    def _loadPortalSubPage(self, portalSubPage: str = None, firstRun: bool = True, disableAnimation: bool = False):
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
            JS.afterDelay(self._loadPortalSubPage, kwargs={"firstRun": False}, delay=250)
            return None

        HTML.clrElement("portalSubPage")

        self.onSubPageLoad()

        if not disableAnimation:
            CSS.setStyle("portalSubPage", "maxHeight", "")
            elHeight = f'{CSS.getAttribute("portalSubPage", "offsetHeight")}px'
            CSS.setStyle("portalSubPage", "maxHeight", "0px")
            JS.aSync(CSS.setStyles, ("portalSubPage", (("transition", "max-height 0.25s"), ("maxHeight", elHeight))))
            JS.afterDelay(CSS.setStyle, ("portalSubPage", "maxHeight", ""), delay=250)

        self.busy = False

    def _toggleOption(self, id):
        for button in self.extraButtons:
            if id.split("_")[-1] != button["id"]:
                continue

            option = not getattr(self, button["toggleVar"])
            setattr(self, button["toggleVar"], option)
            CSS.setAttribute(id, "innerHTML", button["text"] if option else button["textInactive"])

            break

        self._loadPortalSubPage()

    def enableButtons(self, exceptions: tuple | list = ()):
        for button in self.extraButtons:
            if not button["active"] and not button["text"] in exceptions:
                HTML.enableElement(f'portalSubPage_nav_options_{button["id"]}')

    def configPage(self):
        self.enableButtons()

        options = (lambda: dict(self.optionsDict[JS.cache("portalSubPage")]) if JS.cache("portalSubPage") in self.optionsDict else {})()
        self.sheet = Widget.sheetConfig(
            name=JS.cache("portalSubPage"),
            header=("Key", "Value"),
            data=self.getCachedConfig(),
            dates=self.dates,
            wordWrap=self.wordWrap,
            optionsDict=options,
        )
        HTML.setElementRaw("portalSubPage", self.sheet.generateSheet() + HTML.genElement("div", style="height: 100px;"))
        JS.afterDelay(self.sheet.generateEvents, kwargs={"onMod": self.modCachedConfig}, delay=50)

    def modCachedConfig(self, key, data):
        config = self.getCachedConfig()
        if key in config:
            config[key] = data
            JS.cache(f"config{self._pageName}", dumps(config))

    def getCachedConfig(self):
        config = JS.cache(f"config{self._pageName}")
        config = self.defaultCachedConfig if config is None else loads(config)

        if tuple(config) != tuple(self.defaultCachedConfig):
            config = self.defaultCachedConfig
            JS.cache(f"config{self._pageName}", dumps(config))

        return config

    def main(self):
        if self.requireLogin and not self.mainCom in WS.dict():
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="No data was found, please renavigate to this page.", style="textBig")
            HTML.setElement("div", "portalPage", nest=header + body, id="loginPage", align="center")
            self._flyin()
            return None

        self._layout()
        self._flyin()

        if not JS.cache("portalSubPage") == "":
            JS.afterDelay(self._loadPortalSubPage, args=(JS.cache("portalSubPage"),), delay=250)

        JS.onResize(self._pageName, self._onResize)
