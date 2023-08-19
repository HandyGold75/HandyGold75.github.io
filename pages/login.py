from WebKit import HTML, CSS, JS, WS
from datetime import datetime, timedelta
from rsa import encrypt
from json import dumps, loads


class login:
    __all__ = ["main", "preload", "deload", "indexRedirectHook"]

    def __init__(self):
        self.busy = False
        self.requireLogin = False
        self.indexRedirect = None

        if JS.cache("configWS") is None:
            JS.cache("configWS", dumps({"server": "WSS://wss.HandyGold75.com:17500", "autoSignIn": False, "token": ""}))

        self.config = lambda: loads(JS.cache("configWS"))
        self.lastLogin = 0

    def onResize(self):
        if JS.getWindow().innerWidth < 500:
            CSS.setStyle("loginPage_login", "width", "100%")
            CSS.setStyle("loginPage_buttons", "width", "100%")
            for els in HTML.getElements("loginPage_inputHints"):
                setattr(els.style, "padding", "7px 0px")
            return None

        elif JS.getWindow().innerWidth < 1000:
            CSS.setStyle("loginPage_login", "width", "75%")
            CSS.setStyle("loginPage_buttons", "width", "75%")
            for els in HTML.getElements("loginPage_inputHints"):
                setattr(els.style, "padding", "4px 0px")
            return None

        CSS.setStyle("loginPage_login", "width", "75%")
        CSS.setStyle("loginPage_buttons", "width", "75%")
        for els in HTML.getElements("loginPage_inputHints"):
            setattr(els.style, "padding", "4px 0px")

    def preload(self):
        pass

    def deload(self):
        self.busy = True
        JS.onResize("login", None)
        self.busy = False

    def indexRedirectHook(self, function):
        self.indexRedirect = function

    def layout(self):
        def rememberSubmit():
            newConfig = self.config()
            newConfig["autoSignIn"] = not newConfig["autoSignIn"]
            WS.config = newConfig
            JS.cache("configWS", dumps(newConfig))

            if self.config()["autoSignIn"]:
                JS.clearEvents("loginPage_remember")
                CSS.onClick("loginPage_remember", "imgClick")
                JS.addEvent("loginPage_remember", rememberSubmit)
                CSS.setStyles("loginPage_remember", "imgHover")
                return None

            JS.clearEvents("loginPage_remember")
            CSS.onHoverClick("loginPage_remember", "imgHover", "imgClick")
            JS.addEvent("loginPage_remember", rememberSubmit)

        header = HTML.genElement("h1", nest="Login", style="headerMain")

        bodyTxt = HTML.genElement("p", nest="Server", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; margin: 3px auto; padding: 4px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_server", type="url", style="inputMedium %% width: 80%; height: 25px;", custom=f'placeholder="Server" pattern="(WSS||WS)://.+:[0-9]+" value="{self.config()["server"]}"')
        bodyDiv = HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")

        bodyTxt = HTML.genElement("p", nest="Username", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; margin: 3px auto; padding: 4px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_username", type="email", style="inputMedium %% width: 80%; height: 25px;", custom='placeholder="Username"')
        bodyDiv += HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")

        bodyTxt = HTML.genElement("p", nest="Password", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; margin: 3px auto; padding: 4px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_password", type="password", style="inputMedium %% width: 80%; height: 25px;", custom='placeholder="Password"')
        bodyDiv += HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")
        body = HTML.genElement("div", id="loginPage_login", nest=bodyDiv, style="width: 75%; margin: 20px auto; max-width: 750px; transition: width 0.25s;")

        footerImg = HTML.genElement("img", id="loginPage_rememberImg", style="width: 100%;", custom='src="docs/assets/Login/Pin.png" alt="Remember"')
        footerBtn = HTML.genElement("button", id="loginPage_remember", nest=footerImg, style="buttonImg")
        footerDiv = HTML.genElement("div", nest=footerBtn, id="loginPage_rememberDiv", align="right", style="width: 20%; max-width: 50px; margin: auto auto auto 5px;")

        footerBtn = HTML.genElement("button", nest="Login", id="loginPage_submit", type="button", style="buttonMedium %% width: 25%;")
        footerDiv += HTML.genElement("div", nest=footerBtn, align="right", style="width: 80%; margin: auto 5px auto auto;")
        footer = HTML.genElement("div", id="loginPage_buttons", nest=footerDiv, align="center", style="divNormal %% background %% flex %% width: 50%; max-width: 500px; margin: 10px auto; transition: width 0.25s;")

        HTML.setElement("div", "mainPage", nest=header + body + footer, id="loginPage", align="center")

        def addEvents():
            self.busy = True
            for id in ("loginPage_server", "loginPage_username", "loginPage_password"):
                JS.addEvent(id, self.loginSubmit, action="keyup", includeElement=True)
                CSS.onHoverFocus(id, "inputHover", "inputFocus")

            JS.addEvent("loginPage_submit", self.loginSubmit, includeElement=True)
            CSS.onHoverClick("loginPage_submit", "buttonHover", "buttonClick")

            if self.config()["autoSignIn"]:
                CSS.onClick("loginPage_remember", "imgClick")
                JS.addEvent("loginPage_remember", rememberSubmit)
                CSS.setStyles("loginPage_remember", "imgHover")
                return None

            JS.addEvent("loginPage_remember", rememberSubmit)
            CSS.onHoverClick("loginPage_remember", "imgHover", "imgClick")
            self.busy = False

        JS.afterDelay(addEvents, delay=50)

    def flyin(self):
        CSS.setStyle("loginPage", "marginTop", f'-{CSS.getAttribute("loginPage", "offsetHeight")}px')
        JS.aSync(CSS.setStyles, ("loginPage", (("transition", "margin-top 0.25s"), ("marginTop", "0px"))))

    def loginSubmit(self, element):
        def sendLogin():
            if WS.state() == 0 or WS.pub is None:
                JS.afterDelay(sendLogin, delay=50)
                return None
            if WS.state() > 1:
                JS.popup("alert", "Failed to connect to server")
                return None

            crypt = str(encrypt(CSS.getAttribute("loginPage_username", "value").encode() + "<SPLIT>".encode() + CSS.getAttribute("loginPage_password", "value").encode(), WS.pub))
            WS.send(f'<LOGIN> {crypt}')

        if WS.loginState() or (hasattr(element, "key") and element.key != "Enter") or ((datetime.now() - timedelta(seconds=1)).timestamp() < self.lastLogin):
            return None

        self.lastLogin = datetime.now().timestamp()
        server = CSS.getAttribute("loginPage_server", "value")
        if not server == self.config()["server"] or WS.ws == None or WS.state() > 1:
            newConfig = self.config()
            newConfig["server"] = server
            WS.config = newConfig
            JS.cache("configWS", dumps(newConfig))

            try:
                self.setupConnection()
            except ValueError as err:
                JS.popup("alert", str(err))
                return None

        JS.aSync(sendLogin)

    def setupConnection(self):
        def loginSucces():
            def loadingTxt():
                el = HTML.getElement("loginPage_loadingTxt")
                if el is None:
                    return None

                if el.innerHTML.endswith(". . . "):
                    el.innerHTML = el.innerHTML.replace(". . . ", "")

                el.innerHTML += ". "
                JS.afterDelay(loadingTxt, delay=500)

            WS.onMsg("{\"access\":", self.indexRedirect, oneTime=True)
            WS.send("access")

            JS.clearEvents("mainFooter_Login")
            HTML.setElementRaw("mainFooter_Login", "Logout")
            JS.addEvent("mainFooter_Login", WS.logout)
            CSS.onHoverClick("mainFooter_Login", "buttonHover %% background: #66F;", "buttonClick %% background: #66F;")

            if JS.cache("mainPage") != "Login":
                return None

            content = HTML.genElement("h1", nest="Login", style="headerMain")
            content += HTML.genElement("p", nest="You are logged in.", style="textBig")
            content += HTML.genElement("p", nest="Loading access", id="loginPage_loadingTxt", style="textBig")

            HTML.setElement("div", "loginPage", nest=content, id="loginPage_summary", align="center")
            JS.aSync(loadingTxt)

        def loginHandler(msg):
            if msg == "loginTokenNotFound":
                HTML.enableElement("loginPage_server")
                HTML.enableElement("loginPage_username")
                HTML.enableElement("loginPage_password")
            elif msg == "loginTokenWasSend":
                HTML.disableElement("loginPage_server")
                HTML.disableElement("loginPage_username")
                HTML.disableElement("loginPage_password")
            elif msg in ["loginTokenSucces", "loginSucces"]:
                loginSucces()
            elif msg == "loginTokenFail":
                HTML.enableElement("loginPage_server")
                HTML.enableElement("loginPage_username")
                HTML.enableElement("loginPage_password")
            elif msg == "loginFail":
                JS.popup("alert", "Log in failed!")

        server = self.config()["server"]
        if server == "" or not "://" in server or not server.count(":") == 2:
            raise ValueError(f'Invalid server: {server}\nFormat: [WS, WSS]://[Server]:[1-65535]')

        proto = server.split("://")[0]
        ip = server.split("://")[-1].split(":")[0]
        port = int(server.split("://")[-1].split(":")[-1])
        if not proto.lower() in ["ws", "wss"] or port < 1 or port > 65535:
            raise ValueError(f'Invalid protocol or port: {proto}, {port}\nFormat: [WS, WSS]://[Server]:[1-65535]')

        WS.start(proto, ip, str(port), loginHandler)

    def main(self, args=None):
        if WS.loginState():
            header = HTML.genElement("h1", nest="Login", style="headerMain")
            body = HTML.genElement("p", nest="You are logged in.", style="textBig")
            HTML.setElement("div", "mainPage", nest=header + body, align="center")
            return None

        self.layout()
        self.flyin()

        if self.config()["autoSignIn"] and WS.state() != 1:
            self.setupConnection()

        JS.onResize("login", self.onResize)
