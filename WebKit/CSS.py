from json import load
from os import path as osPath

from js import document  # type: ignore
from pyodide.ffi import create_proxy  # type: ignore


class glb:
    onHoverStyles = {}
    onClickStyles = {}
    onFocusStyles = {}

    with open(f"{osPath.split(__file__)[0]}/map.json", "r", encoding="UTF-8") as fileR:
        styleMap = load(fileR)["StyleCSS"]

    def expandStyle(style):
        if style is None or not style.split(" %% ")[0] in glb.styleMap:
            return style

        subStyleMerged = ""
        styleTmp = style.split(" %% ")
        for styleKey in styleTmp:
            if not styleKey in glb.styleMap:
                continue

            for subStyle in glb.styleMap[styleKey].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in style:
                    continue
                subStyleMerged += f"{subStyleKey}:{subStyleValue}; "

            style = style.replace(styleKey, "")

        return f'{subStyleMerged}{style.split(" %% ")[-1]}'

    def onEvents(id: str, style: str, events: tuple, onStyleMap: str):
        def mouseover(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_mouseover" in glb.onHoverStyles:
                    el = el.parentElement
                    continue

                break

            for prop in glb.onHoverStyles[f"{el.id}_mouseover"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseout(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_mouseout" in glb.onHoverStyles:
                    el = el.parentElement
                    continue

                break

            if document.getElementById(el.id).tagName != "BUTTON" and document.activeElement == args.target:
                return None

            for prop in glb.onHoverStyles[f"{el.id}_mouseout"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mousedown(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_mousedown" in glb.onClickStyles:
                    el = el.parentElement
                    continue

                break

            for prop in glb.onClickStyles[f"{el.id}_mousedown"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def mouseup(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_mouseup" in glb.onClickStyles:
                    el = el.parentElement
                    continue

                break

            for prop in glb.onClickStyles[f"{el.id}_mouseup"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def focusin(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_focusin" in glb.onFocusStyles:
                    el = el.parentElement
                    continue

                break

            for prop in glb.onFocusStyles[f"{el.id}_focusin"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        def focusout(args=None):
            el = args.target
            for i in range(0, 3):
                if el is None or not f"{el.id}_focusout" in glb.onFocusStyles:
                    el = el.parentElement
                    continue

                break

            for prop in glb.onFocusStyles[f"{el.id}_focusout"]:
                setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

        el = document.getElementById(id)
        onStyleMap[f"{id}_{events[0]}"] = []
        onStyleMap[f"{id}_{events[1]}"] = []

        for prop in glb.expandStyle(style).split(";")[:-1]:
            styleKey = prop.split(": ")[0].replace(" ", "")

            try:
                getattr(el.style, styleKey)
            except AttributeError:
                continue

            if styleKey == "transition":
                el.style.transition = f'{prop.split(": ")[1]}'
                continue

            onStyleMap[f"{id}_{events[0]}"].append(f'{styleKey}: {prop.split(": ")[1]}')
            onStyleMap[f"{id}_{events[1]}"].append(f"{styleKey}: {getattr(el.style, styleKey)}")

        el.addEventListener(str(events[0]), create_proxy({"mouseover": mouseover, "mousedown": mousedown, "focusin": focusin}[events[0]]))
        el.addEventListener(str(events[1]), create_proxy({"mouseout": mouseout, "mouseup": mouseup, "focusout": focusout}[events[1]]))


def getAttribute(id: str, key: str):
    return getattr(document.getElementById(id), str(key))


def getAttributes(id: str, keys: tuple):
    values = []
    for key in keys:
        values.append(getattr(document.getElementById(id), str(key)))

    return values


def getStyle(id: str, key: str):
    return getattr(document.getElementById(id).style, str(key))


def getStyles(id: str, keys: tuple):
    values = []
    for key in keys:
        values.append(getattr(document.getElementById(id).style, str(key)))

    return values


def setAttribute(id: str, key: str, value: str):
    setattr(document.getElementById(id), str(key), str(value))


def setAttributes(id: str, pairs: tuple):
    for key, value in pairs:
        setattr(document.getElementById(id), str(key), str(value))


def setStyle(id: str, key: str, value: str):
    setattr(document.getElementById(id).style, str(key), str(value))


def setStyles(id: str, pairs: tuple):
    if type(pairs) is str:
        style = glb.expandStyle(pairs)

        for stylePair in glb.expandStyle(style).split("; "):
            if stylePair == "":
                continue
            setattr(document.getElementById(id).style, str(stylePair.split(": ")[0]), str(stylePair.split(": ")[1]))

        return None

    for key, value in pairs:
        setattr(document.getElementById(id).style, str(key), str(value))


def onHover(id: str, style: str):
    glb.onEvents(id, glb.expandStyle(style), ("mouseover", "mouseout"), glb.onHoverStyles)


def onClick(id: str, style: str):
    glb.onEvents(id, glb.expandStyle(style), ("mousedown", "mouseup"), glb.onClickStyles)


def onFocus(id: str, style: str):
    glb.onEvents(id, glb.expandStyle(style), ("focusin", "focusout"), glb.onFocusStyles)


def onHoverClick(id: str, styleHover: str, styleClick: str):
    glb.onEvents(id, glb.expandStyle(styleHover), ("mouseover", "mouseout"), glb.onHoverStyles)
    glb.onEvents(id, glb.expandStyle(styleClick), ("mousedown", "mouseup"), glb.onClickStyles)


def onHoverFocus(id: str, styleHover: str, styleFocus: str):
    glb.onEvents(id, glb.expandStyle(styleHover), ("mouseover", "mouseout"), glb.onHoverStyles)
    glb.onEvents(id, glb.expandStyle(styleFocus), ("focusin", "focusout"), glb.onFocusStyles)
