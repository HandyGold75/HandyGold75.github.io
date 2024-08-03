from WebKit import HTML, Page


class home(Page):
    def __init__(self):
        super().__init__()

        self.onLayout = self.doOnLayout

    def doOnLayout(self):


        header = HTML.genElement("h1", nest="Home", style="headerMain")

        link = HTML.linkWrap("../", nest="../")
        body = HTML.genElement("p", nest=f"Moving towards GO WASM instead of Python WASM.\n\nFor reasons...\n\nNew site is available at {link}", style="textMedium")

        HTML.setElementRaw("subPage", header + body)
