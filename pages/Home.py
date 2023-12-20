from WebKit import CSS, HTML, JS


class home:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

    def onResize(self):
        pass

    def preload(self):
        self.busy = False

    def deload(self):
        self.busy = True
        JS.onResize("home", None)
        self.busy = False

    def layout(self):
        header = HTML.genElement("h1", nest="Page content for home.", style="headerMain")
        body = HTML.genElement("p", nest="Some extra filler text.", style="textBig")
        HTML.setElement("div", "mainPage", nest=header + body, id="homePage", align="center")

    def flyin(self):
        CSS.setStyle("homePage", "marginTop", f'-{CSS.getAttribute("homePage", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("homePage", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def main(self):
        self.layout()
        self.flyin()

        JS.onResize("home", self.onResize)
