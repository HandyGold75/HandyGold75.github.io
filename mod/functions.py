import mod.CSS as CSS
from js import document, window, console
from pyodide.ffi import create_proxy # type: ignore


class glb:
    popupTypes = {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}
    links_py_columns = 4


def log(msg: str = f''):
    console.log(msg)


def clearEvents(id):
    el = document.getElementById(id)
    el.outerHTML = el.outerHTML


def addEvent(id: str, func, action: str = "click", isClass: bool = False):
    if isClass:
        id.addEventListener(action, create_proxy(func))
        return None

    document.getElementById(id).addEventListener(action, create_proxy(func))


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


def getWindow():
    return window


def getVP():
    return window.innerHeight, window.innerWidth


def onResize(args=None):
    if window.innerWidth < 450:
        glb.links_py_columns = 3

        CSS.setStyle(f'body', f'padding', f'0px')
        CSS.setStyle(f'body', f'fontSize', f'75%')
        CSS.setStyle(f'nav_logo', f'max-width', f'85px')

        if window.localStorage.getItem(f'page_index') == f'Links':
            from index import pageIndex
            pageIndex(page=window.localStorage.getItem(f'page_index'))

        return None

    elif window.innerWidth < 700:
        glb.links_py_columns = 4

        CSS.setStyle(f'body', f'padding', f'0px 20px')
        CSS.setStyle(f'body', f'fontSize', f'75%')
        CSS.setStyle(f'nav_logo', f'max-width', f'85px')

        if window.localStorage.getItem(f'page_index') == f'Links':
            from index import pageIndex
            pageIndex(page=window.localStorage.getItem(f'page_index'))

        return None

    elif window.innerWidth < 950:
        glb.links_py_columns = 5

        CSS.setStyle(f'body', f'padding', f'0px 20px')
        CSS.setStyle(f'body', f'fontSize', f'100%')
        CSS.setStyle(f'nav_logo', f'max-width', f'100px')

        if window.localStorage.getItem(f'page_index') == f'Links':
            from index import pageIndex
            pageIndex(page=window.localStorage.getItem(f'page_index'))

        return None

    else:
        glb.links_py_columns = 6

        CSS.setStyle(f'body', f'padding', f'0px 20px')
        CSS.setStyle(f'body', f'fontSize', f'100%')
        CSS.setStyle(f'nav_logo', f'max-width', f'100px')

        if window.localStorage.getItem(f'page_index') == f'Links':
            from index import pageIndex
            pageIndex(page=window.localStorage.getItem(f'page_index'))