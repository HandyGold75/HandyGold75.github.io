from datetime import datetime, timedelta
from json import load
from os import path as osPath

from WebKit import CSS, HTML, JS, WS, Buttons, Widget


class PortalPage:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self._lastUpdate = 0
        self._pageName = ""

        # May be reconfigured
        self.evalMap = {}
        self.configKeys = ["mainCom", "extraButtons"]
        self.mainComReadCommands = ["read"]
        self.subPages = []
        self.requireLogin = True

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
        self.extraButtons = None

    def getData(self):
        if (datetime.now() - timedelta(seconds=1)).timestamp() > self._lastUpdate:
            for com in self.mainComReadCommands:
                WS.send(f"{self.mainCom} {com}")

            self._lastUpdate = datetime.now().timestamp()

    def _onResize(self):
        if JS.getWindow().innerWidth < 500:
            CSS.setStyle("portalPageNav", "width", "75%")
            return None
        elif JS.getWindow().innerWidth < 1000:
            CSS.setStyle("portalPageNav", "width", "82.5%")
            return None
        CSS.setStyle("portalPageNav", "width", "90%")

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

        if firstRun and self.onPreload() is False:
            return None

        if self.subPages == []:
            if "subPages" in config:
                self.subPages = config["subPages"]
            elif "knownFiles" in config:
                self.subPages = list(config["knownFiles"])
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
            navBtns += Buttons.small(f'portalSubPage_nav_options_{button["id"]}', button["text"], buttonKwargs={"align": "right"}, onClick=self.evalMap[button["function"]])
        navDivs += HTML.genElement("div", id="portalSubPage_nav_options", nest=navBtns, align="right", style="width: 40%;")

        mainDiv = HTML.genElement("div", id="portalPageNav", nest=navDivs, align="center", style="pagePortal_Nav")
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
