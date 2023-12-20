from datetime import datetime, timedelta
from json import JSONDecodeError, dumps, loads

from WebKit import CSS, HTML, JS, WS


class console:
    __all__ = ["main", "preload", "deload"]

    def __init__(self):
        self.busy = False
        self.requireLogin = True
        self.lastCommand = 0
        self.commandHistory = []
        self.commandHistoryIndex = 0
        self.receivedCommandCount = 0

    def onResize(self):
        height = JS.getWindow().innerHeight - 335 if HTML.getElement("mainNav_showHideImg").src.endswith("docs/assets/Hide-V.svg") else JS.getWindow().innerHeight - 250
        CSS.setStyle("consolePage_output", "height", f"{height - 40}px")
        CSS.setStyle("consolePage_body", "height", f"{height}px")

        CSS.setStyle("consolePage_output", "width", f'{CSS.getAttribute("consolePage_body", "offsetWidth") - 28}px')
        CSS.setStyle("consolePage_input", "width", f'{CSS.getAttribute("consolePage_body", "offsetWidth") - 42}px')
        CSS.setStyle("consolePage_overlay", "width", f'{CSS.getAttribute("consolePage_body", "offsetWidth") - 28}px')

        if JS.getWindow().innerWidth < 500:
            CSS.setStyle("consolePage_input", "fontSize", "150%")
            CSS.setStyle("consolePage_overlay", "fontSize", "150%")
            return None

        elif JS.getWindow().innerWidth < 1000:
            CSS.setStyle("consolePage_input", "fontSize", "125%")
            CSS.setStyle("consolePage_overlay", "fontSize", "125%")
            return None

        CSS.setStyle("consolePage_input", "fontSize", "100%")
        CSS.setStyle("consolePage_overlay", "fontSize", "100%")

    def preload(self):
        self.busy = False

    def deload(self):
        self.busy = True
        WS.raiseOnMsg = None
        JS.onResize("console", None)
        self.busy = False

    def layout(self):
        header = HTML.genElement("h1", nest="Console", style="headerMain")

        height = JS.getWindow().innerHeight - 335 if HTML.getElement("mainNav_showHideImg").src.endswith("docs/assets/Hide-V.svg") else JS.getWindow().innerHeight - 250

        bodyDiv = HTML.genElement("div", id="consolePage_output", align="left", style=f"width: 0px; height: {height - 42}px; min-height: 209px; padding: 5px 10px; overflow: scroll; transition: width 0.5s; height 0.25s;")
        bodyInp = HTML.genElement("input", id="consolePage_input", type="text", style=f"inputDark %% width: 0px; height: 20px; padding: 5px 10px 5px 24px; margin: 0px; color: #F7E163; transition: width 0.5s;", custom="autofocus")
        bodyOverlay = HTML.genElement("p", ">", id="consolePage_overlay", align="left", style="width: 0px; height: 20px; margin: -27.5px 0px 0px 0px; padding: 0px 10px; font-weight: bold; color: #F7E163; text-align: left; transition: width 0.5s;")
        body = HTML.genElement("div", nest=bodyDiv + bodyInp + bodyOverlay, id="consolePage_body", style=f"divDark %% height: {height}px; min-height: 250px; margin: 15px 5px 5px 5px; padding: 0px; transition: height 0.25s;")
        HTML.setElement("div", "mainPage", nest=header + body, id="consolePage", align="center")

        def addEvents():
            JS.addEvent("consolePage_input", self.consoleSubmit, action="keyup", includeElement=True)
            WS.raiseOnMsg = self.consoleReceive

        JS.afterDelay(addEvents, delay=50)
        JS.afterDelay(CSS.setStyle, args=("consolePage_output", "transition", "height 0.25s"), delay=500)
        JS.afterDelay(CSS.setStyle, args=("consolePage_input", "transition", ""), delay=500)
        JS.afterDelay(CSS.setStyle, args=("consolePage_overlay", "transition", ""), delay=500)

    def consoleReceive(self, msg):
        if msg.startswith("{") and msg.endswith("}"):
            try:
                msg = dumps(loads(msg), indent=4).replace("    ", " - - ")
            except JSONDecodeError:
                pass

        self.receivedCommandCount += 1
        HTML.addElement("p", "consolePage_output", nest=f"{self.receivedCommandCount} > {str(msg)}", style="width: 100%; margin: 0px; color: #F7E163; text-align: left;", id=f"consolePage_output_{self.receivedCommandCount}")
        CSS.getAttribute(f"consolePage_output_{self.receivedCommandCount}", "scrollIntoView")()
        CSS.setAttribute("consolePage_input", "value", "")

    def consoleSubmit(self, element):
        if len(self.commandHistory) > 0:
            if hasattr(element, "key") and element.key == "ArrowUp":
                self.commandHistoryIndex += 1
                if self.commandHistoryIndex > len(self.commandHistory):
                    self.commandHistoryIndex = 1
                CSS.setAttribute("consolePage_input", "value", self.commandHistory[-self.commandHistoryIndex])

            if hasattr(element, "key") and element.key == "ArrowDown":
                self.commandHistoryIndex -= 1
                if self.commandHistoryIndex < 1:
                    self.commandHistoryIndex = len(self.commandHistory)
                CSS.setAttribute("consolePage_input", "value", self.commandHistory[-self.commandHistoryIndex])

        if not WS.loginState() or (hasattr(element, "key") and element.key != "Enter") or ((datetime.now() - timedelta(seconds=1)).timestamp() < self.lastCommand):
            return None

        self.lastCommand = datetime.now().timestamp()
        self.commandHistoryIndex = 0
        command = CSS.getAttribute("consolePage_input", "value")
        self.commandHistory.append(command)
        WS.send(command)

    def flyin(self):
        CSS.setStyle("consolePage", "marginTop", f'-{CSS.getAttribute("consolePage", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("consolePage", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def main(self):
        if not WS.loginState():
            return None

        self.layout()
        self.flyin()

        JS.onResize("console", self.onResize)
