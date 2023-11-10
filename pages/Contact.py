from json import load
from os import path as osPath

from WebKit.init import CSS, HTML, JS, WS


class contact:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False

        with open(f"{osPath.split(__file__)[0]}/config.json", "r", encoding="UTF-8") as fileR:
            self.defaultContacts = load(fileR)["defaultContacts"]

        self.allContacts = dict(sorted(self.defaultContacts.items(), key=lambda x: x[1]["Index"]))

    def onResize(self):
        if JS.getWindow().innerWidth < 500:
            for els in HTML.getElements("contactPage_Images"):
                setattr(els.style, "width", "20%")
            for els in HTML.getElements("contactPage_Links"):
                setattr(els.style, "width", "80%")
            return None

        elif JS.getWindow().innerWidth < 1000:
            for els in HTML.getElements("contactPage_Images"):
                setattr(els.style, "width", "40%")
            for els in HTML.getElements("contactPage_Links"):
                setattr(els.style, "width", "60%")
            return None

        for els in HTML.getElements("contactPage_Images"):
            setattr(els.style, "width", "50%")
        for els in HTML.getElements("contactPage_Links"):
            setattr(els.style, "width", "50%")

    def preload(self):
        self.busy = True
        if not WS.loginState():
            self.busy = False
            return None

        def fetchTemplate():
            WS.onMsg('{"qr": {"Contact":', finalize, (self,), oneTime=True)
            WS.send("qr read Contact")

        def finalize(self):
            msgDict = WS.dict()
            headers = []
            types = []
            for name, ktype in msgDict["qr"]["template"]["sheets"]["Contact"]:
                headers.append(name)
                types.append(type(ktype))

            linkDict = {}
            for link in msgDict["qr"]["Contact"]:
                img = msgDict["qr"]["Contact"][link][headers.index("Img")][0]
                linkDict[img] = {}
                for i, header in enumerate(headers):
                    if header == "Img":
                        continue
                    linkDict[img][header] = msgDict["qr"]["Contact"][link][i]

            self.allContacts = dict(sorted({**self.defaultContacts, **msgDict["qr"]["Contact"]}.items(), key=lambda x: x[1]["Index"]))
            self.busy = False

        if "qr" in WS.dict()["access"]:
            WS.onMsg('{"qr": {"template":', fetchTemplate, oneTime=True)
            WS.send(f"qr template")

    def deload(self):
        self.busy = True
        JS.onResize("contact", None)
        self.busy = False

    def layout(self):
        header = HTML.genElement("h1", nest="Contact details", style="headerMain")

        body = ""
        for i, contact in enumerate(self.allContacts):
            bodyImg = HTML.genElement("img", style="width: 50%; min-width: 35px; max-width: 128px; user-select:none;", custom=f'src="docs/assets/Contact/{contact}" alt="{contact}"')
            bodyImg = HTML.linkWrap(self.allContacts[contact]["url"], nest=bodyImg, classes="contactPage_Images", style="width: 50%; margin: 15px 0px 10px 15px;")
            bodyTxt = HTML.linkWrap(self.allContacts[contact]["url"], nest=self.allContacts[contact]["text"], classes="contactPage_Links", style="width: 50%; margin: auto auto auto 0px; text-align: left; font-size: 150%;")
            body += HTML.genElement("div", nest=bodyImg + bodyTxt, classes="contactPage_Divs", id=f"contactPage_Div_{i}", align="center", style="flex %% background %% width: 85%; margin: 5px auto;")

        HTML.setElement("div", "mainPage", nest=header + body, id="contactPage", align="center")

    def flyin(self):
        CSS.setStyle("contactPage", "marginTop", f'-{CSS.getAttribute("contactPage", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("contactPage", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def loadAnimation(self):
        def doAnimations(index: int = 0):
            if not JS.cache("mainPage") == "Contact":
                return None

            el = HTML.getElements("contactPage_Divs")[index]

            if index % 2 == 0:
                JS.aSync(setattr, (el.style, "transition", "margin-left 0.5s"))
                JS.aSync(setattr, (el.style, "marginLeft", "5px"))
            else:
                JS.aSync(setattr, (el.style, "transition", "margin-right 0.5s"))
                JS.aSync(setattr, (el.style, "marginRight", "5px"))

            if index < len(HTML.getElements("contactPage_Divs")) - 1:
                JS.afterDelay(doAnimations, (index + 1,), delay=250)

        for i, els in enumerate(HTML.getElements("contactPage_Divs")):
            if i % 2 == 0:
                setattr(els.style, "marginLeft", f'-{CSS.getAttribute("contactPage", "offsetWidth")}px')
            else:
                setattr(els.style, "marginRight", f'-{CSS.getAttribute("contactPage", "offsetWidth")}px')

        JS.aSync(doAnimations)

    def main(self):
        self.layout()
        self.flyin()
        self.loadAnimation()

        JS.onResize("contact", self.onResize)
