from js import document, setTimeout, window  # type: ignore
from pyodide.ffi import create_once_callable, create_proxy  # type: ignore

from WebKit import CSS, HTML, JS, WS


class buttons:
    def __init__(self):
        self._onEventMap = {}

    def _makeButton(self, id: str, text: str, theme: str = "dark", size: str = "medium", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        # if id in self._onEventMap:
        #     raise ValueError(f"ID {id} already exists in memory!")
        self._onEventMap[id] = {"function": onClick, "args": args, "kwargs": kwargs}

        return HTML.genElement("button", nest=text, id=id, classes=" ".join((theme, size)), type="button", style=buttonStyle, **buttonKwargs)

    def _makeImgButton(self, id: str, src: str, alt: str = "", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}, size: str = "medium"):
        # if id in self._onEventMap:
        #     raise ValueError(f"ID {id} already exists in memory!")
        self._onEventMap[id] = {"function": onClick, "args": args, "kwargs": kwargs}

        # flyoutImg = HTML.genElement("img", id="portalPage_button_showHideImg", style="width: 100%;", custom='src="docs/assets/Portal/Hide-H.svg" alt="Fold"')
        # flyoutBtn = HTML.genElement("button", id="portalPage_button_showHide", nest=flyoutImg, style="buttonImg")
        # flyoutDivs = HTML.genElement("div", nest=flyoutBtn, id="portalPage_button_showHideDiv", align="center", style="width: 100%; margin: 0px auto 5px 0px;")

        img = HTML.genElement("img", id=f"{id}_img", custom=f'src="{src}" alt="{alt}"')
        return HTML.genElement("button", nest=img, id=id, classes=f"imgBtn {size}", type="button", style=buttonStyle, **buttonKwargs)

    def small(self, id: str, text: str, theme: str = "dark", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "small", buttonStyle, buttonKwargs, onClick, args, kwargs)

    def medium(self, id: str, text: str, theme: str = "dark", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "medium", buttonStyle, buttonKwargs, onClick, args, kwargs)

    def large(self, id: str, text: str, theme: str = "dark", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "large", buttonStyle, buttonKwargs, onClick, args, kwargs)

    def imgSmall(self, id: str, src: str, alt: str = "", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnSmall")

    def imgMedium(self, id: str, src: str, alt: str = "", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnMedium")

    def imgLarge(self, id: str, src: str, alt: str = "", buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnLarge")

    def applyEvents(self):
        for id in dict(self._onEventMap):
            JS.aSync(JS.addEvent, args=(id,), kwargs=self._onEventMap[id])
            self._onEventMap.pop(id)
