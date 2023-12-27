from WebKit import CSS, JS, WS, PortalPage, Widget


class trees(PortalPage):
    def __init__(self):
        super().__init__()

        for key in ("knownFiles", "dates"):
            self.configKeys.append(key)
        self.evalMap = {"wrapOption": self.wrapOption}

        self.onSubPageLoad = self.generateTrees

        self.knownFiles = None
        self.dates = None

        self.wordWrap = False

    def generateTrees(self):
        data = WS.dict()[self.mainCom][JS.cache("portalSubPage")]
        if data == {}:
            mainValue = list(self.knownFiles[JS.cache("portalSubPage")])[-1]
            data[" "] = {}
            for value in self.knownFiles[JS.cache("portalSubPage")][mainValue]:
                data[" "][value] = self.knownFiles[JS.cache("portalSubPage")][mainValue][value]()

        tree = Widget.tree(name=JS.cache("portalSubPage"), elId="portalSubPage", dates=self.dates, wordWrap=self.wordWrap)
        tree.generate(data)

    def wrapOption(self):
        self.wordWrap = not self.wordWrap
        if self.wordWrap:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Inline")
        else:
            CSS.setAttribute("portalSubPage_nav_options_wordwrap", "innerHTML", "Word wrap")

        self._loadPortalSubPage()
