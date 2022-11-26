from WS import ws
from datetime import datetime, timedelta
from js import document, console
from pyodide.ffi import create_proxy


class func:
    def addEvent(id: str, func, action="click", isClass=False):
        proxy = create_proxy(func)

        if isClass:
            id.addEventListener(action, proxy)
            return None

        document.getElementById(id).addEventListener(action, proxy)

    def connectionError():
        element = document.getElementById(f'page_scripts_body')
        element.innerHTML = f'<div id="page_scripts_body_error" align="center"></div>'

        element = document.getElementById(f'page_scripts_body_error')
        element.innerHTML = f'<h1>WARNING!</h1><p>Connection lost to the server! The server is probably not running!<br>Please refresh the page to try again.</p><br>'


class AP:
    currentPage = "Admin Portal"

    lastUpdate = 0

    def getData(args=None):
        if (datetime.now() - timedelta(seconds=5)).timestamp() > AP.lastUpdate:
            try:
                ws.send(f'admin read /Config.json')
                ws.send(f'admin read /Tokens.json')
                # ws.send(f'admin read /Logs.dmp')
            except ConnectionError:
                func.connectionError()

            AP.lastUpdate = datetime.now().timestamp()

    def page(args=None, sub=None):
        element = document.getElementById(f'{AP.currentPage}')
        element.innerHTML += f'<div id="{AP.currentPage}_page" align="center"></div>'

        element = document.getElementById(f'{AP.currentPage}_nav')

        try:
            data = ws.msgDict()
        except ConnectionError:
            func.connectionError()
            return None

        if data == {}:
            element.innerHTML += f'<h2>Unauthorized!</h2>'
