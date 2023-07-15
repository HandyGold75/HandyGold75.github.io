from js import document, window, eval, setTimeout, setInterval, console
from pyodide.ffi import create_proxy, create_once_callable # type: ignore

log = console.log
f5 = window.location.reload
getWindow = lambda: window
getVP = lambda: window.innerHeight, window.innerWidth
afterDelay = lambda func, delay: setTimeout(create_once_callable(func), delay)
aSync = lambda func: setTimeout(create_once_callable(func), 0)
atInterval = lambda func, delay: setInterval(create_proxy(func), delay)
jsEval = lambda com: eval(str(com))
popup = lambda type, txt: {"alert": window.alert, "prompt": window.prompt, "confirm": window.confirm}[type](txt)
clearCache = lambda: (window.localStorage.clear(), window.location.reload())
cache = lambda key, value=None: (window.localStorage.setItem(key, value) if not value is None else None, window.localStorage.getItem(key))[-1]
addEvent = lambda id, func, action="click", isClass=False: id.addEventListener(action, create_proxy(func)) if isClass else document.getElementById(id).addEventListener(action, create_proxy(func))


def clearEvents(id):
    el = document.getElementById(id)
    el.outerHTML = el.outerHTML


def setTitle(title: str):
    document.title = title


def onResize(args=None):
    def update(size: int):
        sizeMap = {"0": ("0px", "50%", "85px"), "1": ("0px 20px", "75%", "85px"), "max": ("0px 20px", "100%", "100px")}

        if size >= 2:
            size = "max"

        if not str(size) in sizeMap:
            return None

        document.getElementById("body").style.padding = sizeMap[str(size)][0]
        document.getElementById("body").style.fontSize = sizeMap[str(size)][1]
        document.getElementById("nav_logo").style.maxWidth = sizeMap[str(size)][2]

    def update_links(size: int):
        sizeMap = {"0": 3, "1": 4, "2": 5, "max": 6}

        if size >= 3:
            size = "max"

        if not str(size) in sizeMap:
            return None

        window.localStorage.setItem("page_links_colums", sizeMap[str(size)])
        from index import pageIndex
        pageIndex("noResize", page=window.localStorage.getItem("page_index"))

    def update_sonos(size: int):
        sizeMap = {"0": ("0%", "100%", "40px", "35px", "none"), "1": ("50%", "50%", "20px", "45px", ""), "max": ("75%", "25%", "0px", "55px", "")}

        if size >= 2:
            size = "max"

        if not str(size) in sizeMap:
            return None

        el = document.getElementById("SubPage_page_art")
        if not el is None:
            el.style.width = sizeMap[str(size)][0]
            el.style.display = sizeMap[str(size)][4]

        el = document.getElementById("SubPage_page_que")
        if not el is None:
            el.style.width = sizeMap[str(size)][1]
            el.style.marginBottom = sizeMap[str(size)][2]

        el = document.getElementById("SubPage_page_queAdd")
        if not el is None:
            el.style.minHeight = sizeMap[str(size)][3]

    page = window.localStorage.getItem("page_index")
    if page == "Portal":
        page = window.localStorage.getItem("page_portal")

    fmap = {"Links": update_links, "Sonos": update_sonos}

    size = 99
    if window.innerWidth < 450:
        size = 0
    elif window.innerWidth < 700:
        size = 1
    elif window.innerWidth < 950:
        size = 2

    update(size)
    if page in fmap:
        fmap[page](size)
