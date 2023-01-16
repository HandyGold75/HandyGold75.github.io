from js import document, window, console
from pyodide.ffi import create_proxy


class glb:
    popupTypes = {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}


def log(msg):
    console.log(msg)


def clearEvents(id):
    el = document.getElementById(id)
    el.outerHTML = el.outerHTML


def addEvent(id: str, func, action: str = "click", isClass: bool = False):
    proxy = create_proxy(func)

    if isClass:
        id.addEventListener(action, proxy)
        return None

    document.getElementById(id).addEventListener(action, proxy)


def cache(key: str, value: any = None):
    if not value is None:
        window.localStorage.setItem(key, value)

    return window.localStorage.getItem(key)


def f5():
    window.location.reload()


def connectionError():
    document.getElementById(f'page_portal_body').innerHTML = f'<div id="page_portal_body_error" align="center"></div>'
    document.getElementById(f'page_portal_body_error').innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! The server is probably not running!<br>Please refresh the page to try again.</p><br>'


def popup(type: str, text: str):
    if type in glb.popupTypes:
        return glb.popupTypes[type](text)


def setTitle(title: str):
    document.title = title
