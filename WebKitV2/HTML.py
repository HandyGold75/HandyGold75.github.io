from js import document
from WebKit import CSS
from json import load
from os import path as osPath 


class bridgedCSS:
    onHoverStyles = lambda: CSS.onHoverStyles
    onClickStyles = lambda: CSS.onClickStyles
    onFocusStyles = lambda: CSS.onFocusStyles

with open(f'{osPath.split(__file__)[0]}/styleMap.json', "r", encoding="UTF-8") as fileR:
    styleMap = load(fileR)["HTML"]
    
disabledStyles = {}

get = lambda id, isClass=False: list(document.getElementsByClassName(id)) if isClass else document.getElementById(id)
move = lambda sourceId, targetId: document.getElementById(targetId).appendChild(document.getElementById(sourceId))


def getLink(href: str, _nest: str = None, _style: str = None):
    if not _style is None and _style.split(" %% ")[0] in styleMap:
        subStyleMerged = ""
        _styleTmp = _style.split(" %% ")

        for style in _styleTmp:
            if not style in styleMap:
                continue

            for subStyle in styleMap[style].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in _style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            _style = _style.replace(style, "")

        _style = f'{subStyleMerged}{_style.split(" %% ")[-1]}'

    style = "color: #44F;"

    if not _style is None:
        style = f'{style} {_style}'

    htmlStr = f'<a href="{href}" target="_blank" style="{style}">'

    if not _nest is None:
        htmlStr += f'{_nest}'

    htmlStr += "</a>"

    return htmlStr


def add(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
    if not _style is None and _style.split(" %% ")[0] in styleMap:
        subStyleMerged = ""
        _styleTmp = _style.split(" %% ")

        for style in _styleTmp:
            if not style in styleMap:
                continue

            for subStyle in styleMap[style].split(";"):
                subStyleKey, subStyleValue = subStyle.split(":")
                subStyleKey = subStyleKey.replace(" ", "")

                if subStyleKey in subStyleMerged or subStyleKey in _style:
                    continue

                subStyleMerged += f'{subStyleKey}:{subStyleValue}; '

            _style = _style.replace(style, "")

        _style = f'{subStyleMerged}{_style.split(" %% ")[-1]}'

    args = {"id": _id, "class": _class, "type": _type, "align": _align, "style": _style}
    additionsStr = ""

    for arg in args:
        if args[arg] is None:
            continue

        additionsStr += f' {arg}="{args[arg]}"'

    if not _custom is None:
        additionsStr += f' {_custom}'

    htmlStr = f'<{type}{additionsStr}>'

    if not _nest is None:
        htmlStr += _nest

    if not type in ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]:
        htmlStr += f'</{type}>'

    if not _prepend is None:
        htmlStr = f'{_prepend}{htmlStr}'

    if not id is None:
        document.getElementById(id).innerHTML += htmlStr

    return htmlStr


def set(type: str, id: str = None, _nest: str = None, _prepend: str = None, _id: str = None, _class: str = None, _type: str = None, _align: str = None, _style: str = None, _custom: str = None):
    htmlStr = add(type, None, _nest, _prepend, _id, _class, _type, _align, _style, _custom)

    if not id is None:
        document.getElementById(id).innerHTML = htmlStr

    return htmlStr


def addRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML += HTML


def setRaw(id: str, HTML: str):
    document.getElementById(id).innerHTML = HTML


def copy(sourceId: str, targetId: str):
    el = document.getElementById(sourceId).cloneNode(True)
    el.id = f'{el.id}_NEW'
    document.getElementById(targetId).appendChild(el)


def enable(id: str, state: bool = True):
    el = document.getElementById(id)

    if el.disabled is not state:
        return None

    onStyles = {
        "onHover": {
            "style": bridgedCSS.onHoverStyles(),
            "actions": ["mouseover", "mouseout"]
        },
        "onClick": {
            "style": bridgedCSS.onClickStyles(),
            "actions": ["mousedown", "mouseup"]
        },
        "onFocus": {
            "style": bridgedCSS.onFocusStyles(),
            "actions": ["focusout", "focusin"]
        }
    }

    el.disabled = not state

    if state:
        if not id in disabledStyles:
            return None

        for onStyle in onStyles:
            for action in onStyles[onStyle]["actions"]:
                if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                    continue

                if not f'{id}_{action}' in disabledStyles[id]["events"]:
                    continue

                itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])

                for i, item in enumerate(itemListTmp):
                    if item.startswith("color: ") and "color" in disabledStyles[id]["events"][f'{id}_{action}']:
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = disabledStyles[id]["events"][f'{id}_{action}']["color"]

                    elif item.startswith("background: ") and "background" in disabledStyles[id]["events"][f'{id}_{action}']:
                        onStyles[onStyle]["style"][f'{id}_{action}'][i] = disabledStyles[id]["events"][f'{id}_{action}']["background"]

        el.style.color = disabledStyles[id]["color"]
        el.style.background = disabledStyles[id]["background"]

        disabledStyles.pop(id)

        return None

    disabledStyles[id] = {"color": el.style.color, "background": el.style.background, "events": {}}

    for onStyle in onStyles:
        for action in onStyles[onStyle]["actions"]:
            if not f'{id}_{action}' in onStyles[onStyle]["style"]:
                continue

            disabledStyles[id]["events"][f'{id}_{action}'] = {}
            itemListTmp = list(onStyles[onStyle]["style"][f'{id}_{action}'])

            for i, item in enumerate(itemListTmp):

                if item.startswith("color: "):
                    disabledStyles[id]["events"][f'{id}_{action}']["color"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = "color: #88B"

                elif item.startswith("background: "):
                    disabledStyles[id]["events"][f'{id}_{action}']["background"] = onStyles[onStyle]["style"][f'{id}_{action}'][i]
                    onStyles[onStyle]["style"][f'{id}_{action}'][i] = "background: #222"

    el.style.color = "#88B"
    el.style.background = "#222"


def clear(id: str, isClass: bool = False):
    if isClass:
        for item in document.getElementsByClassName(id):
            item.innerHTML = ""
            return None

    document.getElementById(id).innerHTML = ""


def remove(id: str, isClass: bool = False):
    if isClass:
        for item in document.getElementsByClassName(id):
            item.remove()

        return None

    document.getElementById(id).remove()
