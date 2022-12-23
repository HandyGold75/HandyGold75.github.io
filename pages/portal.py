import mod.ws as ws
import mod.func as func
import subs.portal_sheets as ps
from rsa import encrypt
from js import document, window, console


class glb:
    allSubs = {"Admin": ps.main, "Asset Manager": ps.main, "License Manager": ps.main}
    allInvokes = {"Admin": ps.invoke.AP, "Asset Manager": ps.invoke.AM, "License Manager": ps.invoke.LM}

    loggedIn = False


def pagePortal(args=None, page=None):
    element = document.getElementById(f'page_portal_body')
    element.innerHTML = f''

    if page in glb.allSubs:
        window.localStorage.setItem("page_portal", page)

    elif not args is None and args.target.id.split("_")[-1] in glb.allSubs:
        window.localStorage.setItem("page_portal", args.target.id.split("_")[-1])

    else:
        return None

    element.innerHTML = f'<div id="SubPage" align="left"></div>'
    document.title = f'HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}'

    element = document.getElementById(f'nav_title')
    element.innerHTML = f'<h1>HandyGold75 - {window.localStorage.getItem("page_index")} - {window.localStorage.getItem("page_portal")}</h1>'

    glb.allSubs[window.localStorage.getItem("page_portal")]()


def main():
    ws.start()

    element = document.getElementById(f'page')
    element.innerHTML = f'<div id="page_portal" align="left"></div>'

    element = document.getElementById("page_portal")
    element.innerHTML += f'<div id="page_portal_buttons" align="left"></div>'
    element.innerHTML += f'<div id="page_portal_body" align="left"></div>'

    element = document.getElementById(f'page_portal_buttons')

    for page in glb.allSubs:
        element.innerHTML += f'<button id="page_portal_{page}" type="button" disabled>{page}</button>'

    def login(args):
        if args.key != "Enter":
            return None

        if checkLogin() is True:
            return None

        element = document.getElementById("page_portal_body_login_usr")
        usr = element.value

        element = document.getElementById("page_portal_body_login_psw")
        psw = element.value

        crypt = str(encrypt(usr.encode() + psw.encode(), ps.glb.pk))

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

            element = document.getElementById(f'page_portal_body_login_usr')
            element.disabled = False

            element = document.getElementById(f'page_portal_body_login_psw')
            element.disabled = False

            return None

        elif msg == f'<LOGIN_TOKEN_SUCCESS>':
            glb.loggedIn = True

        elif msg.startswith(f'<LOGIN_SUCCESS> '):
            glb.loggedIn = True
            window.localStorage.setItem("token", f'{msg.split("<LOGIN_SUCCESS> ")[1]}')

        elif msg == " ":
            glb.loggedIn = True

        if glb.loggedIn:
            element = document.getElementById(f'page')
            element.outerHTML = element.outerHTML

            from index import pageIndex
            pageIndex(page=window.localStorage.getItem("page_index"))

            return True

        if window.localStorage.getItem("token") != "":
            element = document.getElementById(f'page_portal_body_login_usr')
            element.disabled = True

            element = document.getElementById(f'page_portal_body_login_psw')
            element.disabled = True

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
        element = document.getElementById("page_portal_body")
        element.innerHTML += f'<h1>Login</h1>'
        element.innerHTML += f'<form id="page_portal_body_login" onsubmit="return false"></form>'
        element.innerHTML += f'<div id="page_portal_body_buttons" align="center"></div>'

        element = document.getElementById("page_portal_body_login")
        element.innerHTML += f'<div id="page_portal_body_login_txt" align="center"></div>'
        element.innerHTML += f'<div id="page_portal_body_login_inp" align="center"></div>'

        element = document.getElementById("page_portal_body_login_txt")
        element.innerHTML += f'<p>Username</p>'
        element.innerHTML += f'<p>Password</p>'

        element = document.getElementById("page_portal_body_login_inp")
        element.innerHTML += f'<input id="page_portal_body_login_usr"></input>'
        element.innerHTML += f'<input id="page_portal_body_login_psw" type="password"></input>'

        func.addEvent(f'page', checkLogin, f'mouseover')
        func.addEvent(f'page_portal_body_login_usr', login, f'keyup')
        func.addEvent(f'page_portal_body_login_psw', login, f'keyup')

        return None

    for page in glb.allSubs:
        element = document.getElementById(f'page_portal_body')
        element.innerHTML = f'<div id="page_portal_body_logout" align="center"></div>'

        element = document.getElementById(f'page_portal_body_logout')
        element.innerHTML += f'<button id="page_portal_body_logout_submit" type="button">Logout</button>'

        func.addEvent(f'page_portal_{page}', pagePortal)
        func.addEvent(f'page_portal_{page}', glb.allInvokes[page], f'mousedown')
        func.addEvent(f'page_portal_body_logout_submit', logout)

        element = document.getElementById(f'page_portal_{page}')
        element.disabled = False
