from WebKit.init import HTML, CSS, JS, WS
from json import dumps, loads, load
from os import path as osPath


class links:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        if JS.cache("configLinks") is None:
            JS.cache("configLinks", dumps({"folded": {}}))

        with open(f'{osPath.split(__file__)[0]}/config.json', "r", encoding="UTF-8") as fileR:
            self.defaultLinks = load(fileR)["defaultLinks"]

        self.allLinks = dict(sorted(self.defaultLinks.items(), key=lambda x: x[1]['Index']))
        self.foldedStates = loads(JS.cache("configLinks"))["folded"]

        self.columns = 5
        if JS.getWindow().innerWidth < 500:
            self.columns = 3
        elif JS.getWindow().innerWidth < 1000:
            self.columns = 4

    def onResize(self):
        oldColumns = self.columns
        if JS.getWindow().innerWidth < 500:
            self.columns = 3
        elif JS.getWindow().innerWidth < 1000:
            self.columns = 4
        else:
            self.columns = 5

        if self.columns != oldColumns:
            self.layout()

            for el in HTML.getElements("linksPage_Subs"):
                JS.aSync(setattr, (el.style, "transition", "margin-top 0.5s"))
                if self.foldedStates[el.id.split("_")[-2]]:
                    setattr(el.style, "marginTop", f'-{CSS.getAttribute(el.id.replace("_Sub", ""), "offsetWidth")}px')
                else:
                    setattr(el.style, "marginTop", "0px")

    def preload(self):
        self.busy = True
        if JS.getWindow().innerWidth < 500:
            self.columns = 3
        elif JS.getWindow().innerWidth < 1000:
            self.columns = 4
        self.columns = 5

        if not WS.loginState():
            return None

        def finalize(self):
            msgDict = WS.dict()
            if "qr" in msgDict:
                if " " in msgDict["qr"]["/Links.json"]:
                    msgDict["qr"]["/Links.json"].pop(" ")

                self.allLinks = dict(sorted({**self.defaultLinks, **msgDict["qr"]["/Links.json"]}.items(), key=lambda x: x[1]['Index']))
            self.busy = False

        if "qr" in WS.dict()["access"]:
            WS.onMsg("{\"qr\": {\"/Links.json\":", finalize, (self, ), oneTime=True)
            WS.send("qr read /Links.json")

    def deload(self):
        self.busy = True
        JS.onResize("links", None)
        self.busy = False

    def layout(self):
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
            linkDivs = ""
            linksRows = ""

            for colIndex, link in enumerate(sortedCats[cat]):
                linkImg = HTML.genElement("img", style="width: 30%; user-select:none;", custom=f'src="docs/assets/Links/{link}" alt="{self.allLinks[link]["text"]}"')
                linkImg = HTML.linkWrap(self.allLinks[link]["url"], nest=linkImg)
                linkTxt = HTML.linkWrap(self.allLinks[link]["url"], nest=self.allLinks[link]["text"])
                linkTxt = HTML.genElement("p", nest=linkTxt, style="margin: 0px auto;")
                linkDivs += HTML.genElement("div", nest=linkImg + linkTxt, style=f'width: {100 / int(self.columns)}%; margin: 25px auto;')

                if (colIndex + 1) % int(self.columns) == 0:
                    linksRows += HTML.genElement("div", nest=linkDivs, align="center", style="flex")
                    linkDivs = ""

            if linkDivs != "":
                linksRows += HTML.genElement("div", nest=linkDivs, align="center", style="flex")

            catDivs += HTML.genElement("h1", id=f'linksPage_{cat}_Header', nest=cat, align="center", style="headerMain %% width: auto; margin: 10px auto -4px auto; font-size: 150%;")
            catSub = HTML.genElement("div", nest=linksRows, id=f'linksPage_{cat}_Sub', classes="linksPage_Subs")
            catDivs += HTML.genElement("div", nest=catSub, id=f'linksPage_{cat}', align="center", style="background %% min-height: 10px; margin: 0px auto 25px auto; overflow: hidden;")

        HTML.setElement("div", "mainPage", nest=catDivs, id="linksPage", align="center")

        def addEvents():
            self.busy = True
            for cat in sortedCats:
                JS.addEvent(f'linksPage_{cat}_Header', self.toggleCat, (cat, ))
            self.busy = False

        JS.afterDelay(addEvents, delay=50)

    def flyin(self):
        CSS.setStyle("linksPage", "marginTop", f'-{CSS.getAttribute("linksPage", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("linksPage", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def loadAnimation(self):
        def doAnimations(index: int = 0):
            if not JS.cache("mainPage") == "Links":
                return None

            el = HTML.getElements("linksPage_Subs")[index]

            JS.aSync(setattr, (el.style, "transition", "margin-top 0.5s"))
            if self.foldedStates[el.id.split("_")[-2]]:
                if index < len(HTML.getElements("linksPage_Subs")) - 1:
                    JS.aSync(doAnimations, (index + 1, ))
                return None
            JS.aSync(setattr, (el.style, "marginTop", "0px"))

            if index < len(HTML.getElements("linksPage_Subs")) - 1:
                JS.afterDelay(doAnimations, (index + 1, ), delay=250)

        for els in HTML.getElements("linksPage_Subs"):
            setattr(els.style, "marginTop", f'-{CSS.getAttribute(els.id.replace("_Sub", ""), "offsetWidth")}px')

        JS.aSync(doAnimations)

    def toggleCat(self, cat):
        self.foldedStates[cat] = not self.foldedStates[cat]

        CSS.setStyle(f'linksPage_{cat}_Sub', "marginTop", "0px")

        if self.foldedStates[cat]:
            CSS.setStyle(f'linksPage_{cat}_Sub', "marginTop", f'-{CSS.getAttribute("linksPage_" + cat, "offsetHeight")}px')

        configLinks = loads(JS.cache("configLinks"))
        configLinks["folded"] = self.foldedStates
        JS.cache("configLinks", dumps(configLinks))

    def main(self):
        self.layout()
        self.flyin()
        self.loadAnimation()

        JS.onResize("links", self.onResize)