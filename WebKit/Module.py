from js import document, setTimeout, window  # type: ignore
from pyodide.ffi import create_once_callable, create_proxy  # type: ignore

from WebKit import CSS, HTML, JS, WS


class buttons:
    def __init__(self):
        self._onEventMap = {}

    def _makeButton(self, id: str, text: str, theme: str = "dark", size: str = "medium", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        # if id in self._onEventMap:
        #     raise ValueError(f"ID {id} already exists in memory!")
        self._onEventMap[id] = {"function": onClick, "args": args, "kwargs": kwargs}

        return HTML.genElement("button", nest=text, id=id, classes=" ".join((theme, size)) + ("active" if active else ""), type="button", style=buttonStyle, **buttonKwargs)

    def _makeImgButton(self, id: str, src: str, alt: str = "", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}, size: str = "medium"):
        # if id in self._onEventMap:
        #     raise ValueError(f"ID {id} already exists in memory!")
        self._onEventMap[id] = {"function": onClick, "args": args, "kwargs": kwargs}

        img = HTML.genElement("img", id=f"{id}_img", custom=f'src="{src}" alt="{alt}"')
        return HTML.genElement("button", nest=img, id=id, classes=f'imgBtn {size}{" active" if active else ""}', type="button", style=buttonStyle, **buttonKwargs)

    def small(self, id: str, text: str, theme: str = "dark", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "small", active, buttonStyle, buttonKwargs, onClick, args, kwargs)

    def medium(self, id: str, text: str, theme: str = "dark", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "medium", active, buttonStyle, buttonKwargs, onClick, args, kwargs)

    def large(self, id: str, text: str, theme: str = "dark", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeButton(id, text, theme, "large", active, buttonStyle, buttonKwargs, onClick, args, kwargs)

    def imgSmall(self, id: str, src: str, alt: str = "", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, active, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnSmall")

    def imgMedium(self, id: str, src: str, alt: str = "", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, active, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnMedium")

    def imgLarge(self, id: str, src: str, alt: str = "", active: bool = False, buttonStyle: str = "", buttonKwargs: dict = {}, onClick: object = lambda: None, args: tuple = (), kwargs: dict = {}):
        return self._makeImgButton(id, src, alt, active, buttonStyle, buttonKwargs, onClick, args, kwargs, "imgBtnLarge")

    def applyEvents(self):
        for id in dict(self._onEventMap):
            JS.aSync(JS.addEvent, args=(id,), kwargs=self._onEventMap[id])
            self._onEventMap.pop(id)
