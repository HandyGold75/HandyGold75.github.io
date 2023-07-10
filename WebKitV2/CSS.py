from js import document
from pyodide.ffi import create_proxy # type: ignore
from json import load
from os import path as osPath 

with open(f'{osPath.split(__file__)[0]}/styleMap.json', "r", encoding="UTF-8") as fileR:
    styleMap = load(fileR)["CSS"]
    
onHoverStyles = {}
onClickStyles = {}
onFocusStyles = {}

get = lambda id, key: getattr(document.getElementById(id), key)
set = lambda id, key, value: setattr(document.getElementById(id), key, value)
getStyle = lambda id, key: getattr(document.getElementById(id).style, key)
setStyle = lambda id, key, value: setattr(document.getElementById(id).style, key, value)
onHoverClick = lambda id, styleHover, styleClick: (onHover(id, styleHover), onClick(id, styleClick))
onHoverFocus = lambda id, styleHover, styleClick: (onHover(id, styleHover), onFocus(id, styleClick))


def sets(id: str, keyValue: tuple):
    for key, value in keyValue:
        setattr(document.getElementById(id), key, value)


def setStyles(id: str, keyValue: tuple):
    for key, value in keyValue:
        setattr(document.getElementById(id).style, key, value)


def onHover(id: str, style: str):
    def mouseover(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_mouseover' in onHoverStyles:
                el = el.parentElement
                continue
            break

        for prop in onHoverStyles[f'{el.id}_mouseover']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    def mouseout(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_mouseout' in onHoverStyles:
                el = el.parentElement
                continue
            break

        if document.getElementById(el.id).tagName != "BUTTON" and document.activeElement == args.target:
            return None

        for prop in onHoverStyles[f'{el.id}_mouseout']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    onHoverStyles[f'{id}_mouseover'] = []
    onHoverStyles[f'{id}_mouseout'] = []

    if style.split(" %% ")[0] in styleMap:
        subStyleMerged = ""
        styleTmp = style.split(" %% ")

        for styleKey in styleTmp:
            if not styleKey in styleMap:
                continue

            for subStyle in styleMap[styleKey].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            style = style.replace(styleKey, "")

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(";")[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        try:
            getattr(el.style, styleKey)
        except AttributeError:
            continue

        if styleKey == "transition":
            el.style.transition = f'{prop.split(": ")[1]}'
            continue

        onHoverStyles[f'{id}_mouseout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        onHoverStyles[f'{id}_mouseover'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener("mouseover", create_proxy(mouseover))
    el.addEventListener("mouseout", create_proxy(mouseout))


def onClick(id: str, style: str):
    def mousedown(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_mousedown' in onClickStyles:
                el = el.parentElement
                continue
            break

        for prop in onClickStyles[f'{el.id}_mousedown']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    def mouseup(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_mouseup' in onClickStyles:
                el = el.parentElement
                continue
            break

        for prop in onClickStyles[f'{el.id}_mouseup']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    onClickStyles[f'{id}_mousedown'] = []
    onClickStyles[f'{id}_mouseup'] = []

    if style.split(" %% ")[0] in styleMap:
        subStyleMerged = ""
        styleTmp = style.split(" %% ")

        for styleKey in styleTmp:
            if not styleKey in styleMap:
                continue

            for subStyle in styleMap[styleKey].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            style = style.replace(styleKey, "")

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(";")[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        try:
            getattr(el.style, styleKey)
        except AttributeError:
            continue

        if styleKey == "transition":
            el.style.transition = prop.split(": ")[1]
            continue

        onClickStyles[f'{id}_mouseup'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        onClickStyles[f'{id}_mousedown'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener("mousedown", create_proxy(mousedown))
    el.addEventListener("mouseup", create_proxy(mouseup))


def onFocus(id: str, style: str):
    def focusin(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_focusin' in onFocusStyles:
                el = el.parentElement
                continue
            break

        for prop in onFocusStyles[f'{el.id}_focusin']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    def focusout(args=None):
        el = args.target
        for i in range(0, 3):
            if el is None or not f'{el.id}_focusout' in onFocusStyles:
                el = el.parentElement
                continue
            break

        for prop in onFocusStyles[f'{el.id}_focusout']:
            setattr(document.getElementById(el.id).style, prop.split(": ")[0], prop.split(": ")[1])

    el = document.getElementById(id)

    onFocusStyles[f'{id}_focusin'] = []
    onFocusStyles[f'{id}_focusout'] = []

    if style.split(" %% ")[0] in styleMap:
        subStyleMerged = ""
        styleTmp = style.split(" %% ")

        for styleKey in styleTmp:
            if not styleKey in styleMap:
                continue

            for subStyle in styleMap[styleKey].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            style = style.replace(styleKey, "")

        style = f'{subStyleMerged}{style.split(" %% ")[-1]}'

    for prop in style.split(";")[:-1]:
        styleKey = prop.split(": ")[0].replace(" ", "")

        try:
            getattr(el.style, styleKey)
        except AttributeError:
            continue

        if styleKey == "transition":
            el.style.transition = prop.split(": ")[1]
            continue

        onFocusStyles[f'{id}_focusout'].append(f'{styleKey}: {getattr(el.style, styleKey)}')
        onFocusStyles[f'{id}_focusin'].append(f'{styleKey}: {prop.split(": ")[1]}')

    el.addEventListener("focusin", create_proxy(focusin))
    el.addEventListener("focusout", create_proxy(focusout))
