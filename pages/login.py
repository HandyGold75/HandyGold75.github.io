import mod.HTML as HTML
import mod.CSS as CSS
import mod.ws as ws
import mod.functions as f
from datetime import datetime, timedelta
from rsa import encrypt


class glb:
    lastLogin = 0


def setup():
    def logout(args=None):
        if not f.popup(f'confirm', f'Log off?'):
            return None

        ws.send(f'logout')

        f.cache("token", "")
        f.glb.loggedIn = False

        f.f5()

    def loginSucces():
        msg = ws.msg()

        f.cache("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

        loginTokenSucces()

    def loginTokenSucces():
        ws.send(f'access')
        f.glb.loggedIn = True

        if f.cache("page_index") != "Login":
            return None

        f.clearEvents(f'footer_Login')

        content = HTML.add(f'h1', _nest=f'Logged in succesfully', _style=f'headerBig')
        HTML.set(f'div', f'page_login', _nest=f'{content}', _id=f'page_login_summary', _style=f'divNormal')

        HTML.setRaw(f'footer_Login', f'Logout')

        f.addEvent(f'footer_Login', logout)
        CSS.onHover(f'footer_Login', f'buttonHover %% background: #66F;')
        CSS.onClick(f'footer_Login', f'buttonClick %% background: #66F;')

    def loginFail():
        f.popup(f'alert', f'Log in failed!')

    def loginTokenFail():
        f.cache("token", "")
        f.glb.loggedIn = False

        HTML.enable(f'page_login_body_login_usr', True)
        HTML.enable(f'page_login_body_login_psw', True)

    f.cache(f'page_index', f'Login')
    f.cache(f'page_portal', f'')

    ws.start("wss", "wss.HandyGold75.com", "6900")

    if f.cache("token") != "":
        ws.onMsg(f'<LOGIN>', f'<LOGIN_TOKEN> {f.cache("token")}')
        ws.onMsg(f'<LOGIN_TOKEN_SUCCESS>', loginTokenSucces)
        ws.onMsg(f'<LOGIN_TOKEN_FAIL>', loginTokenFail)

    ws.onMsg(f'<LOGIN_SUCCESS>', loginSucces)
    ws.onMsg(f'<LOGIN_FAIL>', loginFail)


def main(args=None):
    HTML.set(f'div', f'page', _id=f'page_login', _align=f'center', _style="flex")

    if f.glb.loggedIn:
        return None

    setup()

    HTML.add(f'div', f'page_login', _id=f'page_login_body', _align=f'center', _style="width: 100%;")

    def login(args):
        if f.glb.loggedIn:
            return None

        if args.key != "Enter":
            return None

        if (datetime.now() - timedelta(seconds=1)).timestamp() < glb.lastLogin:
            return None

        glb.lastLogin = datetime.now().timestamp()

        crypt = str(encrypt(HTML.get("page_login_body_login_usr").value.encode() + "<SPLIT>".encode() + HTML.get("page_login_body_login_psw").value.encode(), f.glb.pk))

        ws.send(f'<LOGIN> {crypt}')

    def signinRemember(args):
        if args.target.checked:
            CSS.set(f'page_login_body_options_auto', f'checked', f'')
            f.cache(f'signin', f'Remember')

            return None

        f.cache(f'signin', f'None')

    def signinAuto(args):
        if args.target.checked:
            CSS.set(f'page_login_body_options_remember', f'checked', f'')
            f.cache(f'signin', f'Auto')

            return None

        f.cache(f'signin', f'None')

    HTML.add(f'h1', f'page_login_body', _nest=f'Login', _style=f'headerBig')
    HTML.add(f'form', f'page_login_body', _id=f'page_login_body_login', _style=f'width: 75%; display: flex; margin: 0 auto 20px auto;', _custom=f'onsubmit="return false"')
    HTML.add(f'div', f'page_login_body', _id=f'page_login_body_options', _align=f'center', _style=f'divNormal %% flex %% width: 50%;')

    txt = HTML.add(f'p', _nest=f'Username', _style=f'margin: 3px; padding: 2px;') + HTML.add(f'p', _nest=f'Password', _style=f'margin: 3px; padding: 2px;')
    inp = HTML.add(f'input', _id=f'page_login_body_login_usr', _style=f'inputMedium %% width: 90%;') + HTML.add(f'input', _id=f'page_login_body_login_psw', _type=f'password', _style=f'inputMedium %% width: 90%;')

    HTML.add(f'div', f'page_login_body_login', _nest=txt, _id=f'page_login_body_login_txt', _align=f'center', _style=f'width: 25%;')
    HTML.add(f'div', f'page_login_body_login', _nest=inp, _id=f'page_login_body_login_inp', _align=f'center', _style=f'width: 75%;')

    HTML.add(f'div', f'page_login_body_options', _style=f'width: 35%; margin: auto;')

    inp1 = HTML.add(f'input', _id=f'page_login_body_options_remember', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;')
    inp2 = HTML.add(f'input', _id=f'page_login_body_options_auto', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;')

    if f.cache(f'signin') == f'Remember':
        inp1 = HTML.add(f'input', _id=f'page_login_body_options_remember', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;', _custom=f'checked')
    if f.cache(f'signin') == f'Auto':
        inp2 = HTML.add(f'input', _id=f'page_login_body_options_auto', _type=f'checkbox', _align=f'right', _style=f'inputMedium %% width: 100%; margin: auto auto; padding: 5px;', _custom=f'checked')

    HTML.add(f'div', f'page_login_body_options', _nest=f'{inp1}{inp2}', _style=f'width: 5%; margin: auto;')

    txt1 = HTML.add(f'p', _nest=f'Remember Sign in', _align=f'left', _style=f'width: 100%; margin: auto auto;')
    txt2 = HTML.add(f'p', _nest=f'Auto Sign in', _align=f'left', _style=f'width: 100%; margin: auto auto;')
    HTML.add(f'div', f'page_login_body_options', _nest=f'{txt1}{txt2}', _style=f'width: 60%; margin: auto;')

    f.addEvent(f'page_login_body_login_usr', login, f'keyup')
    f.addEvent(f'page_login_body_login_psw', login, f'keyup')

    CSS.onHover(f'page_login_body_login_usr', f'inputHover')
    CSS.onHover(f'page_login_body_login_psw', f'inputClick')

    f.addEvent(f'page_login_body_options_remember', signinRemember)
    f.addEvent(f'page_login_body_options_auto', signinAuto)
