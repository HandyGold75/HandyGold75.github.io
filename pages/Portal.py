from subsPortal.init import sheets, sheetsV2, sonos, tapo, trees, ytdl
from WebKit.init import CSS, HTML, JS, WS


class portal:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = True

        for item in ["portalPage", "portalSubPage"]:
            if JS.cache(item) is None:
                JS.cache(item, "")

        self.portalPagesDefault = {
            "Admin": {
                "hidden": True,
                "page": None,
                "loads": sheets,
                "command": "admin",
            },
            "Monitor": {
                "hidden": True,
                "page": None,
                "loads": trees,
                "command": "monitor",
            },
            "Sonos": {
                "hidden": True,
                "page": None,
                "loads": sonos,
                "command": "sonos",
            },
            "Tapo": {
                "hidden": True,
                "page": None,
                "loads": tapo,
                "command": "tapo",
            },
            "YT-DL": {
                "hidden": True,
                "page": None,
                "loads": ytdl,
                "command": "yt",
            },
            "Asset Manager": {
                "hidden": True,
                "page": None,
                "loads": sheets,
                "command": "am",
            },
            "License Manager": {
                "hidden": True,
                "page": None,
                "loads": sheets,
                "command": "lm2",
            },
            "Query": {
                "hidden": True,
                "page": None,
                "loads": sheets,
                "command": "qr",
            },
        }
        self.portalPages = self.portalPagesDefault

        self.oldPage = None
        self.loadingPage = False
        self.busyCount = 0

    def onResize(self):
        if JS.getWindow().innerWidth < 500:
            if HTML.getElement("portalPage_button_showHideImg").alt == "Fold":
                CSS.setStyles("portalFlyout", (("padding", "0px"), ("width", "7.5%")))
            return None
        elif JS.getWindow().innerWidth < 1000:
            if HTML.getElement("portalPage_button_showHideImg").alt == "Fold":
                CSS.setStyles("portalFlyout", (("padding", "5px 0px"), ("width", "7.5%")))
            return None
        if HTML.getElement("portalPage_button_showHideImg").alt == "Fold":
            CSS.setStyles("portalFlyout", (("padding", "5px 0.5%"), ("width", "6.5%")))

    def preload(self):
        self.busy = True
        if not WS.loginState() or not "access" in WS.dict():
            return None

        for page in self.portalPages:
            if self.portalPages[page]["page"] is None and self.portalPages[page]["command"] in WS.dict()["access"]:
                self.portalPages[page]["page"] = self.portalPages[page]["loads"]()
        self.busy = False

    def deload(self):
        self.busy = True
        self.portalPages = self.portalPagesDefault
        JS.onResize("portal", None)

        if not self.oldPage is None:
            self.deloadPortalPage()
        else:
            self.busy = False

    def layout(self):
        def showHideFlyout(self):
            if self.busy:
                return None
            self.busy = True

            el = HTML.getElement("portalPage_button_showHideImg")
            if el.src.endswith("docs/assets/Portal/Hide-H.svg"):
                el.src = "docs/assets/Portal/Show-H.svg"
                el.alt = "Unfold"

                CSS.setStyle("portalPage", "marginLeft", "auto")
                CSS.setStyle("portalFlyout", "maxHeight", f'{CSS.getAttribute("portalFlyout", "offsetHeight")}px')

                JS.aSync(CSS.setStyles, ("portalFlyout", (("maxWidth", "30px"), ("maxHeight", "32px"), ("marginRight", "-30px"), ("padding", "0px"), ("width", "7.5%"))))
                JS.afterDelay(CSS.setStyle, ("portalPage", "width", "100%"), delay=100)

                JS.afterDelay(CSS.setStyle, ("portalPage", "marginLeft", "0px"), delay=350)
                for page in self.portalPages:
                    CSS.setStyle(f"portalPage_button_{page}Div", "marginLeft", f'-{CSS.getAttribute("portalFlyout", "offsetWidth")}px')

                JS.afterDelay(setattr, (self, "busy", False), delay=350)
                for delay in range(10, 370, 10):
                    JS.afterDelay(JS.glb.onResize, delay=delay)
                return None

            el.src = "docs/assets/Portal/Hide-H.svg"
            el.alt = "Fold"

            CSS.setStyles("portalPage", (("marginLeft", "auto"), ("width", "92.5%")))

            CSS.setStyle("portalFlyout", "maxHeight", f'-{CSS.getAttribute("portalFlyout", "offsetHeight")}px')
            JS.afterDelay(CSS.setStyles, ("portalFlyout", (("maxWidth", "107px"), ("maxHeight", "1000px"), ("marginRight", "0px"))), delay=100)

            JS.afterDelay(CSS.setStyle, ("portalPage", "marginLeft", "0px"), delay=350)
            JS.afterDelay(CSS.setStyle, ("portalFlyout", "maxHeight", ""), delay=350)

            for page in self.portalPages:
                JS.afterDelay(CSS.setStyle, (f"portalPage_button_{page}Div", "marginLeft", "0px"), delay=100)

            JS.afterDelay(setattr, (self, "busy", False), delay=350)
            for delay in range(10, 370, 10):
                JS.afterDelay(JS.glb.onResize, delay=delay)

        for page in self.portalPages:
            if not self.portalPages[page]["page"] is None:
                break
        else:
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="You don't have access to any portals!<br>Please request access if you think this is a mistake.", style="textBig")
            HTML.setElement("div", "mainPage", nest=header + body, id="portalPage", align="center", style="width: 92.5%; margin: 0px; overflow: hidden; transition: margin-left 0.25s, width 0.25s;")

        flyoutImg = HTML.genElement("img", id="portalPage_button_showHideImg", style="width: 100%;", custom='src="docs/assets/Portal/Hide-H.svg" alt="Fold"')
        flyoutBtn = HTML.genElement("button", id="portalPage_button_showHide", nest=flyoutImg, style="buttonImg")
        flyoutDivs = HTML.genElement("div", nest=flyoutBtn, id="portalPage_button_showHideDiv", align="center", style="width: 100%; margin: 0px auto 5px 0px;")

        for i, page in enumerate(self.portalPages):
            divStyle = "width: 100%; margin: 5px auto 5px 0px; transition: margin 0.25s;"
            if i + 1 >= len(self.portalPages):
                divStyle = "width: 100%; margin: 5px auto 0px 0px; transition: margin 0.25s;"

            flyoutImg = HTML.genElement("img", style="width: 100%;", custom=f'src="docs/assets/Portal/{page}.svg" alt="{page}"')
            flyoutBtn = HTML.genElement("button", id=f"portalPage_button_{page}", nest=flyoutImg, style="buttonImg")
            flyoutDivs += HTML.genElement("div", nest=flyoutBtn, id=f"portalPage_button_{page}Div", align="center", style=divStyle)

        minMaxRequirements = " min-width: 30px; max-width: 107px; transition: max-width 0.25s, max-height 0.25s, margin 0.25s, width 0.25s, padding 0.25s"
        flyout = HTML.genElement(
            "div", nest=flyoutDivs, id="portalFlyout", align="left", style=f"z-index: 999; width: 6.5%; height: 100%; margin: -11px 0px -11px -11px; padding: 5px 0.5%; background: #222; border: 6px solid #111; border-radius: 10px;{minMaxRequirements}"
        )
        portalPage = HTML.genElement("div", id="portalPage", align="center", style="width: 92.5%; margin: 0px; overflow: hidden; transition: margin-left 0.25s, width 0.25s;")
        HTML.setElement("div", "mainPage", nest=flyout + portalPage, id="portalWrapper", align="center", style="flex")

        def addEvents():
            self.busy = True

            JS.addEvent("portalPage_button_showHide", showHideFlyout, (self,))
            CSS.onHoverClick("portalPage_button_showHide", "imgHover", "imgClick")

            for page in self.portalPages:
                JS.addEvent(f"portalPage_button_{page}", self.loadPortalPage, kwargs={"page": page})
                CSS.onHoverClick(f"portalPage_button_{page}", "imgHover", "imgClick")

            self.busy = False

        JS.afterDelay(addEvents, delay=50)

    def flyin(self):
        CSS.setStyle("portalWrapper", "marginTop", f'-{CSS.getAttribute("portalWrapper", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("portalWrapper", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def deloadPortalPage(self, page: str = None, firstRun: bool = True):
        if firstRun:
            self.busyCount = 0
            JS.aSync(self.portalPages[self.oldPage]["page"].deload)
            CSS.setStyle("portalPage", "marginLeft", "0px")
            JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px'))
            JS.afterDelay(self.deloadPortalPage, kwargs={"page": page, "firstRun": False}, delay=250)
            return None

        if self.portalPages[self.oldPage]["page"].busy:
            self.busyCount += 1
            if self.busyCount <= 15:
                JS.afterDelay(self.deloadPortalPage, kwargs={"page": page, "firstRun": False}, delay=50)
                return None

            JS.log(f"Warning: Force stopped page (Reason page is busy for to long) -> {self.oldPage}")
            self.portalPages[self.oldPage]["page"].busy = False

        self.oldPage = None
        CSS.setStyle("portalPage", "marginLeft", "0px")
        if page is None:
            self.busy = False
        else:
            self.loadPortalPage(page, deloaded=True, rememberSubPage=True)

    def stallPortalPage(self, page: str, firstRun: bool = True):
        if firstRun:
            self.busyCount = 0

        if self.portalPages[page]["page"].busy:
            self.busyCount += 1
            if self.busyCount <= 100:
                JS.afterDelay(self.stallPortalPage, kwargs={"page": page, "firstRun": False}, delay=50)
                return None

            JS.log(f"Warning: Force loaded page (Reason page is busy for to long) -> {page}")
            self.portalPages[page]["page"].busy = False

        self.loadPortalPage(page, didStall=True, rememberSubPage=True)

    def loadPortalPage(self, page: str = None, deloaded: bool = False, didStall: bool = False, rememberSubPage: bool = False):
        if self.loadingPage and not deloaded and not didStall:
            return None

        if not rememberSubPage:
            JS.cache("portalSubPage", "")

        self.loadingPage = True
        self.busy = True
        if not self.oldPage is None and not deloaded:
            self.deloadPortalPage(page)
            return None

        if not didStall:
            JS.cache("portalPage", page)

            HTML.clrElement("portalPage")
            self.portalPages[page]["page"].preload()
            if self.portalPages[page]["page"].busy:
                self.stallPortalPage(page)
                return None

        JS.setTitle(f'HandyGold75 - {JS.cache("mainPage")} - {JS.cache("portalPage")}')
        HTML.setElementRaw("mainNav_title", f'HandyGold75 - {JS.cache("mainPage")} - {JS.cache("portalPage")}')
        JS.aSync(self.portalPages[page]["page"].main)

        self.oldPage = page
        self.loadingPage = False
        self.busy = False

    def main(self):
        if not WS.loginState():
            return None

        self.layout()
        self.flyin()

        if not JS.cache("portalPage") == "":
            self.loadPortalPage(JS.cache("portalPage"), rememberSubPage=True)

        JS.onResize("portal", self.onResize)
