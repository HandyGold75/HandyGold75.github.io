from js import document
from pyodide.ffi import create_proxy


def addEvent(id: str, func, action="click", isClass=False):
    proxy = create_proxy(func)

    if isClass:
        id.addEventListener(action, proxy)
        return None

    document.getElementById(id).addEventListener(action, proxy)


def connectionError():
    element = document.getElementById(f'page_portal_body')
    element.innerHTML = f'<div id="page_portal_body_error" align="center"></div>'

    element = document.getElementById(f'page_portal_body_error')
    element.innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! The server is probably not running!<br>Please refresh the page to try again.</p><br>'