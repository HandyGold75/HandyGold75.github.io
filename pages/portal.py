import mod.HTML as HTML
import mod.ws as ws
import mod.functions as f
import subs.portal_sheets as ps
import subs.portal_trees as pt
from datetime import datetime, timedelta
from rsa import encrypt


class glb:
    allSubs = {"Admin": ps.main, "Monitor": pt.main, "Asset Manager": ps.main, "License Manager": ps.main}
    allInvokes = {"Admin": ps.invoke.AP, "Monitor": pt.invoke.MO, "Asset Manager": ps.invoke.AM, "License Manager": ps.invoke.LM}

    lastLogin = 0
    loggedIn = False


def setup():
    ws.start("wss", "wss.HandyGold75.ga", "6900")
    HTML.set(f'div', f'page', _id=f'page_portal', _align=f'left', _style="flex")


def pagePortal(args=None, page=None):
    HTML.clear(f'page_portal_body')

    if page in glb.allSubs:
        f.cache("page_portal", page)

    elif not args is None and args.target.id.split("_")[-1] in glb.allSubs:
        f.cache("page_portal", args.target.id.split("_")[-1])

    else:
        return None

    f.setTitle(f'HandyGold75 - {f.cache("page_index")} - {f.cache("page_portal")}')

    HTML.set(f'div', f'page_portal_body', _id=f'SubPage', _align=f'left')
    HTML.set(f'h1', f'nav_title', _nest=f'HandyGold75 - {f.cache("page_index")} - {f.cache("page_portal")}')

    glb.allSubs[f.cache("page_portal")]()


def main():
    setup()

    HTML.add(f'div', f'page_portal', _id=f'page_portal_buttons', _align=f'left', _style="width: 10%; min-width: 60px; font-size: 75%; border-right: 10px solid #111; margin-right: 10px;")
    HTML.add(f'div', f'page_portal', _id=f'page_portal_body', _align=f'left', _style="width: 90%;")

    for page in glb.allSubs:
        HTML.add(f'button', f'page_portal_buttons', _nest=f'{page}', _id=f'page_portal_{page}', _type=f'button', _align=f'left', _style=f'buttonMedium %% width: 90%;', _custom=f'disabled')

    def login(args):
        if checkLogin() is True:
            return None

        if args.key != "Enter":
            return None

        if (datetime.now() - timedelta(seconds=3)).timestamp() < glb.lastLogin:
            return None

        glb.lastLogin = datetime.now().timestamp()

        crypt = str(encrypt(HTML.get("page_portal_body_login_usr").value.encode() + HTML.get("page_portal_body_login_psw").value.encode(), ps.glb.pk))

        try:
            ws.send(f'<LOGIN> {crypt}')
        except ConnectionError:
            f.connectionError()

    def checkLogin(args=None):
        if f.cache("page_index") != "Portal":
            return None

        try:
            msg = ws.msg()
        except ConnectionError:
            f.connectionError()
            return None

        if msg == f'<LOGIN_TOKEN_FAIL>':
            f.cache("token", "")
            glb.loggedIn = False

            HTML.enable(f'page_portal_body_login_usr', True)
            HTML.enable(f'page_portal_body_login_psw', True)

            return None

        elif msg == f'<LOGIN_TOKEN_SUCCESS>':
            glb.loggedIn = True

        elif msg.startswith(f'<LOGIN_SUCCESS> '):
            glb.loggedIn = True
            f.cache("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

        elif msg == " ":
            glb.loggedIn = True

        if glb.loggedIn:
            f.clearEvents(f'page')

            from index import pageIndex
            pageIndex(page=f.cache("page_index"))

            return True

        if f.cache("token") != "":
            HTML.enable(f'page_portal_body_login_usr', False)
            HTML.enable(f'page_portal_body_login_psw', False)

            try:
                ws.send(f'<LOGIN_TOKEN> {f.cache("token")}')
            except ConnectionError:
                f.connectionError()

    def logout(args=None):
        try:
            ws.send(f'logout')
        except ConnectionError:
            f.connectionError()

        f.cache("token", "")
        glb.loggedIn = False

        f.f5()

    if not glb.loggedIn:
        HTML.add(f'h1', f'page_portal_body', _nest=f'Login', _style=f'text-align: center;')
        HTML.add(f'form', f'page_portal_body', _id=f'page_portal_body_login', _style=f'width: 75%; display: flex; margin: 0 auto 20px auto;', _custom=f'onsubmit="return false"')
        HTML.add(f'div', f'page_portal_body', _id=f'page_portal_body_buttons', _align=f'center')

        txt = HTML.add(f'p', _nest=f'Username', _style=f'margin: 3px; padding: 2px;') + HTML.add(f'p', _nest=f'Password', _style=f'margin: 3px; padding: 2px;')
        inp = HTML.add(f'input', _id=f'page_portal_body_login_usr', _style=f'width: 90%;') + HTML.add(f'input', _id=f'page_portal_body_login_psw', _type=f'password', _style=f'width: 90%;')

        HTML.add(f'div', f'page_portal_body_login', _nest=txt, _id=f'page_portal_body_login_txt', _align=f'center', _style=f'width: 25%;')
        HTML.add(f'div', f'page_portal_body_login', _nest=inp, _id=f'page_portal_body_login_inp', _align=f'center', _style=f'width: 75%;')

        f.addEvent(f'page', checkLogin, f'mouseover')
        f.addEvent(f'page_portal_body_login_usr', login, f'keyup')
        f.addEvent(f'page_portal_body_login_psw', login, f'keyup')

        return None

    for invoke in reversed(glb.allInvokes):
        glb.allInvokes[invoke]()

    for page in glb.allSubs:
        HTML.set(f'div', f'page_portal_body', _id=f'page_portal_body_logout', _align=f'center', _style=f'height: 100%;')
        HTML.add(f'button', f'page_portal_body_logout', _nest=f'Logout', _id=f'page_portal_body_logout_submit', _type=f'button', _style=f'position: relative; top: 45%;')

        f.addEvent(f'page_portal_{page}', pagePortal)
        f.addEvent(f'page_portal_{page}', glb.allInvokes[page], f'mousedown')
        f.addEvent(f'page_portal_body_logout_submit', logout)

        HTML.enable(f'page_portal_{page}', True)
