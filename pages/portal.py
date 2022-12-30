import mod.ws as ws
import mod.func as func
import subs.portal_sheets as ps
import subs.portal_trees as pt
from datetime import datetime, timedelta
from rsa import encrypt
from js import document, window, console


class glb:
    allSubs = {"Admin": ps.main, "Monitor": pt.main, "Asset Manager": ps.main, "License Manager": ps.main}
    allInvokes = {"Admin": ps.invoke.AP, "Monitor": pt.invoke.MO, "Asset Manager": ps.invoke.AM, "License Manager": ps.invoke.LM}

    lastLogin = 0
    loggedIn = False


def setup():
    ws.start()

    el = document.getElementById(f'page')
    el.innerHTML = f'<div id="page_portal" align="left" style="display: flex;"></div>'


def pagePortal(args=None, page=None):
    el = document.getElementById(f'page_portal_body')
    el.innerHTML = f''

    if page in glb.allSubs:
        window.localStorage.setItem("page_portal", page)

    elif not args is None and args.target.id.split("_")[-1] in glb.allSubs:
        window.localStorage.setItem("page_portal", args.target.id.split("_")[-1])

    else:
        return None

    el.innerHTML = f'<div id="SubPage" align="left"></div>'
    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}'

    el = document.getElementById(f'nav_title')
    el.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}</h1>'

    glb.allSubs[window.localStorage.getItem("page_portal")]()


def main():
    setup()

    el = document.getElementById("page_portal")
    el.innerHTML += f'<div id="page_portal_buttons" align="left" style="width: 10%; min-width: 60px; font-size: 75%; border-right: 10px solid #111; margin-right: 10px;"></div>'
    el.innerHTML += f'<div id="page_portal_body" align="left" style="width: 90%;"></div>'

    el = document.getElementById(f'page_portal_buttons')

    for page in glb.allSubs:
        el.innerHTML += f'<button id="page_portal_{page}" type="button" style="width: 90%; word-wrap: break-word;" disabled>{page}</button>'

    def login(args):
        if checkLogin() is True:
            return None

        if args.key != "Enter":
            return None

        if (datetime.now() - timedelta(seconds=3)).timestamp() < glb.lastLogin:
            console.log("TIMEOUT")
            return None

        glb.lastLogin = datetime.now().timestamp()

        crypt = str(encrypt(document.getElementById("page_portal_body_login_usr").value.encode() + document.getElementById("page_portal_body_login_psw").value.encode(), ps.glb.pk))

        try:
            ws.send(f'<LOGIN> {crypt}')
        except ConnectionError:
            func.connectionError()

    def checkLogin(args=None):
        if window.localStorage.getItem("page_index") != "Portal":
            return None

        try:
            msg = ws.msg()
        except ConnectionError:
            func.connectionError()
            return None

        if msg == f'<LOGIN_TOKEN_FAIL>':
            window.localStorage.setItem("token", "")
            glb.loggedIn = False

            document.getElementById(f'page_portal_body_login_usr').disabled = False
            document.getElementById(f'page_portal_body_login_psw').disabled = False

            return None

        elif msg == f'<LOGIN_TOKEN_SUCCESS>':
            glb.loggedIn = True

        elif msg.startswith(f'<LOGIN_SUCCESS> '):
            glb.loggedIn = True
            window.localStorage.setItem("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

        elif msg == " ":
            glb.loggedIn = True

        if glb.loggedIn:
            el = document.getElementById(f'page')
            el.outerHTML = el.outerHTML

            from index import pageIndex
            pageIndex(page=window.localStorage.getItem("page_index"))

            return True

        if window.localStorage.getItem("token") != "":
            document.getElementById(f'page_portal_body_login_usr').disabled = True
            document.getElementById(f'page_portal_body_login_psw').disabled = True

            try:
                ws.send(f'<LOGIN_TOKEN> {window.localStorage.getItem("token")}')
            except ConnectionError:
                func.connectionError()

    def logout(args=None):
        try:
            ws.send(f'logout')
        except ConnectionError:
            func.connectionError()

        window.localStorage.setItem("token", "")
        glb.loggedIn = False

        window.location.reload()

    if not glb.loggedIn:
        el = document.getElementById("page_portal_body")
        el.innerHTML += f'<h1 style="text-align: center;">Login</h1>'
        el.innerHTML += f'<form id="page_portal_body_login" style="width: 75%; display: flex; margin: 0 auto 20px auto;" onsubmit="return false"></form>'
        el.innerHTML += f'<div id="page_portal_body_buttons" align="center"></div>'

        el = document.getElementById("page_portal_body_login")
        el.innerHTML += f'<div id="page_portal_body_login_txt" align="center" style="width: 25%;"></div>'
        el.innerHTML += f'<div id="page_portal_body_login_inp" align="center" style="width: 75%;"></div>'

        el = document.getElementById("page_portal_body_login_txt")
        el.innerHTML += f'<p style="margin: 3px; padding: 2px;">Username</p>'
        el.innerHTML += f'<p style="margin: 3px; padding: 2px;">Password</p>'

        el = document.getElementById("page_portal_body_login_inp")
        el.innerHTML += f'<input id="page_portal_body_login_usr" style="width: 90%;"></input>'
        el.innerHTML += f'<input id="page_portal_body_login_psw" type="password" style="width: 90%;"></input>'

        func.addEvent(f'page', checkLogin, f'mouseover')
        func.addEvent(f'page_portal_body_login_usr', login, f'keyup')
        func.addEvent(f'page_portal_body_login_psw', login, f'keyup')

        return None

    for invoke in reversed(glb.allInvokes):
        glb.allInvokes[invoke]()

    for page in glb.allSubs:
        el = document.getElementById(f'page_portal_body')
        el.innerHTML = f'<div id="page_portal_body_logout" align="center" style="height: 100%;"></div>'

        el = document.getElementById(f'page_portal_body_logout')
        el.innerHTML += f'<button id="page_portal_body_logout_submit" type="button" style="position: relative; top: 45%;">Logout</button>'

        func.addEvent(f'page_portal_{page}', pagePortal)
        func.addEvent(f'page_portal_{page}', glb.allInvokes[page], f'mousedown')
        func.addEvent(f'page_portal_body_logout_submit', logout)

        document.getElementById(f'page_portal_{page}').disabled = False
