from WebKit import HTML, Page


class home(Page):
    def __init__(self):
        super().__init__()

        self.onLayout = self.doOnLayout

    def doOnLayout(self):
        header = HTML.genElement("h1", nest="Page content for home.", style="headerMain")

        body = ""
        for txt in ("filler", "extra", "more"):
            body += HTML.genElement("p", nest=f"Some {txt} text.", style="textBig")

        HTML.setElementRaw("subPage", header + body)
