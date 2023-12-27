from json import loads

from pages import console, contact, home, links, login, portal
from WebKit import CSS, HTML, JS, WS, Buttons


class mainPage:
    def __init__(self):
        for item in ["mainPage"]:
            if JS.cache(item) is None:
                JS.cache(item, "")

        if JS.cache("mainPage") == "":
            JS.cache("mainPage", "Home")

        self.pages = {
            "Home": {
                "hidden": False,
                "page": home(),
            },
            "Links": {
                "hidden": False,
                "page": links(),
            },
            "Portal": {
                "hidden": False,
                "page": portal(),
            },
            "Console": {
                "hidden": False,
                "page": console(),
            },
            "Contact": {
                "hidden": False,
                "page": contact(),
            },
            "Login": {
                "hidden": True,
                "page": login(),
            },
        }

        self.oldPage = None
        self.loadingPage = False
        self.busyCount = 0

    def onResize(self):
        if JS.getWindow().innerWidth < 500:
            if not CSS.getAttribute("mainNav_showHide_img", "src").endswith("docs/assets/Show-V.svg"):
                # CSS.setStyle("mainNav_showHideDiv", "maxWidth", "35px")
                CSS.setStyle("mainNav_logo", "maxWidth", "70px")
            return None

        elif JS.getWindow().innerWidth < 1000:
            if not CSS.getAttribute("mainNav_showHide_img", "src").endswith("docs/assets/Show-V.svg"):
                # CSS.setStyle("mainNav_showHideDiv", "maxWidth", "42.5px")
                CSS.setStyle("mainNav_logo", "maxWidth", "85px")
            return None

        if not CSS.getAttribute("mainNav_showHide_img", "src").endswith("docs/assets/Show-V.svg"):
            # CSS.setStyle("mainNav_showHideDiv", "maxWidth", "50px")
            CSS.setStyle("mainNav_logo", "maxWidth", "101px")

    def layout(self):
        def showHideNav():
            el = HTML.getElement("mainNav_showHide_img")

            if el.src.endswith("docs/assets/Hide-V.svg"):
                el.src = "docs/assets/Show-V.svg"
                el.alt = "Unfold"

                CSS.setStyle("mainNav", "padding", "0px")
                CSS.setStyle("mainNav_middle", "marginTop", f'-{CSS.getAttribute("mainNav", "offsetHeight")}px')
                CSS.setStyle("mainNav_logo", "maxWidth", "40px")
                # CSS.setStyle("mainNav_showHide", "maxWidth", "30px")
                self.pages[JS.cache("mainPage")]["page"].onResize()
                return None

            el.src = "docs/assets/Hide-V.svg"
            el.alt = "Fold"

            CSS.setStyle("mainNav", "padding", "5px")
            CSS.setStyle("mainNav_middle", "marginTop", "0px")

            self.onResize()
            self.pages[JS.cache("mainPage")]["page"].onResize()

        JS.setTitle("HandyGold75")

        navButtons = ""
        for page in self.pages:
            if self.pages[page]["hidden"]:
                continue
            navButtons += Buttons.large(f"subPageButton_{page}", page, onClick=self.loadPage, args=(page,))

        nav = HTML.genElement("img", id="mainNav_logo", align="left", style="width: 20%; max-width: 101px; margin: auto auto auto 5px; user-select: none; transition: max-width 0.25s;", custom='src="docs/assets/;D.png"')

        navTxt = HTML.genElement("h1", nest=f'HandyGold75 - {JS.cache("mainPage")}', id="mainNav_title", align="center", style="headerBig %% width: 80%;")
        navDiv = HTML.genElement("div", nest=navButtons, id="mainNav_buttons", align="center", style="padding: 4px; margin: 0px auto;")
        nav += HTML.genElement("div", nest=navTxt + navDiv, id="mainNav_middle", align="center", style="width: 80%; transition: margin-top 0.5s;")

        # navImg = HTML.genElement("img", id="mainNav_showHideImg", style="width: 100%;", custom='src="docs/assets/Hide-V.svg" alt="Fold"')
        # navBtn = HTML.genElement("button", id="mainNav_showHide", nest=navImg, style="buttonImg")
        # nav += HTML.genElement("div", nest=navBtn, id="mainNav_showHideDiv", align="right", style="width: 20%; max-width: 50px; margin: auto 5px auto auto; transition: max-width 0.25s;")

        nav += Buttons.imgSmall("mainNav_showHide", "docs/assets/Hide-V.svg", alt="Fold", buttonStyle="margin-top: auto; margin-bottom: auto;", buttonKwargs={"align": "right"}, onClick=showHideNav)

        footerTxt = HTML.genElement("p", nest="HandyGold75 - 2022 / 2023", style="headerVerySmall %% color: #111; text-align: left; padding: 3px; margin: 0px auto;")
        footer = HTML.genElement("div", nest=footerTxt, id="mainFooter_note", style="width: 50%; margin: auto;")

        footerBtns = Buttons.small("mainFooter_Login", "Login", onClick=self.loadPage, args=("Login",), theme="light")
        footerBtns += Buttons.small("mainFooter_toTop", "Back to top", onClick=getattr(HTML.getBody(), "scrollIntoView"), theme="light")
        footerBtns += Buttons.small("mainFooter_ClearCache", "Clear cache", onClick=JS.clearCache, theme="light")

        footer += HTML.genElement("div", nest=footerBtns, id="mainFooter_buttons", align="right", style="width: 50%; margin: auto;")

        main = HTML.genElement("header", nest=nav, id="mainNav", flex=True, style="divNormal %% padding: 5px; transition: padding 0.25s;")
        main += HTML.genElement("div", id="mainPage", style="divNormal %% transition: max-height 0.25s;")
        main += HTML.genElement("footer", nest=footer, id="mainFooter", flex=True, style="divAlt %% padding: min(1vw, 10px) 10px;")
        main += HTML.genElement("div", id="mainPopup", style="z-index: 10000; display: none; position: fixed; width: 100%; height: 100%; top: 0px; left: 0px; background: rgba(0, 0, 0, 0); transition: background 0.25s;")

        HTML.getBody().innerHTML = main

        Buttons.applyEvents()

        # def addEvents():
        #     JS.addEvent("mainNav_showHide", showHideNav)
        #     CSS.onHoverClick("mainNav_showHide", "imgHover", "imgClick")

        #     JS.onResize("mainPage", self.onResize)

        JS.afterDelay(JS.onResize, args=("mainPage", self.onResize), delay=50)

    def deloadPage(self, page: str = None, firstRun: bool = True):
        if firstRun:
            self.busyCount = 0
            JS.aSync(self.pages[self.oldPage]["page"].deload)
            CSS.setStyle("mainPage", "maxHeight", f'{CSS.getAttribute("mainPage", "offsetHeight")}px')
            JS.aSync(CSS.setStyle, ("mainPage", "maxHeight", "0px"))
            JS.afterDelay(self.deloadPage, kwargs={"page": page, "firstRun": False}, delay=250)
            return None

        if self.pages[self.oldPage]["page"].busy:
            self.busyCount += 1
            if self.busyCount <= 15:
                JS.afterDelay(self.deloadPage, kwargs={"page": page, "firstRun": False}, delay=50)
                return None

            JS.log(f"Warning: Force stopped page (Reason page is busy for to long) -> {self.oldPage}")
            self.pages[self.oldPage]["page"].busy = False

        CSS.setStyle("mainPage", "maxHeight", "")
        if not page is None:
            self.oldPage = None
            self.loadPage(page, deloaded=True, rememberPortalPage=True)

    def stallPage(self, page: str, firstRun: bool = True):
        if firstRun:
            self.busyCount = 0

        if self.pages[page]["page"].busy:
            self.busyCount += 1
            if self.busyCount <= 100:
                JS.afterDelay(self.stallPage, kwargs={"page": page, "firstRun": False}, delay=50)
                return None

            JS.log(f"Warning: Force loaded page (Reason page is busy for to long) -> {page}")
            self.pages[page]["page"].busy = False

        self.loadPage(page, didStall=True, rememberPortalPage=True)

    def spoofPage(self, page):
        redirectPage = page
        if self.pages[page]["page"].requireLogin and not WS.loginState():
            page = "Login"
        else:
            configWS = loads(JS.cache("configWS"))
            doSpoof = True
            if not configWS["autoSignIn"] or WS.loginState():
                doSpoof = False
            elif configWS["server"] == "" or configWS["token"] == "":
                doSpoof = False
            elif not "://" in configWS["server"] or configWS["server"].count(":") != 2:
                doSpoof = False
            elif WS.reconnectTries >= WS.maxReconnectTries:
                doSpoof = False

            if doSpoof:
                page = "Login"

        if hasattr(self.pages[page]["page"], "indexRedirectHook"):
            self.pages[page]["page"].indexRedirectHook(lambda: self.loadPage(redirectPage, rememberPortalPage=True))

        return page

    def loadPage(self, page: str = None, deloaded: bool = False, didStall: bool = False, rememberPortalPage: bool = False):
        if self.loadingPage and not deloaded and not didStall:
            return None

        if not rememberPortalPage:
            JS.cache("portalPage", "")
            JS.cache("portalSubPage", "")

        self.loadingPage = True
        if not self.oldPage is None and not deloaded:
            self.deloadPage(page)
            return None

        if not didStall:
            page = self.spoofPage(page)
            JS.cache("mainPage", page)

            HTML.clrElement("mainPage")
            self.pages[page]["page"].preload()
            if self.pages[page]["page"].busy:
                self.stallPage(page)
                return None

        JS.setTitle(f'HandyGold75 - {JS.cache("mainPage")}')
        HTML.setElementRaw("mainNav_title", f'HandyGold75 - {JS.cache("mainPage")}')
        JS.aSync(self.pages[page]["page"].main)

        self.oldPage = page
        self.loadingPage = False

    def onLogout(self):
        JS.clearEvents("mainFooter_Login")
        HTML.setElementRaw("mainFooter_Login", "Login")
        JS.addEvent("mainFooter_Login", self.loadPage, kwargs={"page": "Login"})
        CSS.onHoverClick("mainFooter_Login", "buttonHover %% background: #66F;", "buttonClick %% background: #66F;")


if __name__ == "__main__":
    page = mainPage()
    page.layout()
    page.loadPage(JS.cache("mainPage"), rememberPortalPage=True)

    WS.indexLogoutHook(page.onLogout)
