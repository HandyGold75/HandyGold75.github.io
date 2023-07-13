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


def expandStyle(style):
    if style is None or not " %% " in style:
        return style

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

    return f'{subStyleMerged}{style.split(" %% ")[-1]}'


def getLink(href: str, nest: str = "", style: str = ""):
    return f'<a href="{href}" target="_blank" style="color: #44F; {expandStyle(style)}">{nest}</a>'


def add(tag: str, targetId: str = None, nest: str = "", prepend: str = "", id: str = "", clas: str = "", type: str = "", align: str = "", style: str = "", custom: str = ""):
    args = {"id": id, "class": clas, "type": type, "align": align, "style": expandStyle(style)}
    additionsStr = ""
    for arg in args:
        if args[arg] == "":
            continue

        additionsStr += f' {arg}="{args[arg]}"'

    additionsStr += f' {custom}'

    htmlStr = f'{prepend}<{tag}{additionsStr}>{nest}'
    if not tag in ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]:
        htmlStr += f'</{tag}>'

    if not targetId is None:
        document.getElementById(targetId).innerHTML += htmlStr

    return htmlStr


def set(tag: str, targetId: str = None, nest: str = "", prepend: str = "", id: str = "", clas: str = "", type: str = "", align: str = "", style: str = "", custom: str = ""):
    htmlStr = add(tag, None, nest, prepend, id, clas, type, align, style, custom)

    if not targetId is None:
        document.getElementById(targetId).innerHTML = htmlStr

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
