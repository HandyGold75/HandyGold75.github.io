from datetime import datetime, timedelta
from json import dumps, loads

from rsa import encrypt

from WebKit import CSS, HTML, JS, WS, Buttons, Page, Widget


class login(Page):
    def __init__(self):
        super().__init__()

        self.onLayout = self.doOnLayout

        self.indexRedirect = None

        if JS.cache("configWS") is None:
            JS.cache("configWS", dumps({"server": "WSS://py.HandyGold75.com", "autoSignIn": False, "token": ""}))

        self.config = lambda: loads(JS.cache("configWS"))
        self.lastLogin = 0

    def doOnLayout(self):
        def rememberSubmit():
            newConfig = self.config()
            newConfig["autoSignIn"] = not newConfig["autoSignIn"]
            WS.config = newConfig
            JS.cache("configWS", dumps(newConfig))

            if self.config()["autoSignIn"]:
                CSS.setAttribute("loginPage_remember", "className", "imgBtn imgBtnSmall active")
                return None

            CSS.setAttribute("loginPage_remember", "className", "imgBtn imgBtnSmall")

        if WS.loginState():
            header = HTML.genElement("h1", nest="Login", style="headerMain")
            body = HTML.genElement("p", nest="You are logged in.", style="textBig")
            HTML.setElement("div", "subPage", nest=header + body, align="center")
            return None

        header = HTML.genElement("h1", nest="Login", style="headerMain")

        bodyTxt = HTML.genElement("p", nest="Server", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; height: 25px; line-height: 25px; margin: 3px auto; padding: 1px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_server", type="url", style="inputMedium %% width: 80%; height: 25px;", custom=f'placeholder="Server" pattern="(WSS||WS)://.+:[0-9]+" value="{self.config()["server"]}"')
        bodyDiv = HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")

        bodyTxt = HTML.genElement("p", nest="Username", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; height: 25px; line-height: 25px; margin: 3px auto; padding: 1px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_username", type="email", style="inputMedium %% width: 80%; height: 25px;", custom='placeholder="Username"')
        bodyDiv += HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")

        bodyTxt = HTML.genElement("p", nest="Password", classes="loginPage_inputHints", style="headerSmall %% background %% width: 20%; height: 25px; line-height: 25px; margin: 3px auto; padding: 1px 0px; border: 2px solid #191919; border-radius: 6px;")
        bodyInp = HTML.genElement("input", id="loginPage_password", type="password", style="inputMedium %% width: 80%; height: 25px;", custom='placeholder="Password"')
        bodyDiv += HTML.genElement("div", nest=bodyTxt + bodyInp, align="center", style="flex")
        body = HTML.genElement("div", id="loginPage_login", nest=bodyDiv, style="width: max(75%, 247px); margin: 20px auto; max-width: 750px; transition: width 0.25s;")

        footerBtns = Buttons.imgSmall("loginPage_remember", "./docs/assets/Login/Pin.svg", active=self.config()["autoSignIn"], buttonStyle="margin-top: auto; margin-bottom: auto;", alt="Remember", onClick=rememberSubmit)
        footerBtns += HTML.genElement("div", style="height: 50px; margin: auto;")
        footerBtns += Buttons.medium("loginPage_submit", "Login", buttonStyle="margin-top: auto; margin-bottom: auto;", onClick=self.loginSubmit)

        footer = HTML.genElement("div", id="loginPage_buttons", nest=footerBtns, align="center", style="divNormal %% background %% flex %% width: max(75%, 247px); max-width: 500px; margin: 10px auto; transition: width 0.25s;")

        HTML.setElement("div", "subPage", nest=header + body + footer, id="loginPage", align="center")

        Buttons.applyEvents()

        def addEvents():
            self.busy = True
            for id in ("loginPage_server", "loginPage_username", "loginPage_password"):
                JS.addEvent(id, self.loginSubmit, action="keyup", includeElement=True)
                CSS.onHoverFocus(id, "inputHover", "inputFocus")

            self.busy = False

        JS.afterDelay(addEvents, delay=50)

        if self.config()["autoSignIn"] and WS.state() != 1:
            self.setupConnection()

    def indexRedirectHook(self, function):
        self.indexRedirect = function

    def loginSubmit(self, element=None):
        def sendLogin():
            if WS.state() == 0 or WS.pub is None:
                JS.afterDelay(sendLogin, delay=50)
                return None
            if WS.state() > 1:
                Widget.popup("warning", "Server\nFailed to connect to server")
                return None

            crypt = str(encrypt(CSS.getAttribute("loginPage_username", "value").encode() + "<SPLIT>".encode() + CSS.getAttribute("loginPage_password", "value").encode(), WS.pub))
            WS.send(f"<LOGIN> {crypt}")

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
                Widget.popup("warning", f"Server\n{err}")
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

            WS.onMsg('{"access":', self.indexRedirect, oneTime=True)
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
                Widget.popup("warning", "Server\nLog in failed!")

        server = self.config()["server"]
        if server == "" or not "://" in server or server.count(":") == 0 or server.count(":") > 2:
            raise ValueError(f"Invalid server: {server}\nFormat: [WS, WSS]://[Server]:[1-65535]")

        proto = server.split("://")[0]
        ip = server.split("://")[-1].split(":")[0]
        if server.count(":") == 1:
            port = 443
        else:
            port = int(server.split("://")[-1].split(":")[-1])
        if not proto.lower() in ["ws", "wss"] or port < 1 or port > 65535:
            raise ValueError(f"Invalid protocol or port: {proto}, {port}\nFormat: [WS, WSS]://[Server]:[1-65535]")

        WS.start(proto, ip, str(port), loginHandler)
