from json import dumps, load, loads
from os import path as osPath

from WebKit import CSS, HTML, JS, WS, Page


class links(Page):
    def __init__(self):
        super().__init__()

        self.onResize = self.doOnResize
        self.onPreload = self.doOnPreload
        self.onLayout = lambda: self.doOnLayout(doEvents=False)

        if JS.cache("configLinks") is None:
            JS.cache("configLinks", dumps({"folded": {}}))

        with open(f"{osPath.split(__file__)[0]}/config.json", "r", encoding="UTF-8") as fileR:
            self.defaultLinks = load(fileR)["defaultLinks"]

        self.allLinks = dict(sorted(self.defaultLinks.items(), key=lambda x: x[1]["Index"]))
        self.foldedStates = loads(JS.cache("configLinks"))["folded"]

        self.columns = 0

    def doOnResize(self):
        oldColumns = self.columns

        self.columns = 5
        if JS.getWindow().innerWidth < 500:
            self.columns = 3
        elif JS.getWindow().innerWidth < 1000:
            self.columns = 4

        if self.columns != oldColumns:
            self.doOnLayout()

    def doOnPreload(self):
        if JS.getWindow().innerWidth < 500:
            self.columns = 3
        elif JS.getWindow().innerWidth < 1000:
            self.columns = 4
        self.columns = 5

        if not WS.loginState():
            return None

        def fetchTemplate():
            WS.onMsg('{"qr": {"Links":', finalize, oneTime=True)
            WS.send("qr read Links")

        def finalize():
            msgDict = WS.dict()

            headers = tuple(name for name, ktype in msgDict["qr"]["template"]["sheets"]["Links"])

            linkDict = {}
            for link in msgDict["qr"]["Links"]:
                img = msgDict["qr"]["Links"][link][headers.index("Img")][0]
                linkDict[img] = {}
                for i, header in enumerate(headers):
                    if header == "Img":
                        continue
                    linkDict[img][header] = msgDict["qr"]["Links"][link][i]

            self.allLinks = dict(sorted({**self.defaultLinks, **linkDict}.items(), key=lambda x: x[1]["Index"]))
            self.busy = False

        if "qr" in WS.dict()["access"]:
            WS.onMsg('{"qr": {"template":', fetchTemplate, oneTime=True)
            WS.send(f"qr template")

        return False

    def doOnLayout(self, doEvents: bool = True):
        sortedCats = {}
        for link in self.allLinks:
            if not self.allLinks[link]["cat"] in sortedCats:
                sortedCats[self.allLinks[link]["cat"]] = []
            sortedCats[self.allLinks[link]["cat"]].append(link)
            if not self.allLinks[link]["cat"] in self.foldedStates:
                self.foldedStates[self.allLinks[link]["cat"]] = False

        configLinks = loads(JS.cache("configLinks"))
        configLinks["folded"] = self.foldedStates
        JS.cache("configLinks", dumps(configLinks))

        catDivs = ""
        for cat in sortedCats:
            linksRows = ""

            linkDivs = ""
            for colIndex, link in enumerate(sortedCats[cat]):
                linkImg = HTML.genElement("img", style="width: 30%; user-select:none;", custom=f'src="docs/assets/Links/{link}" alt="{self.allLinks[link]["text"]}"')
                linkImg = HTML.linkWrap(self.allLinks[link]["url"], nest=linkImg)
                linkTxt = HTML.linkWrap(self.allLinks[link]["url"], nest=self.allLinks[link]["text"])
                linkTxt = HTML.genElement("p", nest=linkTxt, style="margin: 0px auto;")
                linkDivs += HTML.genElement("div", nest=linkImg + linkTxt, style=f"width: {100 / int(self.columns)}%; margin: 25px auto;")

                if (colIndex + 1) % int(self.columns) == 0:
                    linksRows += HTML.genElement("div", nest=linkDivs, align="center", style="flex")
                    linkDivs = ""

            if linkDivs != "":
                linksRows += HTML.genElement("div", nest=linkDivs, align="center", style="flex")

            catDivs += HTML.genElement("h1", id=f"linksPage_{cat}_Header", nest=cat, align="center", style="headerMain %% width: auto; margin: 10px auto -4px auto; font-size: 150%;")
            catSub = HTML.genElement("div", nest=linksRows, id=f"linksPage_{cat}_Sub", classes="linksPage_Subs")
            catDivs += HTML.genElement("div", nest=catSub, id=f"linksPage_{cat}", align="center", style="background %% min-height: 10px; margin: 0px auto 25px auto; overflow: hidden;")

        HTML.setElementRaw("subPage", catDivs)
        self.loadAnimation()

        def addEvents():
            self.busy = True
            for cat in sortedCats:
                JS.addEvent(f"linksPage_{cat}_Header", self.toggleCat, (cat,))
            self.busy = False

        if doEvents:
            JS.afterDelay(addEvents, delay=50)

    def loadAnimation(self):
        def doAnimations(index: int = 0):
            if not JS.cache("mainPage") == "Links":
                return None

            el = HTML.getElements("linksPage_Subs")[index]

            JS.aSync(setattr, (el.style, "transition", "margin-top 0.5s"))
            if self.foldedStates[el.id.split("_")[-2]]:
                if index < len(HTML.getElements("linksPage_Subs")) - 1:
                    JS.aSync(doAnimations, (index + 1,))
                return None
            JS.aSync(setattr, (el.style, "marginTop", "0px"))

            if index < len(HTML.getElements("linksPage_Subs")) - 1:
                JS.afterDelay(doAnimations, (index + 1,), delay=250)

        for els in HTML.getElements("linksPage_Subs"):
            setattr(els.style, "marginTop", f'-{CSS.getAttribute(els.id.replace("_Sub", ""), "offsetWidth")}px')

        JS.aSync(doAnimations)

    def toggleCat(self, cat):
        self.foldedStates[cat] = not self.foldedStates[cat]

        CSS.setStyle(f"linksPage_{cat}_Sub", "marginTop", "0px")

        if self.foldedStates[cat]:
            CSS.setStyle(f"linksPage_{cat}_Sub", "marginTop", f'-{CSS.getAttribute("linksPage_" + cat, "offsetHeight")}px')

        configLinks = loads(JS.cache("configLinks"))
        configLinks["folded"] = self.foldedStates
        JS.cache("configLinks", dumps(configLinks))
