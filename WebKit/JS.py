from js import document, window, eval, setTimeout, setInterval, console
from pyodide.ffi import create_proxy, create_once_callable  # type: ignore


class glb:
    callOnResize = {}

    def onResize(element=None):
        for function in glb.callOnResize:
            if callable(glb.callOnResize[function]):
                glb.callOnResize[function]()

    window.onresize = onResize


def log(msg: str):
    console.log(msg)


def f5():
    window.location.reload()


def getWindow():
    return window


def getVP():
    return (window.innerHeight, window.innerWidth)


def afterDelay(function: object, args: tuple = (), kwargs: dict = {}, delay: int = 1):
    setTimeout(create_once_callable(lambda: function(*args, **kwargs)), delay)


def aSync(function: object, args: tuple = (), kwargs: dict = {}):
    setTimeout(create_once_callable(lambda: function(*args, **kwargs)), 1)


def atInterval(function: object, args: tuple = (), kwargs: dict = {}, delay: int = 1):
    setInterval(create_proxy(lambda: function(*args, **kwargs)), delay)


def jsEval(com: str):
    return eval(str(com))


def popup(type: str, txt: str):
    return {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}[type](txt)


def clearCache():
    window.localStorage.clear()
    window.location.reload()


def cache(key: str, value: any = None):
    if value is None:
        return window.localStorage.getItem(key)

    window.localStorage.setItem(key, value)


def addEvent(id: str, function: object, args: tuple = (), kwargs: dict = {}, action: str = "click", includeElement: bool = False):
    if includeElement:
        func = lambda element=None: function(element, *args, **kwargs)
    else:
        func = lambda element=None: function(*args, **kwargs)

    document.getElementById(id).addEventListener(action, create_proxy(func))


def addEventRaw(element: str, function: object, args: tuple = (), kwargs: dict = {}, action: str = "click", includeElement: bool = False):
    if includeElement:
        func = lambda element=None: function(element, *args, **kwargs)
    else:
        func = lambda element=None: function(*args, **kwargs)

    element.addEventListener(action, create_proxy(func))


def clearEvents(id):
    el = document.getElementById(id)
    el.outerHTML = el.outerHTML


def clearEventsRaw(element):
    element.outerHTML = element.outerHTML


def setTitle(title: str):
    document.title = title


def onResize(name: str, function: object, args: tuple = (), kwargs: dict = {}):
    if function is None:
        if name in glb.callOnResize:
            glb.callOnResize.pop(name)
        return None

    glb.callOnResize[name] = lambda: function(*args, **kwargs)
    glb.onResize()
