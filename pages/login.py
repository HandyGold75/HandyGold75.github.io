from WebKit import HTML, CSS, JS, WS
from datetime import datetime, timedelta
from rsa import encrypt


class glb:
    lastLogin = 0


def setup():
    JS.cache(f'page_index', f'Login')


def setupConnection():
    def logout(args=None):
        if not JS.popup(f'confirm', f'Log off?'):
            return None

        WS.send(f'logout')

        JS.cache("token", "")
        WS.loggedIn = False

        JS.f5()

    def loginSucces():
        msg = WS.msg()

        JS.cache("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

        loginTokenSucces()

    def loginTokenSucces():
        def getData():
            from pages.portal import glb as pGlb, pagePortal, main as pMain

            access = WS.dict()["access"]
            for invoke in reversed(pGlb.allInvokes):
                if not pGlb.allCommands[invoke] in access:
                    continue

                pGlb.allInvokes[invoke]()

            if JS.cache("page_portal") != "":
                pGlb.allInvokes[JS.cache("page_portal")]()

                JS.cache(f'page_index', f'Portal')
                JS.setTitle(f'HandyGold75 - {JS.cache("page_index")} - {JS.cache("page_portal")}')
                HTML.setRaw(f'nav_title', f'HandyGold75 - {JS.cache("page_index")} - {JS.cache("page_portal")}')

                JS.afterDelay(pMain, max(250, (250 * len(access)) - 250))
                JS.afterDelay(pagePortal, max(500, 250 * len(access)))

        def loadingTxt():
            el = HTML.get(f'page_login_loadingTxt')
            if el is None:
                return None

            if el.innerHTML.endswith(". . . "):
                el.innerHTML = el.innerHTML.replace(". . . ", "")

            el.innerHTML += ". "
            JS.afterDelay(loadingTxt, 500)

        WS.onMsg("{\"access\":", getData, oneTime=True)
        WS.send(f'access')
        WS.loggedIn = True

        JS.clearEvents(f'footer_Login')
        HTML.setRaw(f'footer_Login', f'Logout')

        JS.addEvent(f'footer_Login', logout)
        CSS.onHoverClick(f'footer_Login', f'buttonHover %% background: #66F;', f'buttonClick %% background: #66F;')

        if JS.cache("page_index") != "Login":
            return None

        content = HTML.add(f'h1', _nest=f'Logged in succesfully', _style=f'headerBig')
        if JS.cache("page_portal") != "":
            content += HTML.add(f'h1', _nest=f'Loading last used page', _id=f'page_login_loadingTxt', _style=f'headerMedium')

        HTML.set(f'div', f'page_login', _nest=f'{content}', _id=f'page_login_summary', _style=f'divNormal')
        JS.aSync(loadingTxt)

    def loginFail():
        JS.popup(f'alert', f'Log in failed!')

    def loginTokenFail():
        JS.cache("token", "")
        WS.loggedIn = False

        HTML.enable(f'page_login_body_login_usr', True)
        HTML.enable(f'page_login_body_login_psw', True)

    if JS.cache("server") == "" or not "://" in JS.cache("server") or not JS.cache("server").count(":") == 2:
        raise ValueError(f'Invalid server: {JS.cache("server")}\nFormat: [WS, WSS]://[Server]:[1-65535]')

    proto = JS.cache("server").split("://")[0]
    ip = JS.cache("server").split("://")[-1].split(":")[0]
    port = int(JS.cache("server").split("://")[-1].split(":")[-1])

    if not proto.lower() in ["ws", "wss"] or port < 1 or port > 65535:
        raise ValueError(f'Invalid protocol or port: {proto}, {port}\nFormat: [WS, WSS]://[Server]:[1-65535]')

    if JS.cache("token") != "":
        WS.onMsg(f'<LOGIN_TOKEN_SUCCESS>', loginTokenSucces, oneTime=True)
        WS.onMsg(f'<LOGIN_TOKEN_FAIL>', loginTokenFail, oneTime=True)

    WS.onMsg(f'<LOGIN_SUCCESS>', loginSucces, oneTime=True)
    WS.onMsg(f'<LOGIN_FAIL>', loginFail)

    WS.start(proto, ip, port)


def main(args=None):
    def login(args):
        def sendLogin():
            if WS.ws.readyState > 1:
                JS.popup("alert", "Failed to connect to server")
                return None

            if WS.ws.readyState == 0 or WS.PK is None:
                JS.afterDelay(sendLogin, 50)
                return None

            crypt = str(encrypt(HTML.get("page_login_body_login_usr").value.encode() + "<SPLIT>".encode() + HTML.get("page_login_body_login_psw").value.encode(), WS.PK))
            WS.send(f'<LOGIN> {crypt}')

        if WS.loggedIn:
            return None

        if hasattr(args, "key") and args.key != "Enter":
            return None

        if (datetime.now() - timedelta(seconds=1)).timestamp() < glb.lastLogin:
            return None

        glb.lastLogin = datetime.now().timestamp()

        srv = HTML.get("page_login_body_login_srv").value

        if not srv == JS.cache("server") or WS.ws == None or WS.ws.readyState > 1:
            JS.cache("server", srv)

            try:
                setupConnection()
            except ValueError as err:
                JS.popup("alert", str(err))
                return None

        JS.aSync(sendLogin)

    def signinRemember(args):
        if args.target.checked:
            CSS.set(f'page_login_body_options_auto', f'checked', f'')
            JS.cache(f'signin', f'Remember')

            return None

        JS.cache(f'signin', f'None')

    def signinAuto(args):
        if args.target.checked:
            CSS.set(f'page_login_body_options_remember', f'checked', f'')
            JS.cache(f'signin', f'Auto')

            return None

        JS.cache(f'signin', f'None')

    HTML.set(f'div', f'page', _id=f'page_login', _align=f'center', _style="flex")

    if WS.loggedIn:
        return None

    setup()
    setupConnection()

    HTML.add(f'div', f'page_login', _id=f'page_login_body', _align=f'center', _style="width: 100%;")

    HTML.add(f'h1', f'page_login_body', _nest=f'Login', _style=f'headerBig')
    HTML.add(f'form', f'page_login_body', _id=f'page_login_body_login', _style=f'width: 75%; display: flex; margin: 0 auto 20px auto; max-width: 750px;', _custom=f'onsubmit="return false"')
    HTML.add(f'div', f'page_login_body', _id=f'page_login_body_options', _align=f'center', _style=f'divNormal %% flex %% width: 50%; max-width: 500px;')

    txt = HTML.add(f'p', _nest=f'Server', _style=f'margin: 3px; padding: 2px;')
    txt += HTML.add(f'p', _nest=f'Username', _style=f'margin: 3px; padding: 2px;')
    txt += HTML.add(f'p', _nest=f'Password', _style=f'margin: 3px; padding: 2px;')
    inp = HTML.add(f'input', _id=f'page_login_body_login_srv', _type=f'url', _style=f'inputMedium %% width: 90%;', _custom=f'placeholder="Server" pattern="(WSS||WS)://.+:[0-9]+" value="{JS.cache("server")}"')
    inp += HTML.add(f'input', _id=f'page_login_body_login_usr', _type=f'email', _style=f'inputMedium %% width: 90%;', _custom=f'placeholder="Username"')
    inp += HTML.add(f'input', _id=f'page_login_body_login_psw', _type=f'password', _style=f'inputMedium %% width: 90%;', _custom=f'placeholder="Password"')
    HTML.add(f'div', f'page_login_body_login', _nest=txt, _id=f'page_login_body_login_txt', _align=f'center', _style=f'width: 25%;')
    HTML.add(f'div', f'page_login_body_login', _nest=inp, _id=f'page_login_body_login_inp', _align=f'center', _style=f'width: 75%;')

    inp1 = HTML.add(f'input', _id=f'page_login_body_options_remember', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;')
    inp2 = HTML.add(f'input', _id=f'page_login_body_options_auto', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;')
    if JS.cache(f'signin') == f'Remember':
        inp1 = HTML.add(f'input', _id=f'page_login_body_options_remember', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;', _custom=f'checked')
    if JS.cache(f'signin') == f'Auto':
        inp2 = HTML.add(f'input', _id=f'page_login_body_options_auto', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;', _custom=f'checked')
    HTML.add(f'div', f'page_login_body_options', _nest=f'{inp1}{inp2}', _style=f'width: 5%; margin: auto;')

    txt1 = HTML.add(f'p', _nest=f'Remember Sign in', _align=f'left', _style=f'width: 100%; margin: auto auto;')
    txt2 = HTML.add(f'p', _nest=f'Auto Sign in', _align=f'left', _style=f'width: 100%; margin: auto auto;')
    HTML.add(f'div', f'page_login_body_options', _nest=f'{txt1}{txt2}', _style=f'width: 47.5%; margin: auto;')

    btn = HTML.add(f'button', _nest=f'Login', _id=f'page_login_body_options_submit', _type=f'button', _style=f'buttonMedium %% width: 50%; height: 50%;')
    HTML.add(f'div', f'page_login_body_options', _nest=f'{btn}', _style=f'width: 47.5%; margin: auto;')

    JS.addEvent(f'page_login_body_login_srv', login, f'keyup')
    JS.addEvent(f'page_login_body_login_usr', login, f'keyup')
    JS.addEvent(f'page_login_body_login_psw', login, f'keyup')

    CSS.onHoverFocus(f'page_login_body_login_srv', f'inputHover', f'inputFocus')
    CSS.onHoverFocus(f'page_login_body_login_usr', f'inputHover', f'inputFocus')
    CSS.onHoverFocus(f'page_login_body_login_psw', f'inputHover', f'inputFocus')
    CSS.onHoverClick(f'page_login_body_options_submit', f'buttonHover', f'buttonClick')

    JS.addEvent(f'page_login_body_options_remember', signinRemember)
    JS.addEvent(f'page_login_body_options_auto', signinAuto)
    JS.addEvent(f'page_login_body_options_submit', login)
