from subsPortal import sheets, sonos, tapo, trees, ytdl
from WebKit import CSS, HTML, JS, WS, Buttons, Page


class portal(Page):
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        super().__init__()

        self.onPreload = self.doOnPreload
        self.onDeload = self.doOnDeload
        self.onLayout = self.doOnLayout

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
                "command": "lm",
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

    def doOnPreload(self):
        if not WS.loginState() or not "access" in WS.dict():
            return None

        for page in self.portalPages:
            if self.portalPages[page]["page"] is None and self.portalPages[page]["command"] in WS.dict()["access"]:
                self.portalPages[page]["page"] = self.portalPages[page]["loads"]()

    def doOnDeload(self):
        self.portalPages = self.portalPagesDefault

        if not self.oldPage is None:
            self.deloadPortalPage()
        else:
            self.busy = False

    def doOnLayout(self):
        for page in self.portalPages:
            if not self.portalPages[page]["page"] is None:
                break
        else:
            header = HTML.genElement("h1", nest="Portal", style="headerMain")
            body = HTML.genElement("p", nest="You don't have access to any portals!<br>Please request access if you think this is a mistake.", style="textBig")
            HTML.setElement("div", "subPage", nest=header + body, id="portalPage", align="center", style="width: 89%; margin: 0px; overflow: hidden; transition: margin-left 0.25s, width 0.25s;")

        showHideBtn = Buttons.imgMedium("portalPage_button_showHide", "./docs/assets/Portal/Hide-H.svg", alt="Fold", onClick=self.showHideFlyout)
        pageBtns = "".join(Buttons.imgMedium(f"portalPage_button_{page}", f"./docs/assets/Portal/{page}.svg", alt=page, onClick=self.loadPortalPage, args=(page,)) for page in self.portalPages if not self.portalPages[page]["page"] is None)

        minMaxRequirements = "height: 100%; max-width: 76px; min-height: 47px; transition: max-width 0.25s, max-height 0.25s;"
        flyout = HTML.genElement(
            "div",
            nest=showHideBtn + pageBtns,
            id="portalFlyout",
            align="left",
            style=f"z-index: 999; margin: -5px 0px -11px -5px; background: #222; border-right: 6px solid #111; border-bottom: 6px solid #111; border-bottom-right-radius: 8px; overflow: hidden; {minMaxRequirements}",
        )
        portalPage = HTML.genElement("div", id="portalPage", align="center", style="width: calc(100% - 76px); margin: -11px 0px 0px 0px; overflow: hidden; transition: margin-left 0.25s, width 0.25s;")
        HTML.setElement("div", "subPage", nest=flyout + portalPage, id="portalWrapper", align="center", style="flex")

        Buttons.applyEvents()

        if not JS.cache("portalPage") == "":
            self.loadPortalPage(JS.cache("portalPage"), rememberSubPage=True)

    def showHideFlyout(self):
        if self.busy:
            return None
        self.busy = True

        el = HTML.getElement("portalPage_button_showHide_img")
        if el.src.endswith("docs/assets/Portal/Hide-H.svg"):
            el.src = "docs/assets/Portal/Show-H.svg"
            el.alt = "Unfold"

            CSS.setStyle("portalPage", "marginLeft", "auto")
            CSS.setStyle("portalPageNav", "margin", "0px max(5%, 57px) 10px max(5%, 57px)")

            CSS.setStyle("portalFlyout", "maxHeight", f'{CSS.getAttribute("portalFlyout", "offsetHeight")}px')
            JS.aSync(CSS.setStyles, ("portalFlyout", (("maxWidth", "47px"), ("maxHeight", "47px"), ("marginRight", "-47px"))))
            JS.aSync(CSS.setAttribute, ("portalPage_button_showHide", "className", "imgBtn imgBtnSmall"))

            JS.afterDelay(CSS.setStyle, ("portalPage", "width", "100%"), delay=100)
            JS.afterDelay(CSS.setStyle, ("portalPage", "marginLeft", "0px"), delay=350)

            JS.afterDelay(setattr, (self, "busy", False), delay=350)
            for delay in range(10, 370, 10):
                JS.afterDelay(JS.glb.onResize, delay=delay)
            return None

        el.src = "docs/assets/Portal/Hide-H.svg"
        el.alt = "Fold"

        CSS.setStyles("portalPage", (("marginLeft", "auto"), ("width", "calc(100% - 76px)")))
        CSS.setStyle("portalPageNav", "margin", "0px 5% 10px 5%")

        CSS.setStyle("portalFlyout", "maxHeight", f'-{CSS.getAttribute("portalFlyout", "offsetHeight")}px')
        JS.afterDelay(CSS.setStyles, ("portalFlyout", (("maxWidth", "76px"), ("maxHeight", f"{JS.getVP()[0]}px"), ("marginRight", "0px"))), delay=100)
        JS.afterDelay(CSS.setAttribute, ("portalPage_button_showHide", "className", "imgBtn imgBtnMedium"), delay=100)
        JS.afterDelay(CSS.setStyle, ("portalFlyout", "maxHeight", ""), delay=350)

        JS.afterDelay(CSS.setStyle, ("portalPage", "marginLeft", "0px"), delay=350)

        JS.afterDelay(setattr, (self, "busy", False), delay=350)
        for delay in range(10, 370, 10):
            JS.afterDelay(JS.glb.onResize, delay=delay)

    def deloadPortalPage(self, page: str = None, firstRun: bool = True, busyCount: int = 0):
        if firstRun:
            JS.aSync(self.portalPages[self.oldPage]["page"].deload)
            CSS.setStyle("portalPage", "marginLeft", "0px")
            JS.aSync(CSS.setStyle, ("portalPage", "marginLeft", f'-{CSS.getAttribute("portalPage", "offsetWidth")}px'))
            JS.aSync(self.deloadPortalPage, kwargs={"page": page, "firstRun": False, "busyCount": busyCount})
            return None

        if self.portalPages[self.oldPage]["page"].busy:
            if busyCount <= 20:
                JS.afterDelay(self.deloadPortalPage, kwargs={"page": page, "firstRun": False, "busyCount": busyCount + 1}, delay=50)
                return None

            JS.log(f"Warning: Force stopped page (Reason page is busy for to long) -> {self.oldPage}")
            self.portalPages[self.oldPage]["page"].busy = False

        self.oldPage = None
        CSS.setStyle("portalPage", "marginLeft", "0px")
        if page is None:
            self.busy = False
        else:
            self.loadPortalPage(page, didDeload=True, rememberSubPage=True)

    def preloadPortalPage(self, page: str, firstRun: bool = True, busyCount: int = 0):
        if firstRun:
            HTML.clrElement("portalPage")
            JS.aSync(self.portalPages[page]["page"].preload)
            JS.aSync(self.preloadPortalPage, kwargs={"page": page, "firstRun": False})
            return None

        if self.portalPages[page]["page"].busy:
            if busyCount <= 40:
                JS.afterDelay(self.preloadPortalPage, kwargs={"page": page, "firstRun": False, "busyCount": busyCount + 1}, delay=50)
                return None

            JS.log(f"Warning: Force loaded page (Reason page is busy for to long) -> {page}")
            self.portalPages[page]["page"].busy = False

        self.loadPortalPage(page, didPreload=True, rememberSubPage=True)

    def stallPortalPage(self, page: str, busyCount: int = 0):
        if self.portalPages[page]["page"].busy:
            if busyCount <= 20:
                JS.afterDelay(self.stallPortalPage, kwargs={"page": page, "busyCount": busyCount + 1}, delay=50)
                return None

            JS.log(f"Warning: Force finished page (Reason page is busy for to long) -> {page}")
            self.portalPages[page]["page"].busy = False

        self.loadPortalPage(page, didStall=True, rememberSubPage=True)

    def loadPortalPage(self, page: str = None, didDeload: bool = False, didPreload: bool = False, didStall: bool = False, rememberSubPage: bool = False):
        if self.loadingPage and not didDeload and not didPreload and not didStall:
            return None

        if not rememberSubPage:
            JS.cache("portalSubPage", "")

        self.loadingPage = True
        self.busy = True
        if not self.oldPage is None and not didDeload and not didPreload and not didStall:
            JS.aSync(self.deloadPortalPage, (page,))
            return None

        if not didPreload and not didStall:
            JS.cache("portalPage", page)

            JS.aSync(self.preloadPortalPage, (page,))
            return None

        if not didStall:
            JS.setTitle(f'HandyGold75 - {JS.cache("mainPage")} - {JS.cache("portalPage")}')
            HTML.setElementRaw("mainNav_title", f'HandyGold75 - {JS.cache("mainPage")} - {JS.cache("portalPage")}')
            JS.aSync(self.portalPages[page]["page"].main)

            JS.aSync(self.stallPortalPage, (page,))
            return None

        self.oldPage = page
        self.loadingPage = False
        self.busy = False
